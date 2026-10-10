"""Render auditable PNG snapshots from the current real run artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .config import RESULTS_DIR, ROOT_DIR, SCREENSHOTS_DIR, STORAGE_DIR
from .document_loader import input_files


WIDTH = 1600
HEIGHT = 1200
BG = "#F4F7FB"
NAVY = "#16324F"
BLUE = "#1E6AA8"
TEXT = "#1F2937"
MUTED = "#5B6777"
CARD = "#FFFFFF"
LINE = "#D7E0EA"
GREEN = "#157347"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]
        if bold
        else [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]
    )
    candidates.extend([r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"])
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


FONT_TITLE = _font(34, True)
FONT_SUBTITLE = _font(19)
FONT_SECTION = _font(24, True)
FONT_BODY = _font(20)
FONT_SMALL = _font(17)
FONT_MONO = _font(17)


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw_line in str(text).splitlines() or [""]:
        current = ""
        for char in raw_line:
            candidate = current + char
            if current and ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(candidate, font=font) > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        lines.append(current)
    return lines


def _draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: str, max_width: int, line_gap: int = 8) -> int:
    x, y = xy
    lines = _wrap(text, font, max_width)
    bbox = draw.textbbox((x, y), "Ag中文", font=font)
    line_height = bbox[3] - bbox[1] + line_gap
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _render(name: str, title: str, subtitle: str, sections: list[tuple[str, str]]) -> Path:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 112), fill=NAVY)
    draw.text((48, 22), title, font=FONT_TITLE, fill="white")
    draw.text((50, 72), subtitle, font=FONT_SUBTITLE, fill="#D9E7F5")
    y = 142
    for section_title, content in sections:
        if y > HEIGHT - 100:
            break
        card_top = y
        wrapped = _wrap(content, FONT_BODY, WIDTH - 150)
        card_height = min(HEIGHT - card_top - 36, 84 + len(wrapped) * 33)
        draw.rounded_rectangle((40, card_top, WIDTH - 40, card_top + card_height), radius=16, fill=CARD, outline=LINE, width=2)
        draw.text((68, card_top + 22), section_title, font=FONT_SECTION, fill=BLUE)
        content_y = card_top + 62
        max_lines = max(1, (card_height - 84) // 33)
        visible = "\n".join(wrapped[:max_lines])
        _draw_wrapped(draw, (70, content_y), visible, FONT_BODY, TEXT, WIDTH - 150, line_gap=8)
        y = card_top + card_height + 22
    footer = "数据来自本次真实运行的 results/、storage/ 和 data/raw/；PNG 仅做可复核结果快照。"
    draw.text((48, HEIGHT - 32), footer, font=FONT_SMALL, fill=MUTED)
    path = SCREENSHOTS_DIR / name
    image.save(path, format="PNG", optimize=True)
    return path


def _structure_text() -> str:
    entries = [
        "homework6/",
        "├─ data/raw/  ← 用户新增 PDF / MD / TXT",
        "├─ models/  ← BGE + Qwen 本地模型",
        "├─ storage/  ← 按参数持久化索引",
        "├─ results/  ← JSON / Markdown / CSV / 日志",
        "├─ reports/实验报告.md",
        "├─ screenshots/  ← 本组 PNG",
        "├─ main.py",
        "├─ run.ps1",
        "└─ README.md",
        "\n当前 raw 输入：" + ", ".join(path.name for path in input_files()),
    ]
    return "\n".join(entries)


def generate_all_screenshots() -> list[Path]:
    stats = _load_json(RESULTS_DIR / "document_and_index_stats.json", {})
    qa_results = _load_json(RESULTS_DIR / "qa_results.json", [])
    rows = list(csv.DictReader((RESULTS_DIR / "parameter_comparison.csv").open(encoding="utf-8-sig", newline=""))) if (RESULTS_DIR / "parameter_comparison.csv").exists() else []
    generated: list[Path] = []
    generated.append(_render("01_project_structure.png", "Homework 6 · 项目结构", "真实运行结果快照 01/08", [("可迁移目录", _structure_text())]))

    document_lines = []
    for doc in stats.get("documents", []):
        document_lines.append(
            f"{doc.get('file_name')} | type={doc.get('file_type')} | chars={doc.get('characters')} | title={doc.get('title')}"
        )
    generated.append(
        _render(
            "02_document_loading.png",
            "Homework 6 · 文献加载",
            "真实运行结果快照 02/08 · data/raw 自动扫描",
            [("验证结果", f"文献文件数：{stats.get('document_count')}\n" + "\n".join(document_lines))],
        )
    )

    index_dirs = ", ".join(path.name for path in STORAGE_DIR.iterdir() if path.is_dir()) if STORAGE_DIR.exists() else ""
    generated.append(
        _render(
            "03_index_build.png",
            "Homework 6 · 切分与索引",
            "真实运行结果快照 03/08 · VectorStoreIndex",
            [
                (
                    "索引统计",
                    f"文献数：{stats.get('document_count')}\n节点数：{stats.get('node_stats', {}).get('node_count')}\n节点字符数：{stats.get('node_stats', {}).get('min_chars')}–{stats.get('node_stats', {}).get('max_chars')}，均值 {stats.get('node_stats', {}).get('mean_chars')}\nchunk_size={stats.get('chunk_size')}，chunk_overlap={stats.get('chunk_overlap')}\n持久化目录：{index_dirs}",
                )
            ],
        )
    )

    by_id = {item.get("id"): item for item in qa_results}
    qa_specs = [
        ("fact_mechanism", "04_fact_question.png", "事实型问题", "真实运行结果快照 04/08"),
        ("comparison_dual_vs_single", "05_comparison_question.png", "比较型问题", "真实运行结果快照 05/08"),
        ("summary_benefits_limits_irae", "06_summary_question.png", "总结型问题", "真实运行结果快照 06/08"),
    ]
    for key, filename, label, subtitle in qa_specs:
        item = by_id.get(key, {})
        sources = ", ".join(dict.fromkeys(node.get("source_file", "") for node in item.get("source_nodes", [])))
        answer = item.get("answer", "")
        generated.append(
            _render(
                filename,
                f"Homework 6 · {label}",
                subtitle,
                [
                    ("问题", item.get("question", "")),
                    ("模型回答", answer),
                    ("运行信息", f"runtime={item.get('runtime_seconds')} s | source_nodes={item.get('source_nodes_count')}\n来源：{sources}"),
                ],
            )
        )

    fact = by_id.get("fact_mechanism", {})
    node_lines = []
    for number, node in enumerate(fact.get("source_nodes", []), start=1):
        snippet = str(node.get("text_snippet", "")).replace("\n", " ")[:520]
        node_lines.append(f"Node {number} | source={node.get('source_file')} | score={node.get('score')} | page={node.get('page')}\n{snippet}")
    generated.append(
        _render(
            "07_source_nodes.png",
            "Homework 6 · source_nodes 证据",
            "真实运行结果快照 07/08 · 来源与相似度",
            [("事实型问题的召回证据", "\n\n".join(node_lines) or "无 source_nodes")],
        )
    )

    table_lines = ["experiment | value | chunk_size | top_k | nodes | seconds"]
    table_lines.extend(
        f"{row.get('experiment')} | {row.get('value')} | {row.get('chunk_size')} | {row.get('similarity_top_k')} | {row.get('retrieved_nodes')} | {row.get('response_time_seconds')}"
        for row in rows
    )
    generated.append(
        _render(
            "08_parameter_experiments.png",
            "Homework 6 · 参数对比",
            "真实运行结果快照 08/08 · parameter_comparison.csv",
            [("6 组实验结果", "\n".join(table_lines) or "尚未生成参数实验结果")],
        )
    )
    return generated


if __name__ == "__main__":
    for path in generate_all_screenshots():
        print(path)
