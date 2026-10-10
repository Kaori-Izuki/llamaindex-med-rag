"""Local HuggingFace LLM query engine and source-node serialization."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any

import torch
from llama_index.core import PromptTemplate, Settings
from llama_index.llms.huggingface import HuggingFaceLLM
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import (
    DEVICE,
    LLM_CONTEXT_WINDOW,
    LLM_MAX_NEW_TOKENS,
    LLM_MODEL_DIR,
    LLM_MODEL_ID,
    LLM_TEMPERATURE,
    SYSTEM_PROMPT,
)


QA_TEMPLATE = PromptTemplate(
    """以下是检索到的医学文献上下文：
----------------
{context_str}
----------------

问题：{query_str}

请只依据上面的上下文回答。回答中引用来源文件名；若证据不足，请明确说明，不要猜测。不要复述问题或提示词。
回答："""
)


@lru_cache(maxsize=1)
def create_llm() -> HuggingFaceLLM:
    model_path = LLM_MODEL_DIR if (LLM_MODEL_DIR / "config.json").exists() else LLM_MODEL_ID
    dtype = torch.float32 if DEVICE == "cpu" else torch.float16
    torch.manual_seed(42)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(str(model_path), torch_dtype=dtype)
    if DEVICE != "cpu":
        model.to(DEVICE)

    def completion_to_prompt(prompt: str) -> str:
        if getattr(tokenizer, "chat_template", None):
            return tokenizer.apply_chat_template(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                tokenize=False,
                add_generation_prompt=True,
            )
        return f"{SYSTEM_PROMPT}\n\n{prompt}"

    stop_ids = [tokenizer.eos_token_id] if tokenizer.eos_token_id is not None else []
    im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
    if isinstance(im_end_id, int) and im_end_id >= 0:
        stop_ids.append(im_end_id)
    llm = HuggingFaceLLM(
        context_window=LLM_CONTEXT_WINDOW,
        max_new_tokens=LLM_MAX_NEW_TOKENS,
        generate_kwargs={
            "temperature": LLM_TEMPERATURE,
            "do_sample": True,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "no_repeat_ngram_size": 3,
        },
        tokenizer_name=str(model_path),
        model_name=str(model_path),
        model=model,
        tokenizer=tokenizer,
        device_map="auto" if DEVICE != "cpu" else "cpu",
        stopping_ids=stop_ids,
        completion_to_prompt=completion_to_prompt,
    )
    Settings.llm = llm
    return llm


def create_query_engine(index: Any, similarity_top_k: int = 3) -> Any:
    llm = create_llm()
    return index.as_query_engine(
        llm=llm,
        similarity_top_k=similarity_top_k,
        text_qa_template=QA_TEMPLATE,
        response_mode="compact",
    )


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _source_node_payload(source: Any, max_chars: int = 1600) -> dict[str, Any]:
    node = source.node
    content = node.get_content()
    return {
        "source_file": node.metadata.get("file_name") or node.metadata.get("source_file", ""),
        "metadata": {str(k): _json_safe(v) for k, v in node.metadata.items()},
        "score": round(float(source.score), 6) if source.score is not None else None,
        "text_snippet": content[:max_chars],
        "text_length": len(content),
        "page": node.metadata.get("page_label") or node.metadata.get("page_number"),
    }


def run_query(index: Any, question: str, similarity_top_k: int = 3) -> dict[str, Any]:
    query_engine = create_query_engine(index, similarity_top_k=similarity_top_k)
    start = perf_counter()
    response = query_engine.query(question)
    elapsed = perf_counter() - start
    answer = getattr(response, "response", str(response)).strip()
    source_nodes = [_source_node_payload(item) for item in getattr(response, "source_nodes", [])]
    return {
        "question": question,
        "answer": answer,
        "source_nodes_count": len(source_nodes),
        "source_nodes": source_nodes,
        "runtime_seconds": round(elapsed, 3),
        "parameters": {
            "similarity_top_k": similarity_top_k,
            "temperature": LLM_TEMPERATURE,
            "max_new_tokens": LLM_MAX_NEW_TOKENS,
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "llm_model": LLM_MODEL_ID,
        },
    }


def source_files(result: dict[str, Any]) -> list[str]:
    return list(dict.fromkeys(node.get("source_file", "") for node in result.get("source_nodes", []) if node.get("source_file")))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
