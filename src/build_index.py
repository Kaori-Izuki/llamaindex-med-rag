"""Document chunking, HuggingFace embedding, VectorStoreIndex persistence."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median
from typing import Any

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from .config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DEVICE,
    EMBEDDING_MODEL_DIR,
    EMBEDDING_MODEL_ID,
    index_dir,
)
from .document_loader import document_stats, input_files, load_documents, source_signature


def create_embedding() -> HuggingFaceEmbedding:
    model_path = EMBEDDING_MODEL_DIR if (EMBEDDING_MODEL_DIR / "config.json").exists() else EMBEDDING_MODEL_ID
    return HuggingFaceEmbedding(
        model_name=str(model_path),
        cache_folder=str(EMBEDDING_MODEL_DIR.parent / "cache"),
        device=DEVICE,
        normalize=True,
    )


def _manifest_path(persist_dir: Path) -> Path:
    return persist_dir / "index_manifest.json"


def _valid_persisted_index(persist_dir: Path, chunk_size: int, chunk_overlap: int) -> bool:
    required = (persist_dir / "docstore.json", persist_dir / "index_store.json", _manifest_path(persist_dir))
    if not all(path.exists() for path in required):
        return False
    try:
        manifest = json.loads(_manifest_path(persist_dir).read_text(encoding="utf-8"))
        return (
            manifest.get("chunk_size") == chunk_size
            and manifest.get("chunk_overlap") == chunk_overlap
            and manifest.get("embedding_model") == EMBEDDING_MODEL_ID
            and manifest.get("document_count") == len(input_files())
            and manifest.get("source_signature") == source_signature()
        )
    except (OSError, json.JSONDecodeError):
        return False


def _node_stats(nodes: list[Any]) -> dict[str, float | int]:
    lengths = [len(node.get_content()) for node in nodes]
    if not lengths:
        return {"node_count": 0, "min_chars": 0, "max_chars": 0, "mean_chars": 0, "median_chars": 0}
    return {
        "node_count": len(lengths),
        "min_chars": min(lengths),
        "max_chars": max(lengths),
        "mean_chars": round(mean(lengths), 2),
        "median_chars": round(median(lengths), 2),
    }


def build_or_load_index(
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    force_rebuild: bool = False,
) -> tuple[Any, dict[str, Any]]:
    persist_dir = index_dir(chunk_size, chunk_overlap)
    if _valid_persisted_index(persist_dir, chunk_size, chunk_overlap) and not force_rebuild:
        storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
        index = load_index_from_storage(storage_context, embed_model=create_embedding())
        manifest = json.loads(_manifest_path(persist_dir).read_text(encoding="utf-8"))
        manifest["loaded_from_cache"] = True
        return index, manifest

    documents = load_documents()
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = splitter.get_nodes_from_documents(documents, show_progress=True)
    for node in nodes:
        node.metadata["chunk_size"] = str(chunk_size)
        node.metadata["chunk_overlap"] = str(chunk_overlap)
    embedding = create_embedding()
    index = VectorStoreIndex(nodes, embed_model=embedding, show_progress=True)
    persist_dir.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(persist_dir))
    stats = document_stats(documents)
    manifest: dict[str, Any] = {
        "embedding_model": EMBEDDING_MODEL_ID,
        "embedding_model_path": str(EMBEDDING_MODEL_DIR),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "document_count": len(stats),
        "documents": stats,
        "source_signature": source_signature(),
        "node_stats": _node_stats(nodes),
        "loaded_from_cache": False,
    }
    _manifest_path(persist_dir).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return index, manifest
