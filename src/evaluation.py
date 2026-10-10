"""Small, transparent parameter-comparison experiment."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from .build_index import build_or_load_index
from .config import CHUNK_OVERLAP, CHUNK_SIZE, COMPARISON_QUESTION, RESULTS_DIR, SIMILARITY_TOP_K
from .query_engine import run_query, source_files


EXPECTED_TERMS = [
    "联合",
    "单药",
    "机制",
    "疗效",
    "不良",
    "毒性",
    "PD-1",
    "CTLA-4",
]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}|[\u4e00-\u9fff]{2,}", text.lower()))


def transparent_scores(result: dict[str, Any]) -> dict[str, Any]:
    """Return heuristic screening values, explicitly not clinical metrics."""

    answer = result.get("answer", "")
    term_coverage = sum(term.lower() in answer.lower() for term in EXPECTED_TERMS) / len(EXPECTED_TERMS)
    completeness = round(max(1.0, min(5.0, 1 + 4 * term_coverage)), 2)
    source_text = " ".join(node.get("text_snippet", "") for node in result.get("source_nodes", []))
    answer_tokens = _tokenize(answer)
    source_tokens = _tokenize(source_text)
    consistency_coverage = len(answer_tokens & source_tokens) / max(1, len(answer_tokens))
    consistency = round(max(1.0, min(5.0, 1 + 4 * consistency_coverage)), 2)
    scores = [node.get("score") for node in result.get("source_nodes", []) if isinstance(node.get("score"), (int, float))]
    source_relevance = round(max(1.0, min(5.0, 1 + 4 * (sum(scores) / len(scores) if scores else 0.0))), 2)
    answer_numbers = set(re.findall(r"\d+(?:\.\d+)?%?", answer))
    source_numbers = set(re.findall(r"\d+(?:\.\d+)?%?", source_text))
    unsupported_numbers = sorted(answer_numbers - source_numbers)
    hallucination_risk = "可能存在未在召回片段中核实的数值" if unsupported_numbers else "未发现明显未核实数值；仍需人工复核"
    return {
        "answer_completeness_heuristic_1_5": completeness,
        "source_consistency_heuristic_1_5": consistency,
        "source_relevance_heuristic_1_5": source_relevance,
        "hallucination_screening": hallucination_risk,
        "evaluation_note": "透明启发式筛查，不等同于临床评价或客观金标准；最终结论需人工对照原文。",
    }


def run_parameter_experiments(force_rebuild: bool = False) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for chunk_size in (256, 512, 1024):
        index, manifest = build_or_load_index(chunk_size, CHUNK_OVERLAP, force_rebuild=force_rebuild)
        result = run_query(index, COMPARISON_QUESTION, similarity_top_k=SIMILARITY_TOP_K)
        rows.append(
            {
                "experiment": "chunk_size",
                "value": chunk_size,
                "chunk_size": chunk_size,
                "chunk_overlap": CHUNK_OVERLAP,
                "similarity_top_k": SIMILARITY_TOP_K,
                "response_time_seconds": result["runtime_seconds"],
                "retrieved_nodes": result["source_nodes_count"],
                "source_files": " | ".join(source_files(result)),
                "answer_excerpt": result["answer"].replace("\n", " ")[:700],
                "node_count": manifest.get("node_stats", {}).get("node_count", ""),
                **transparent_scores(result),
            }
        )

    index, manifest = build_or_load_index(CHUNK_SIZE, CHUNK_OVERLAP, force_rebuild=force_rebuild)
    for top_k in (1, 3, 5):
        result = run_query(index, COMPARISON_QUESTION, similarity_top_k=top_k)
        rows.append(
            {
                "experiment": "similarity_top_k",
                "value": top_k,
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "similarity_top_k": top_k,
                "response_time_seconds": result["runtime_seconds"],
                "retrieved_nodes": result["source_nodes_count"],
                "source_files": " | ".join(source_files(result)),
                "answer_excerpt": result["answer"].replace("\n", " ")[:700],
                "node_count": manifest.get("node_stats", {}).get("node_count", ""),
                **transparent_scores(result),
            }
        )
    return rows


def save_comparison(rows: list[dict[str, Any]], path: Path | None = None) -> Path:
    path = path or (RESULTS_DIR / "parameter_comparison.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return path
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path
