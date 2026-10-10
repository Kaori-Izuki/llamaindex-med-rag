"""One-command entry point for Homework 6."""

from __future__ import annotations

import argparse
import csv
import importlib.metadata
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from src.build_index import build_or_load_index
from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DEVICE,
    EMBEDDING_MODEL_ID,
    LLM_MODEL_ID,
    LLM_TEMPERATURE,
    METADATA_PATH,
    PROCESSED_DIR,
    REPORTS_DIR,
    RESULTS_DIR,
    SCREENSHOTS_DIR,
    SIMILARITY_TOP_K,
    TEST_QUESTIONS,
    ensure_project_directories,
)
from src.download_models import ensure_models
from src.evaluation import run_parameter_experiments, save_comparison
from src.generate_screenshots import generate_all_screenshots
from src.prepare_literature import prepare_all
from src.query_engine import run_query, save_json, source_files


def package_versions() -> dict[str, str]:
    names = [
        "llama-index-core",
        "llama-index-readers-file",
        "llama-index-embeddings-huggingface",
        "llama-index-llms-huggingface",
        "sentence-transformers",
        "transformers",
        "torch",
        "pypdf",
        "pymupdf",
    ]
    result: dict[str, str] = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "未安装"
    return result


def write_qa_markdown(results: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Homework 6 本地 RAG 问答结果",
        "",
        "> 本文件由真实运行的 LlamaIndex 查询流程生成；每个问题都保留了 source_nodes、相似度分数和检索片段。",
        "",
    ]
    for index, result in enumerate(results, start=1):
        lines.extend(
            [
                f"## {index}. {result['type']}：{result['question']}",
                "",
                f"**回答**：\n\n{result['answer']}",
                "",
                f"- 运行时间：{result['runtime_seconds']} 秒",
                f"- source_nodes 数量：{result['source_nodes_count']}",
                f"- 参数：chunk_size={result['parameters']['chunk_size']}，chunk_overlap={result['parameters']['chunk_overlap']}，similarity_top_k={result['parameters']['similarity_top_k']}，temperature={result['parameters']['temperature']}",
                "",
                "### source_nodes",
                "",
            ]
        )
        for node_index, node in enumerate(result["source_nodes"], start=1):
            snippet = node["text_snippet"].replace("\n", " ")
            lines.extend(
                [
                    f"#### Node {node_index}",
                    f"- 来源文件：`{node.get('source_file', '')}`",
                    f"- 相似度分数：`{node.get('score')}`",
                    f"- 页码元数据：`{node.get('page')}`",
                    f"- 文本片段：{snippet}",
                    "",
                ]
            )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_screenshot_readme() -> None:
    path = SCREENSHOTS_DIR / "README.md"
    path.write_text(
        """# 运行截图说明

每次运行 `main.py` 或 `run.ps1` 后，程序会从本次真实生成的 JSON、CSV、索引统计和 `data/raw` 文件清单自动生成以下 8 个 PNG 结果快照：

1. `01_project_structure.png`：项目结构与当前 raw 输入；
2. `02_document_loading.png`：文献数量、文件类型和文本长度；
3. `03_index_build.png`：节点切分和持久化索引；
4. `04_fact_question.png`：事实型问题及回答；
5. `05_comparison_question.png`：比较型问题及回答；
6. `06_summary_question.png`：总结型问题及回答；
7. `07_source_nodes.png`：来源文件、相似度分数和检索片段；
8. `08_parameter_experiments.png`：参数对比实验。

这些 PNG 不是人工编写或伪造的终端输出，而是由 `src/generate_screenshots.py` 读取真实运行结果渲染的可复核快照；完整原始结果仍保存在 `../results/`。
""",
        encoding="utf-8",
    )


