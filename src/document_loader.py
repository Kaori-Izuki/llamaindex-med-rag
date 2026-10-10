"""Load arbitrary local PDF/Markdown/TXT literature from data/raw."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from llama_index.core import Document, SimpleDirectoryReader

from .config import METADATA_PATH, PROCESSED_DIR, RAW_DIR, ROOT_DIR


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def clean_text(text: str) -> str:
    """Normalize extracted text without changing the source document."""

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00ad", "").replace("\u200b", "")
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalised_stem(value: str) -> str:
    """Match metadata rows even when a downloaded file has a repeated suffix."""

    name = Path(str(value).strip()).name
    while True:
        lowered = name.lower()
        for suffix in (".pdf", ".md", ".txt"):
            if lowered.endswith(suffix):
                name = name[: -len(suffix)]
                break
        else:
            break
    return name.strip().lower()


def _metadata_by_stem() -> dict[str, dict[str, str]]:
    if not METADATA_PATH.exists():
        return {}
    with METADATA_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        for key in (row.get("local_stem", ""), row.get("local_markdown", ""), row.get("local_pdf", "")):
            normalised = _normalised_stem(key)
            if normalised:
                mapping[normalised] = {str(k): str(v or "").strip() for k, v in row.items()}
    return mapping


def _display_title(path: Path) -> str:
    name = path.name
    while name.lower().endswith((".pdf", ".md", ".txt")):
        name = name.rsplit(".", 1)[0]
    return re.sub(r"[_-]+", " ", name).strip() or path.name


def input_files() -> list[Path]:
    """Return the active literature inputs.

    data/raw is the user-facing source directory. Legacy processed files are
    used only when raw contains no supported literature files, which keeps old
    projects readable without mixing stale documents with new raw inputs.
    """

    raw_files = (
        sorted(
            path
            for path in RAW_DIR.rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
            and "failed_pdf_downloads" not in path.parts
        )
        if RAW_DIR.exists()
        else []
    )
    if raw_files:
        return raw_files

    processed_files = (
        sorted(
            path
            for path in PROCESSED_DIR.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if PROCESSED_DIR.exists()
        else []
    )
    return processed_files


def source_inventory() -> list[dict[str, object]]:
    """Return stable fingerprints used to invalidate cached indexes."""

    inventory: list[dict[str, object]] = []
    for path in input_files():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        inventory.append(
            {
                "source_file": path.relative_to(ROOT_DIR).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": digest,
            }
        )
    return inventory


def source_signature() -> str:
    return json.dumps(source_inventory(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_documents() -> list[Document]:
    files = input_files()
    if not files:
        raise FileNotFoundError("没有发现 data/raw 中的 PDF/TXT/Markdown 文献。")
    metadata_map = _metadata_by_stem()

    def file_metadata(path: str) -> dict[str, str]:
        file_path = Path(path)
        row = metadata_map.get(_normalised_stem(file_path.name), {})
        relative = file_path.relative_to(ROOT_DIR).as_posix()
        return {
            "source_file": relative,
            "file_name": file_path.name,
            "file_type": file_path.suffix.lower().lstrip("."),
            "title": row.get("title") or _display_title(file_path),
            "authors": row.get("authors", ""),
            "year": row.get("year", ""),
            "journal": row.get("journal", ""),
            "doi": row.get("doi", ""),
            "pmid": row.get("pmid", ""),
            "pmcid": row.get("pmcid", ""),
            "source_url": row.get("source_url", ""),
        }

    reader = SimpleDirectoryReader(
        input_files=files,
        filename_as_id=True,
        file_metadata=file_metadata,
        recursive=False,
    )
    loaded = reader.load_data(show_progress=False)
    documents: list[Document] = []
    for item in loaded:
        text = clean_text(item.get_content())
        if not text:
            continue
        documents.append(Document(text=text, metadata=dict(item.metadata), id_=item.id_))
    if not documents:
        raise ValueError("文献加载后文本为空。请检查 PDF 是否为扫描图片，或先进行 OCR。")
    return documents


def document_stats(documents: list[Document]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for doc in documents:
        source_file = str(doc.metadata.get("source_file", ""))
        item = grouped.setdefault(
            source_file,
            {
                "source_file": source_file,
                "file_name": doc.metadata.get("file_name", ""),
                "file_type": doc.metadata.get("file_type", ""),
                "title": doc.metadata.get("title", ""),
                "characters": 0,
                "words_approx": 0,
                "pmid": doc.metadata.get("pmid", ""),
                "pmcid": doc.metadata.get("pmcid", ""),
            },
        )
        item["characters"] = int(item["characters"]) + len(doc.get_content())
        item["words_approx"] = int(item["words_approx"]) + len(doc.get_content().split())
    return list(grouped.values())
