# 运行截图说明

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