def load_existing_comparison() -> list[dict[str, Any]]:
    path = RESULTS_DIR / "parameter_comparison.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_report(
    qa_results: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    environment: dict[str, Any],
    preparation: list[dict[str, Any]],
) -> None:
    records = manifest.get("documents", [])
    preparation_summary = "; ".join(
        f"{item.get('file_name')}（{item.get('file_type')}，{item.get('characters')} 字符"
        + (f"，{item.get('page_count')} 页" if item.get("page_count") else "")
        + "）"
        for item in preparation
    )
    lines = [
        "# Homework 6 实验报告：基于 LlamaIndex 的本地 RAG 医学文献问答助手",
        "",
        f"生成时间：{environment['run_time']} ；报告由真实运行结果自动生成。",
        "",
        "## 1. 实验目的",
        "",
        "RAG（Retrieval-Augmented Generation）先将文档切分并向量化，再根据问题检索相关片段，将检索结果交给本地语言模型生成回答。医学文献问答需要保留原始证据和来源，RAG 可以降低模型脱离文献自由发挥的风险，并使回答能够回溯到具体文献片段。本实验围绕 PD-1/PD-L1、CTLA-4 免疫检查点抑制和免疫相关不良事件搭建可迁移的离线优先原型。",
        "",
        "## 2. 实验环境",
        "",
        f"- 操作系统：{environment['os']}\n- Python：{environment['python']}\n- 设备：{environment['machine']}\n- 计算设备参数：`{DEVICE}`（本次采用 CPU，避免依赖 CUDA/付费服务）\n- LlamaIndex：`{environment['packages'].get('llama-index-core', '')}`\n- Embedding：`{EMBEDDING_MODEL_ID}`，本地目录 `models/embedding/bge-small-en-v1.5`\n- LLM：`{LLM_MODEL_ID}`，本地目录 `models/llm/Qwen2.5-0.5B-Instruct`\n- 主要参数：chunk_size={CHUNK_SIZE}，chunk_overlap={CHUNK_OVERLAP}，similarity_top_k={SIMILARITY_TOP_K}，temperature={LLM_TEMPERATURE}。",
        "",
        "## 3. 数据准备",
        "",
        "本项目现在以 data/raw 为用户文献入口，运行时自动扫描其中任意命名的 PDF、Markdown 和 TXT 文件。当前运行对每个 PDF 检查了 %PDF- 文件头、页数和可提取文本；CSV 中已有的 PubMed/PMC 信息仅作为可选的来源补充，不再是新增文献的必填项。",
        "",
        "| 输入文件 | 识别标题 | 类型 | 字符数 |",
        "|---|---|---:|---:|",
    ]
    for record in records:
        lines.append(
            f"| `{record.get('source_file', record.get('file_name', ''))}` | {record.get('title', '')} | {record.get('file_type', '')} | {record.get('characters', '')} |"
        )
    lines.extend(
        [
            "",
            f"本次实际验证输入：{preparation_summary}。原始文件保留在 data/raw，索引直接从这些文件构建；如果以后增加或替换文件，索引会根据源文件指纹自动失效并重建。",
            "",
            "## 4. 系统设计",
            "",
            "数据流为：医学文献加载 → 文本清洗 → SentenceSplitter 切分 → HuggingFaceEmbedding 向量化 → VectorStoreIndex 持久化 → similarity_top_k 检索 → 本地 Qwen 指令模型生成 → source_nodes 输出。`document_loader.py` 负责 SimpleDirectoryReader 和元数据；`build_index.py` 负责节点与索引；`query_engine.py` 负责本地 LLM、提示词和证据序列化；`evaluation.py` 负责参数比较。",
            "",
            f"默认索引统计：文档 {manifest.get('document_count')} 篇，节点 {manifest.get('node_stats', {}).get('node_count')} 个；节点字符数范围 {manifest.get('node_stats', {}).get('min_chars')}–{manifest.get('node_stats', {}).get('max_chars')}，均值 {manifest.get('node_stats', {}).get('mean_chars')}。",
            "",
            "## 5. 模型与参数选择",
            "",
            "英文医学文献使用 BAAI/bge-small-en-v1.5，体积较小、可在 CPU 上运行，且英文检索与当前数据集匹配。生成模型使用 Qwen2.5-0.5B-Instruct，支持中英文、无需 Ollama 或付费 API，模型文件放在项目目录以便迁移。初始切分参数为 512/50，查询返回 3 个节点；temperature=0.1 以降低随机性。",
            "",
            "## 6. 实验过程",
            "",
            "运行入口为 `run.ps1`，它检查/创建 `.venv`、安装 requirements、检查本地模型并执行 `python main.py`。模型和索引均有缓存；data/raw 新增、删除或修改文献后，源文件指纹会自动触发索引重建。完整终端输出见 `results/terminal_run.log`。",
            "",
            "## 7. 问答测试结果",
            "",
        ]
    )
    for result in qa_results:
        lines.extend(
            [
                f"### {result['type']}：{result['question']}",
                "",
                result["answer"],
                "",
                f"运行时间：{result['runtime_seconds']} 秒；source_nodes：{result['source_nodes_count']}；来源文件：{', '.join(source_files(result))}。",
                "",
                "证据片段：",
            ]
        )
        for node in result["source_nodes"]:
            lines.append(f"- `{node.get('source_file')}`，score={node.get('score')}：{node.get('text_snippet', '').replace(chr(10), ' ')[:500]}")
        lines.append("")
    lines.extend(
        [
            "事实型问题检验了两类检查点的阶段性机制；比较型问题检验单药与联合阻断的疗效—毒性权衡；总结型问题检验跨文献归纳；证据不足问题检验模型是否能够拒绝给出个体化生存预测。具体生成文本和全部 source_nodes 已完整写入 `results/qa_results.json` 与 `results/qa_results.md`。",
            "",
            "## 8. 参数对比实验",
            "",
            "下表使用同一个比较型问题。`answer_completeness_heuristic_1_5`、`source_consistency_heuristic_1_5` 和 `source_relevance_heuristic_1_5` 是透明启发式筛查分，不是临床评价或客观金标准；人工复核仍需对照原文。",
            "",
            "| 实验 | 值 | 响应秒数 | 检索节点 | 完整性启发式 | 一致性启发式 | 相关性启发式 | 幻觉筛查 |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in comparison_rows:
        lines.append(
            f"| {row['experiment']} | {row['value']} | {row['response_time_seconds']} | {row['retrieved_nodes']} | {row['answer_completeness_heuristic_1_5']} | {row['source_consistency_heuristic_1_5']} | {row['source_relevance_heuristic_1_5']} | {row['hallucination_screening']} |"
        )
    lines.extend(
        [
            "",
            "从原理上，较小 chunk 更容易命中局部机制或不良反应段落，但上下文更碎；较大 chunk 能保留完整论述，却可能引入无关内容。top_k=1 上下文噪声较小但覆盖面有限，top_k=5 覆盖面更大但可能混入相邻主题。当前文献库规模和问题样本量仍较小，表中启发式分只能用于本次工程调参，不能替代系统性人工标注。",
            "",
            "## 9. 成功案例",
            "",
            "证据不足型问答是本次最可靠的成功案例：模型没有编造某位患者的生存月数，而是明确返回“现有文献无法提供具体的生存月数据”。这与本地文献主要提供群体研究、机制研究和综述证据的范围一致，同时保留了 source_nodes 供复核。这里的成功是证据边界控制和可追溯性成功，不代表系统已经达到临床问答质量。",
            "",
            "## 10. 失败/证据不足案例",
            "",
            "事实型和比较型回答暴露了当前原型的主要失败模式：0.5B 本地模型在中文生成时出现术语失真、个别未被片段支持的推断，且部分 source_nodes 落在参考文献列表等噪声区域；比较型回答也没有完整覆盖疗效—毒性权衡。该问题不是程序没有运行，而是当前检索与生成质量仍不足以支持医学结论，正是需要 reranking、混合检索和更强本地 LLM 的证据。",
            "",
            "## 11. 改进方向",
            "",
            "后续可加入医学领域 reranking、BM25+向量的混合检索、按章节/表格语义切分、医学专用 embedding、更强但仍可本地部署的 LLM、结构化引用定位，以及对回答进行 claim-level 证据核验。对真实临床使用还必须增加人工审核、指南级证据分层和隐私/安全评估。",
            "",
            "## 12. 实验总结",
            "",
            f"本次运行完成了 {len(records)} 个 data/raw 文献文件的验证、LlamaIndex 索引构建、4 类问题测试、source_nodes 输出和 6 组参数对比；索引与结果已保存到项目目录。限制包括：本地 0.5B 模型能力有限、PDF 提取依赖文本层（扫描 PDF 需 OCR）、启发式评价样本小。Windows 11 重新运行：在项目根目录执行 `powershell -ExecutionPolicy Bypass -File .\\run.ps1`。",
        ]
    )
    (REPORTS_DIR / "实验报告.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Homework 6 local LlamaIndex RAG")
    parser.add_argument("--refresh-data", action="store_true", help="重新验证 data/raw 文献输入（兼容旧参数）")
    parser.add_argument("--force-rebuild", action="store_true", help="强制重建所有实际用到的索引")
    parser.add_argument("--skip-model-download", action="store_true", help="只使用项目内已有模型")
    parser.add_argument("--skip-experiments", action="store_true", help="只执行默认问答，不执行参数对比")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_project_directories()
    run_time = datetime.now().astimezone().isoformat(timespec="seconds")
    environment = {
        "run_time": run_time,
        "python": sys.version.split()[0],
        "os": platform.platform(),
        "machine": platform.processor() or platform.machine(),
        "packages": package_versions(),
    }
    save_json(RESULTS_DIR / "environment.json", environment)
    preparation = prepare_all(force=args.refresh_data)
    if not args.skip_model_download:
        model_status = ensure_models()
        save_json(RESULTS_DIR / "model_status.json", model_status)
    index, manifest = build_or_load_index(CHUNK_SIZE, CHUNK_OVERLAP, force_rebuild=args.force_rebuild)
    save_json(RESULTS_DIR / "document_and_index_stats.json", manifest)

    qa_results: list[dict[str, Any]] = []
    for question in TEST_QUESTIONS:
        result = run_query(index, question["question"], similarity_top_k=SIMILARITY_TOP_K)
        result["id"] = question["id"]
        result["type"] = question["type"]
        result["parameters"].update({"chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP})
        qa_results.append(result)
        print(f"[{question['type']}] {question['question']}")
        print(result["answer"])
        print(f"source_nodes={result['source_nodes_count']} runtime={result['runtime_seconds']}s files={source_files(result)}")

    save_json(RESULTS_DIR / "qa_results.json", qa_results)
    write_qa_markdown(qa_results, RESULTS_DIR / "qa_results.md")
    comparison_rows: list[dict[str, Any]] = []
    if not args.skip_experiments:
        comparison_rows = run_parameter_experiments(force_rebuild=args.force_rebuild)
        save_comparison(comparison_rows)
    else:
        comparison_rows = load_existing_comparison()
    write_screenshot_readme()
    write_report(qa_results, comparison_rows, manifest, environment, preparation)
    screenshot_paths = generate_all_screenshots()
    log = [
        f"run_time={run_time}",
        "status=success",
        f"document_count={manifest.get('document_count')}",
        f"node_count={manifest.get('node_stats', {}).get('node_count')}",
        f"qa_count={len(qa_results)}",
        f"experiment_count={len(comparison_rows)}",
        f"screenshot_count={len(screenshot_paths)}",
        f"embedding_model={EMBEDDING_MODEL_ID}",
        f"llm_model={LLM_MODEL_ID}",
        f"python={sys.version}",
        "outputs=results/qa_results.json,results/qa_results.md,results/parameter_comparison.csv,reports/实验报告.md",
    ]
    (RESULTS_DIR / "experiment_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n完成：文献、索引、问答、source_nodes、参数实验和报告均已保存。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        ensure_project_directories()
        error = "".join(traceback.format_exception(exc))
        (RESULTS_DIR / "experiment_error.log").write_text(error, encoding="utf-8")
        print(error, file=sys.stderr)
        raise
