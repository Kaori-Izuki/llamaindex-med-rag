"""Download the local embedding and generation models into the project."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import shutil

import requests

from huggingface_hub import snapshot_download

from .config import EMBEDDING_MODEL_DIR, EMBEDDING_MODEL_ID, LLM_MODEL_DIR, LLM_MODEL_ID


MODELSCOPE_API = "https://www.modelscope.cn/api/v1/models/Qwen/Qwen2.5-0.5B-Instruct/repo/files?Revision=master&Recursive=true"
MODELSCOPE_FILE = "https://www.modelscope.cn/models/Qwen/Qwen2.5-0.5B-Instruct/resolve/master/{name}"
USER_AGENT = "homework6-local-rag/1.0"


def _has_model_files(path: Path) -> bool:
    return path.exists() and (path / "config.json").exists() and any(path.glob("*.safetensors"))


def _download_small_file(url: str, destination: Path) -> None:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=120)
    response.raise_for_status()
    destination.write_bytes(response.content)


def _download_large_file_in_ranges(url: str, destination: Path, size: int) -> None:
    """Download a large ModelScope LFS file with resumable parallel ranges."""

    if destination.exists() and destination.stat().st_size == size:
        return
    part_dir = destination.parent / f".{destination.name}.parts"
    part_dir.mkdir(parents=True, exist_ok=True)
    chunk_size = 16 * 1024 * 1024
    ranges = [(start, min(size - 1, start + chunk_size - 1)) for start in range(0, size, chunk_size)]

    def fetch(item: tuple[int, int]) -> Path:
        start, end = item
        part = part_dir / f"part_{start:012d}"
        expected = end - start + 1
        if part.exists() and part.stat().st_size == expected:
            return part
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Range": f"bytes={start}-{end}"},
            stream=True,
            timeout=(30, 300),
        )
        response.raise_for_status()
        if response.status_code != 206 and start != 0:
            raise RuntimeError(f"服务器未返回分块响应：status={response.status_code}, range={start}-{end}")
        with part.open("wb") as handle:
            for block in response.iter_content(chunk_size=1024 * 1024):
                if block:
                    handle.write(block)
        if part.stat().st_size != expected:
            raise RuntimeError(f"分块大小不符：{part} {part.stat().st_size}/{expected}")
        return part

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch, item) for item in ranges]
        for future in as_completed(futures):
            future.result()
    with destination.open("wb") as output:
        for start, _ in ranges:
            output.write((part_dir / f"part_{start:012d}").read_bytes())
    if destination.stat().st_size != size:
        raise RuntimeError(f"模型权重合并后大小不符：{destination.stat().st_size}/{size}")
    shutil.rmtree(part_dir, ignore_errors=True)


def _download_qwen_from_modelscope(local_dir: Path) -> None:
    """Download the same Qwen model from ModelScope when HF is slow/unavailable."""

    response = requests.get(MODELSCOPE_API, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    files = response.json().get("Data", {}).get("Files", [])
    if not files:
        raise RuntimeError("ModelScope 文件列表为空")
    local_dir.mkdir(parents=True, exist_ok=True)
    for item in files:
        name = item.get("Name", "")
        size = int(item.get("Size") or 0)
        if not name or name.startswith("/") or "/" in name:
            continue
        destination = local_dir / name
        url = MODELSCOPE_FILE.format(name=name)
        if size >= 64 * 1024 * 1024:
            _download_large_file_in_ranges(url, destination, size)
        elif not destination.exists() or destination.stat().st_size != size:
            _download_small_file(url, destination)


def ensure_models() -> list[dict[str, str | bool]]:
    outputs: list[dict[str, str | bool]] = []
    for model_id, local_dir in (
        (EMBEDDING_MODEL_ID, EMBEDDING_MODEL_DIR),
        (LLM_MODEL_ID, LLM_MODEL_DIR),
    ):
        local_dir.mkdir(parents=True, exist_ok=True)
        if _has_model_files(local_dir):
            outputs.append({"model_id": model_id, "local_dir": str(local_dir), "cached": True})
            continue
        if model_id == LLM_MODEL_ID:
            _download_qwen_from_modelscope(local_dir)
        else:
            snapshot_download(
                repo_id=model_id,
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
                resume_download=True,
            )
        outputs.append({"model_id": model_id, "local_dir": str(local_dir), "cached": False})
    return outputs


if __name__ == "__main__":
    for item in ensure_models():
        print(item)
