# Homework 6：基于 LlamaIndex 的本地 RAG 医学文献问答助手

本项目使用 4 篇 PubMed/PMC 开放全文医学文献，构建不依赖 Ollama、付费 API 或在线 LLM 的本地 RAG 问答系统。系统流程为：

`医学文献 → 清洗 → SentenceSplitter → BGE embedding → VectorStoreIndex → 相似度检索 → Qwen 本地生成 → source_nodes 证据输出`

## 目录

```text
homework6/
├── data/
│   ├── raw/                         # 用户只需向这里增加任意命名的 PDF/MD/TXT
│   ├── processed/                   # 旧版运行遗留的兼容目录（raw 有文件时不参与索引）
│   └── literature_metadata.csv
├── models/                          # BGE 和 Qwen 模型，迁移电脑时随项目复制
├── src/
├── storage/                         # 按 embedding/chunk 参数区分的持久化索引
├── results/                         # JSON、Markdown、CSV、终端日志
├── reports/实验报告.md
├── screenshots/README.md
├── main.py
├── requirements.txt
└── run.ps1
```

## 实际使用的模型和参数

- Embedding：`BAAI/bge-small-en-v1.5`，英文医学文献，项目内 `models/embedding/bge-small-en-v1.5`。
- LLM：`Qwen/Qwen2.5-0.5B-Instruct`，项目内 `models/llm/Qwen2.5-0.5B-Instruct`，CPU 推理，中文回答。
- `chunk_size=512`，`chunk_overlap=50`，`similarity_top_k=3`，`temperature=0.1`，最多生成 256 tokens。
- 参数实验实际比较 `chunk_size=256/512/1024` 和 `similarity_top_k=1/3/5`。

## Windows 11 运行

在项目根目录打开 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

脚本会创建/复用 `.venv`，安装 `requirements.txt`，下载缺失的模型到项目目录，再执行 `python main.py`。模型和索引存在时会复用缓存；程序会比较 `data/raw` 中源文件的 SHA-256 指纹，新增、删除或修改文献后自动重建索引。首次运行需要网络和约 2 GB 以上磁盘空间；本地模型下载完成后可迁移整个 `homework6` 目录到另一台 Windows 11 电脑。

也可以直接使用虚拟环境：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 新增文献：只操作 data/raw

后续使用时不需要修改 Python 代码，也不需要填写 CSV。把任意文件名的文献复制到：

```text
data/raw/
```

支持：

- 可提取文本的 `.pdf`；
- `.md` Markdown；
- `.txt` 纯文本。

然后直接运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

程序会自动扫描文件、校验 PDF 文件头和文本层、加载文献、重建必要索引、运行问答和参数实验。原始文件名可以是中文或英文，不要求固定命名规则。当前 `data/raw` 有一个或多个支持格式文件时，旧的 `data/processed` 不会混入索引，避免旧文献重复进入系统。

如果只想快速更新问答、不等待参数实验：

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 --skip-experiments
```

扫描 PDF 如果没有文本层（例如纯扫描图片），程序会明确报错；请先 OCR 后再放入 `data/raw`。`data/literature_metadata.csv` 现在只是可选的题名、作者、PMID/PMCID 来源补充，不再是新增文献的必填文件。

## 常用选项

```powershell
.\.venv\Scripts\python.exe main.py --skip-experiments
.\.venv\Scripts\python.exe main.py --refresh-data
.\.venv\Scripts\python.exe main.py --force-rebuild
.\.venv\Scripts\python.exe main.py --skip-model-download
```

`--skip-model-download` 只适用于模型已经存在于项目目录的离线运行。`--force-rebuild` 可强制重建索引；正常情况下源文件指纹变化会自动触发重建。若网络不可用且模型/依赖尚未下载，程序会真实报错并写入 `results/experiment_error.log`，不会用固定答案伪装成功。

## 数据与全文

文献输入以 `data/raw/` 为准。程序直接使用 `SimpleDirectoryReader` 读取其中的 PDF、Markdown 和 TXT，并保留来源文件名；CSV 中的 PubMed/PMC 字段仅在文件名能够匹配时用于补充元数据。旧版 `data/processed/` 仅在 `data/raw/` 没有可识别文件时作为兼容回退。

## 结果说明

- `results/qa_results.json`：4 个问题的完整答案、运行参数和 source_nodes。
- `results/qa_results.md`：便于阅读的答案、来源文件、相似度分数和检索片段。
- `results/parameter_comparison.csv`：6 组实际参数对比实验。
- `results/experiment_log.txt`：运行摘要；`results/terminal_run.log`：完整 PowerShell 运行日志。
- `reports/实验报告.md`：基于本次真实运行数据生成的中文实验报告。
- `screenshots/01_*.png` 至 `screenshots/08_*.png`：由本次真实结果文件自动渲染的 PNG 快照。

## 设计要点

`SimpleDirectoryReader` 直接读取 `data/raw` 中的 PDF/Markdown/TXT；`SentenceSplitter` 负责节点切分；`HuggingFaceEmbedding` 使用本地 BGE；`VectorStoreIndex` 按参数目录和源文件指纹持久化；查询结果显式序列化 `source_nodes`、来源文件、相似度分数、元数据和文本片段。提示词要求模型只依据检索内容回答，证据不足时拒答或说明不确定性。

## 常见错误

- `ModuleNotFoundError`：从项目根目录运行 `run.ps1`，不要调用系统 Python；脚本会在 `.venv` 中安装依赖。
- PDF 未被读取：确认扩展名是 `.pdf`，且 PDF 有文本层；扫描版 PDF 需要 OCR。
- 模型下载失败：检查网络后重试；不要删除已有模型目录，下载器支持续传。
- 内存不足：设置 `$env:HOMEWORK6_DEVICE='cpu'`，并使用 `--skip-experiments` 先验证主流程。
- 文献重复或旧文献仍出现：确认 `data/raw/` 中没有同一篇文献的 PDF 和 Markdown 两份副本；raw 有文件时，旧 `data/processed/` 不会参与索引。
- 需要提交截图：只截取真实运行窗口；本项目未生成伪造 PNG，截图待办和日志位置见 `screenshots/README.md`。
