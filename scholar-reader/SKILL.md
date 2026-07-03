---
name: scholar-reader
description: |
  Use when user asks to "read paper", "analyze paper", "summarize paper",
  "读论文", "分析文献", "帮我看一下这篇paper", "论文笔记", or provides a PDF file
  that appears to be an academic paper. Specialized for social science papers.

  Also supports Zotero integration: "读一下这篇论文 ...", "快速看一下这篇论文 ...",
  "批判性分析这篇论文 ...", "读一下 Zotero 里的 XXX", "批量读一下 Zotero 里 FoMO 分类下的论文"

  **重要触发词**: "读一下 XXX"、"读一下这篇"、"帮我读" → 必须调用此 skill
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
---

> **开始前**: 先跟用户打个招呼 🐕

# 社科论文阅读助手 (Scholar Reader)

专注社会科学领域（教育学、心理学、管理学、传播学等），支持 Zotero 集成和 Obsidian 笔记保存。

## Step 0: 读取共享配置

先读取 `../_shared/scholar-config.json`，如果 `../_shared/scholar-config.local.json` 存在，再用它覆盖默认值。

显式生成并在后续统一使用这些变量：

- `VAULT_PATH`
- `NOTES_PATH`
- `CONCEPTS_PATH`
- `ZOTERO_DB`
- `ZOTERO_STORAGE`
- `AUTO_REFRESH_INDEXES`
- `GIT_COMMIT_ENABLED`
- `GIT_PUSH_ENABLED`

其中：

- `NOTES_PATH = {VAULT_PATH}/{paper_notes_folder}`
- `CONCEPTS_PATH = {NOTES_PATH}/{concepts_folder}`
- `GIT_PUSH_ENABLED` 只有在 `GIT_COMMIT_ENABLED=true` 时才可能为真

后续统一使用上面的变量。

## 1. 接收论文

| 输入方式 | 示例 | 处理方法 |
|----------|------|----------|
| DOI 链接 | `https://doi.org/10.1016/...` | WebFetch 获取论文页面 |
| PDF 路径 | `/path/to/paper.pdf` | 直接 Read |
| Zotero 分类 | "FoMO 分类的论文" | 查询数据库 → 列出 → 用户选择 |
| Zotero 搜索 | "Zotero 里的 Przybylski" | 搜索标题/作者 → 找到 PDF |
| 无 PDF | Zotero 条目无附件 | 从网上获取（见下方） |

### 无 PDF 时的获取流程

1. `python3 assets/zotero_helper.py info {item_id}` 获取论文信息
2. 按优先级获取：DOI 页面 > WebSearch 标题 > 请求用户提供 PDF
3. 判断 DOI：从 Zotero DOI 字段 / URL 字段 / 标题搜索
4. WebFetch DOI 对应的出版商页面，尝试获取全文
5. 跳过条件：既无 PDF 也无在线来源 / 非论文内容

> Zotero 详细操作见 `references/zotero-guide.md`

## 2. 阅读模式

| 模式 | 触发词 | 输出 |
|------|--------|------|
| **快速摘要** | "快速看一下"、"quick" | 3-5 句核心贡献 |
| **完整解析** | "详细分析"、默认 | 结构化笔记（用模板） |
| **批判分析** | "批判性分析"、"critique" | 方法论优缺点评估 |
| **知识提取** | "提取效应量"、"统计结果" | 提取效应量和统计结果 |

## 3. 笔记生成

**模板**: 严格遵循 `assets/paper-note-template.md`，不可自行简化。

### 核心质量规则

1. **统计准确**: 所有统计结果必须准确转录（p值、t值、F值、卡方值等）
2. **效应量完整**: 效应量（r, β, d, OR, η²）和置信区间不能遗漏
3. **内联概念链接**: 正文中首次出现的理论、构念、量表名必须用 `[[概念]]` 链接
4. **测量工具详录**: 每个量表的名称、维度、题项数、信度 α 值必须记录
5. **样本信息完整**: 样本量、来源、人口统计特征必须记录

> 详细质量规范见 `references/quality-standards.md`

### 图片获取流程（简化版）

社科论文笔记以文字内容为核心，图片为辅助。

