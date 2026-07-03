---
name: paper-writer
description: "撰写中英文学术论文的技能，支持docx文档导出。支持毕业论文、课程论文、开题报告、文献综述、文献精读、选题报告、thesis、journal article、conference paper、research proposal 等学术文体。覆盖完整流程：学术文献检索 → 分章节写作 → 科研图表 → DOCX 排版与导出。"
---

# 学术论文写作

端到端论文写作流程。支持中文学术论文（GB/T 7714 引用）和英文学术论文（APA/IEEE/Chicago 等引用）。本技能通过 JS 脚本（docx-helper）生成文档。下文提到的 `multi_round_search`、`search_and_save`、`run_node_docx` 等均为**技能脚本目录中的函数**，在 `python_cell_exec` 中 import 后调用，不是需要单独具备的外部工具。

## 重要规则
1. **读取参考文件时完整读取，不要截断**
2. 保留最后的 JS 文件

---

## 执行流程

按顺序执行，每步完成后再进入下一步。

开始前一次性读取对应语言的参考文档和 DOCX API 参考：

- **[中文]** [chinese-paper-reference.md](references/chinese-paper-reference.md) + [docx-api.md](references/docx-api.md)
- **[EN]** [international-paper-reference.md](references/international-paper-reference.md) + [docx-api.md](references/docx-api.md)

### 步骤 1：文献检索

导入 `academic_search` 模块，调用 `await ac.multi_round_search()` 一次完成全部检索（导入和调用代码见参考文档"检索代码模板"），**必须传 `refs_json` 参数落盘**。中文论文**必须传 `zh_ratio`**（从参考文档字数表查值），不足时自动追加中文检索。

检索预算、代码模板、数据源选择见参考文档"文献检索"章节。

写作中引用不足时，调用 `await ac.search_and_save()` 补检索（传相同 `refs_json` 追加）。只引用学术来源，禁止 CSDN/知乎/百度百科等非学术网页。

**此步骤不可跳过**。`refs_json` 文件是后续生成参考文献的唯一数据来源。搜索结果不理想时，调整关键词、换数据源或用网页搜索补充，**禁止手动创建或覆盖 `refs_json` 文件**。数据来源质量不够完美也优于手写幻觉数据。

### 步骤 2：写作规划

1. **确定文体**：根据用户描述匹配（提到"毕业"→学位论文，"课程/作业"→课程论文，"开题"→开题报告……），无法判断时询问用户
2. **章节结构以参考文档为准**：从参考文档查该文体的章节模板和各章字数分配，严格按此结构写作

### 步骤 3：分章节写作与 DOCX 排版

按 [docx-api.md](references/docx-api.md) 编写 JS 脚本（基于 `docx-helper` API），逐章构建文档内容并写入 JS 文件。写作规范和文风要求见参考文档。

写作规则：
- **按章节分批写入**，每个一级章节至少单独一批
- **段落 ≥ 250 字**（英文 ≥ 180 words）
- **一次成稿**：写作前规划好每章段落数和篇幅，写作时一次写到位
- **引用**：只引用 `references.json` 中存在的 key，禁止凭记忆编造作者姓名。综述章每个主题段建议引用 ≥ 3 篇
- **参考文献**：正文用 `[@key]`，文末用 `refs.autoBibliography()` 自动生成
- **图表**：数据图表（柱状图/折线图/饼图等）用 `scientific_visualization` 生成 300dpi PNG；流程图和框架图用 `generate_image` 工具生图。API 见 docx-api.md 第七节

### 步骤 4: 产物交付

在 `python_cell_exec` 中导入 `run_node_docx` 函数执行 JS 文件（导入方式见 docx-api.md），成功后不做额外检查，**直接交付文档**。

引用一致性和错误引用的清理由 `autoBibliography` 和 `run_node_docx` 自动处理，无需人工复核。