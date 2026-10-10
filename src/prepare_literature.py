"""Validate and inventory user-supplied literature in data/raw."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from .config import METADATA_PATH, ROOT_DIR, ensure_project_directories
from .document_loader import clean_text, input_files


def read_metadata() -> list[dict[str, str]]:
    """Read optional provenance enrichment; raw filenames remain sufficient."""

    if not METADATA_PATH.exists():
        return []
    with METADATA_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _inspect_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    page_count: int | None = None
    if suffix == ".pdf":
        header = path.read_bytes()[:5]
        if header != b"%PDF-":
            raise ValueError("文件不是有效 PDF（缺少 %PDF- 文件头）")
        reader = PdfReader(str(path))
        page_count = len(reader.pages)
        if page_count <= 0:
            raise ValueError("PDF 没有页面")
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    else:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    text = clean_text(text)
    if not text:
        raise ValueError("提取文本为空；扫描 PDF 需要先 OCR")
    return {
        "source_file": path.relative_to(ROOT_DIR).as_posix(),
        "file_name": path.name,
        "file_type": suffix.lstrip("."),
        "size_bytes": path.stat().st_size,
        "page_count": page_count,
        "characters": len(text),
        "paragraphs": len([line for line in text.splitlines() if line.strip()]),
        "status": "validated",
    }


def prepare_all(force: bool = False) -> list[dict[str, Any]]:
    """Validate every current raw input before indexing.

    ``force`` is retained for command-line compatibility. Raw files are never
    downloaded or overwritten by this step.
    """

    del force
    ensure_project_directories()
    files = input_files()
    if not files:
        raise FileNotFoundError("data/raw 中没有 PDF、Markdown 或 TXT 文件。")

    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in files:
        try:
            results.append(_inspect_file(path))
        except Exception as exc:  # noqa: BLE001 - report every bad input together
            errors.append(f"{path}: {exc}")
    if errors:
        raise ValueError("原始文献验证失败：\n" + "\n".join(errors))
    return results


if __name__ == "__main__":
    for item in prepare_all():
        print(item)