1. 如果论文有 DOI，尝试 WebFetch 出版商页面提取关键图表（如结构方程模型图、交互效应图）
2. 如果有本地 PDF，可用 `pdfimages -png` 提取关键图片（筛选 >10KB）
3. 找不到图片时直接跳过，在笔记中用文字描述模型/框架即可
4. 提取到的图片保存到 `assets/` 文件夹，用 `![[]]` wikilink 嵌入

### 表格处理

社科论文中的相关矩阵、回归结果表、测量模型表等必须完整转录：
- 保留所有行列数据
- 显著性标记（*, **, ***）必须保留
- 括号内的标准误/置信区间必须保留

## 4. Obsidian 保存

### 文件命名

使用**第一作者姓 + 年份**格式：`{FirstAuthor}{Year}.md`（如 `Przybylski2013.md`、`Wang2024.md`）。
多个同作者同年论文用字母后缀：`Wang2024a.md`、`Wang2024b.md`。

### 保存路径

按 Zotero 分类层级：`{NOTES_PATH}/{zotero_collection_path}/{FirstAuthor}{Year}.md`

### YAML frontmatter

```yaml
---
title: "论文标题"
authors: [Author1, Author2]
year: 2025
journal: "Journal Name"
doi: "10.xxxx/xxxxx"
tags: [tag1, tag2]  # 小写连字符，3-8 个
zotero_collection: {zotero_path}
created: YYYY-MM-DD
---
```

Tags 判断：看 Keywords / Abstract 关键词 / 理论框架。第一个 tag 是最核心主题。
常用 tags 示例：`self-determination-theory`, `fomo`, `social-media`, `well-being`, `meta-analysis`, `sem`, `longitudinal`, `cross-sectional`, `mediation`, `moderation`, `scale-development`

### 保存后自动执行

1. 只有在 `AUTO_REFRESH_INDEXES=true` 时才刷新目录页：
   ```bash
   python3 ../_shared/generate_concept_mocs.py
   python3 ../_shared/generate_paper_mocs.py
   ```
2. 只有在 `GIT_COMMIT_ENABLED=true` 时才做 git：
   - 先确认 `VAULT_PATH/.git` 存在
   - `git add {新增文件} {paper_notes_folder}/` 后必须真的有 staged changes
   - 满足条件后再执行：
   ```bash
   cd {VAULT_PATH} && git add {新增文件} {paper_notes_folder}/ && git commit -m "add paper note: {FirstAuthor}{Year}"
   ```
   - 只有在 `GIT_PUSH_ENABLED=true` 且仓库已配置远端时才 push

## 5. 概念库维护（每篇论文必做）

概念库位置：`{CONCEPTS_PATH}`

### 流程

1. **扫描**论文笔记中所有 `[[概念]]` 链接
2. **检查**每个链接对应的概念笔记是否存在（`ls` + `find`）
3. **创建**不存在的概念（不可跳过），自动归类到对应子目录

> 分类规则和模板见 `references/concept-categories.md`

### 自检

- [ ] 笔记中所有 `[[概念]]` 链接的概念笔记都存在？
- [ ] 概念笔记包含本论文作为"代表工作"？

## 6. 完成后自检（合并 checklist）

- [ ] 所有统计结果准确转录（效应量、p值、CI）？
- [ ] 所有测量工具信息完整（量表名、α值、题项数）？
- [ ] 所有 Table 完整保留（所有行列、显著性标记）？
- [ ] 正文中理论/构念/量表名有 `[[概念]]` 内联链接？
- [ ] 概念库已更新（缺失的概念已创建）？
- [ ] 样本信息完整（N、来源、人口统计）？

## 7. 交互式功能

完成解析后询问：深入解释？对比其他论文？保存到 Obsidian？
保存后自动创建缺失概念笔记，报告新增概念数量。

## 8. 批量处理

支持 Zotero 分类批量处理（默认递归子分类）。流程：递归获取论文 → 去重 → 跳过已有笔记 → 依次处理 → 汇总。

## 参考文件（按需查阅）

- **`references/zotero-guide.md`** — Zotero 查询、分类、PDF 路径获取、智能分类判断
- **`references/concept-categories.md`** — 概念自动归类的 6 个子目录规则 + 模板
- **`references/quality-standards.md`** — 统计结果/表格/测量工具的详细质量规范 + 自检清单
