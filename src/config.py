"""Central project configuration.

All project paths are derived from this file so that the directory can be
moved to another Windows 11 computer without rewriting absolute paths.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT_DIR / "models"
EMBEDDING_MODEL_DIR = MODELS_DIR / "embedding" / "bge-small-en-v1.5"
LLM_MODEL_DIR = MODELS_DIR / "llm" / "Qwen2.5-0.5B-Instruct"
STORAGE_DIR = ROOT_DIR / "storage"
RESULTS_DIR = ROOT_DIR / "results"
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"

METADATA_PATH = DATA_DIR / "literature_metadata.csv"

EMBEDDING_MODEL_ID = os.getenv("HOMEWORK6_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
LLM_MODEL_ID = os.getenv("HOMEWORK6_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
SIMILARITY_TOP_K = 3
LLM_TEMPERATURE = 0.1
LLM_MAX_NEW_TOKENS = 256
LLM_CONTEXT_WINDOW = 4096
DEVICE = os.getenv("HOMEWORK6_DEVICE", "cpu")

SYSTEM_PROMPT = """你是一个医学文献问答助手。你只能依据检索到的文献上下文回答，不能凭常识补写文献没有支持的研究结果。

请遵守以下规则：
1. 使用中文回答，但保留药物、靶点和研究术语的英文缩写。
2. 区分文献明确报告的结果、文献中的机制解释和你的谨慎归纳。
3. 尽可能在句末用 [来源文件] 标注证据；如果多个来源共同支持，请分别列出。
4. 如果上下文不足以回答，明确写“现有文献证据不足”，并解释缺少什么证据。
5. 不要编造患者个体疗效、具体生存期、未在上下文出现的数值或临床建议。
6. 回答应简洁、结构清楚，优先使用要点或小标题。
"""

TEST_QUESTIONS = [
    {
        "id": "fact_mechanism",
        "type": "事实型",
        "question": "根据这些文献，PD-1/PD-L1 与 CTLA-4 分别在 T 细胞激活的哪个阶段发挥抑制作用？它们解除抑制后主要带来哪些免疫学变化？",
    },
    {
        "id": "comparison_dual_vs_single",
        "type": "比较型",
        "question": "与单药 PD-1/PD-L1 抑制相比，PD-1/PD-L1 联合 CTLA-4 阻断在作用机制、潜在疗效和免疫相关不良事件方面有哪些差异？",
    },
    {
        "id": "summary_benefits_limits_irae",
        "type": "总结型",
        "question": "根据这些文献，总结免疫检查点抑制剂治疗的主要优势、局限性以及常见免疫相关不良事件，并指出证据来源。",
    },
    {
        "id": "evidence_insufficient",
        "type": "证据不足测试",
        "question": "仅根据当前本地文献库，能否准确预测某一位具体患者接受纳武利尤单抗后的个人生存月数？请说明理由。",
    },
]

COMPARISON_QUESTION = TEST_QUESTIONS[1]["question"]


def ensure_project_directories() -> None:
    """Create only the project directories that are part of the deliverable."""

    for path in (
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        MODELS_DIR,
        STORAGE_DIR,
        RESULTS_DIR,
        REPORTS_DIR,
        SCREENSHOTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def index_dir(chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> Path:
    """Return a parameter-specific persistent index directory."""

    model_tag = EMBEDDING_MODEL_ID.split("/")[-1].replace("-", "_")
    return STORAGE_DIR / f"index_{model_tag}_c{chunk_size}_o{chunk_overlap}"
