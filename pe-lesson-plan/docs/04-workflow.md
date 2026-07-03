# 交互流程

> 本文档定义三种模式的完整步骤。教案内容必须基于**人才培养方案 → 教学大纲/课程标准 → 教学计划/授课计划 → 教学设计**逐层推导，各环节与之紧密关联，禁止凭空填写。

---

## 生成教案（5 阶段 / 15 步）

### 阶段 A：上游文档链解析（新增）

> **目标**：从上游教学文档逐层提取信息，建立「培养目标 → 课程目标 → 周目标 → 课时目标」的逻辑链，为教案内容提供可靠来源。

#### 步骤 1：收集与识别上游文档

向用户确认可用的上游教学文档：

| 文档层级 | 文档名称 | 提供什么信息 |
|---------|---------|------------|
| L1 顶层 | **人才培养方案** | 培养目标、毕业要求、专业定位 |
| L2 课程 | **教学大纲 / 课程标准** | 课程目标、教学内容范围、学时分配、考核方式 |
| L3 进度 | **教学计划 / 授课计划 / 教学进度表** | 周次安排、每周教学内容、教学阶段划分、课程思政主题 |
| L4 设计 | **教学设计 / 教案设计说明**（如有） | 单次课的设计思路、教学方法选择依据 |

**执行规则**：
- 询问用户有哪些文档可用（可上传文件或提供文字）
- 不是每个层级都必须有文档：有 L3 授课计划就能推导出大部分内容，L1/L2/L4 为可选项
- 如果用户没有任何上游文档，进入**降级模式**（直接由用户提供教案信息，跳到阶段 B 步骤 5）
- 批量生成模式通常以 L3 授课计划为核心文档，L1/L2 为辅助

**输出**：已识别的上游文档列表 + 各文档来源（文件路径 / 文字内容）

#### 步骤 2：逐层提取关键信息

按文档层级从上到下提取，建立结构化摘要：

**L1 人才培养方案 → 提取：**
- 专业名称与定位
- 培养目标（与体育相关的表述）
- 毕业要求指标点（支撑本课程的）
- 课程在培养体系中的定位

**L2 教学大纲/课程标准 → 提取：**
- 课程名称、课程性质（必修/选修）、总学时
- **课程目标**（知识目标、能力目标、素质/思政目标）
- **教学内容与学时分配表**（哪些单元/模块、各占多少学时）
- 教学方法建议
- 考核方式与成绩构成

**L3 教学计划/授课计划 → 提取：**
- 总周次与当前周次位置
- 各教学阶段的划分（如：基础阶段/单练阶段/对练阶段/考核阶段）
- **本周教学内容**（新授内容 + 复习内容，原文照录）
- **本周目的要求**（教学目标 + 课程思政主题 + 量化指标，原文照录）
- 教学方式建议

**L4 教学设计（如有）→ 提取：**
- 设计理念与理论依据
- 教学方法选择的原因
- 重点难点的设计思路

**提取方法**：
- 文件类文档：用 `python-docx` 读取表格/段落，按层级结构解析
- 文字类信息：从用户对话中提取
- 提取结果必须**保留原文**，禁止自行改写或概括

**输出**：各层级结构化摘要（JSON 或 key-value 格式）

#### 步骤 3：建立教学逻辑链，推导本节课内容

基于步骤 2 的提取结果，按以下逻辑链推导：

```
L1 培养目标
  → 支撑本课程的毕业要求指标点
    → L2 课程目标（知识/能力/素质）
      → L3 本周教学内容范围 + 目的要求
        → 推导出本节课的：
            ├─ 课题名称（topic）
            ├─ 教学目标（知识点 + 能力点 + 素质点）
            ├─ 教学重难点（keyDifficult）
            ├─ 教学内容范围（contentAnalysis）
            ├─ 课程思政主题（从 L3 目的要求提取）
            └─ 课程进度上下文（curriculum_context：前序内容 → 本周 → 后续内容）
```

**推导规则**：
- **课题名称**：从 L3 本周教学内容中提取（去掉"复习"前缀后的核心主题）
- **三维目标**：L2 课程目标 → 结合 L3 本周目的要求 → 细化为本节课可衡量的具体目标
- **教学重难点**：从 L3 目的要求中的关键词推导（"掌握"→重点、"难点/易错"→难点）
- **教学内容分析**：L3 本周内容摘要 → 结合 L2 教学内容范围 → 描述本节课在整个课程中的位置和作用
- **学情分析**：L2 授课对象信息 + 当前周次（前序内容决定了学生的已有基础）
- **课程进度上下文**：从 L3 教学计划中提取「前几周学了什么 → 本周学什么 → 下周学什么」
- **课程思政主题**：从 L3 目的要求中**原文提取**，禁止自行编造

**降级模式**（无上游文档时）：
- 由用户直接提供课题名称、教学目标、重难点、教学内容等
- 课程进度上下文为空字符串（策略生成降级但不崩溃）
- 后续步骤不变

**输出**：推导结果摘要（课题/目标/重难点/内容分析/思政主题/课程进度）

#### 步骤 4：向用户确认推导结果

将步骤 3 的推导结果展示给用户确认：

```
推导结果确认：
  课题名称：XXX
  授课对象：XXX
  课时：90分钟
  教学目标：
    - 知识点：...
    - 能力点：...
    - 素质点：...
  教学重难点：...
  教学内容范围：...
  课程思政主题：...
  课程进度：前序(第N周:xxx) → 本周(第M周:xxx) → 后续(第P周:xxx)

请确认以上内容是否准确，如有需要修改的部分请指出。
```

- 用户确认后进入阶段 B
- 用户要求修改时，回到步骤 2-3 重新提取/推导
- **批量生成模式跳过此步骤**（已有校验脚本保障）

---

### 阶段 B：教案内容构建

#### 步骤 5：补全教案各字段

基于阶段 A 的推导结果（或降级模式的用户提供信息），补全 LESSON_DATA 所有字段。

**字段来源映射**：

| 字段 | 来源 |
|------|------|
| `title` | 自动生成：`{courseModule}模块{lessonSeq圈标}教案{lessonSeq中文}`（如"武术模块①教案一"），也可手动覆盖 |
| `courseName` | L2 课程名称 |
| `courseModule` | L2 教学内容模块（如"武术""篮球"） |
| `lessonSeq` | 模块内第几课时（数字，默认 1），L3 授课计划中推导 |
| `courseCategory` | L2 课程类别 |
| `target` | L2 授课对象 |
| `time` | L3 周次/日期 |
| `location` | 用户指定 |
| `format` | 授课形式 |
| `hours` | 默认 90 分钟 |
| `equipment` | 用户指定或根据运动项目推断 |
| `topic` | 步骤 3 推导 |
| `contentAnalysis` | 步骤 3 推导（结合 L2+L3） |
| `studentAnalysis` | 步骤 3 推导（基于学情） |
| `knowledgePoints` | 步骤 3 三维目标 - 知识 |
| `abilityPoints` | 步骤 3 三维目标 - 能力 |
| `qualityPoints` | 步骤 3 三维目标 - 素质 |
| `keyDifficult` | 步骤 3 推导 |
| `topic` | 步骤 3 推导 |
| `methodMeans` | L2 教学方法建议 + 用户补充 |
| 教学过程 `prepare/basic/ending` | 根据课题内容设计（需用户确认或提供） |
| `exerciseDensity` / `avgHeartRate` | 根据运动强度推断或用户指定 |
| `teachingEval` / `homework` | 根据教学目标设计 |


> **完整字段 schema** 见 [01-data-schema.md](01-data-schema.md)

**执行规则**：
- 阶段 A 已推导的字段直接使用
- 教学过程（prepare/basic/ending）需要根据课题内容具体设计——如果用户未提供，向用户询问或基于教学设计（L4）推断
- 缺失且无法推导的字段留空字符串或 null，**禁止编造**

**输出**：完整的 LESSON_DATA 字典（除自动生成字段和图片字段外）

#### 步骤 6：偏好确认

使用 `ask_user_question` 工具**一次性询问**以下三项偏好：

**问题 1**：「请选择教案表格配色方案」

- 淡灰（默认）/ 淡蓝 / 淡绿

**问题 2**：「队列队形图使用什么方式生成？」
- AI 生图（推荐）/ PIL 程序化绘制 / 跳过队形图

**问题 3**：「队形图标注文字使用什么语言？」（仅 AI 生图模式下生效）
- 中文（推荐）/ 英文

**规则**：
- 三项问题在同一个 `ask_user_question` 调用中提出（`multiSelect: false`）
- 若用户选择「AI 生图」但当前环境无 `generate_image` 工具，自动 fallback 到 PIL
- 若用户未指定，配色默认 `default`，队形图默认 AI 生图，标注语言默认中文
- 同一会话内后续教案复用已选方案，不再重复询问

**输出**：`colorTheme` + 队形图方式 + `label_lang`

---

### 阶段 C：自动生成（Agent 自主执行）

> 需要读取 [03-auto-generation.md](03-auto-generation.md) 获取详细生成逻辑。

#### 步骤 7：生成教学策略文本

- 收集 7 个变量：课程性质、教学内容、授课对象、课时类型、教学目标、重点难点、**课程进度上下文**（从阶段 A 步骤 3 获取）
- 调用 `scripts/strategy_prompt.md` 生成精简三段式策略文本（200-300 字）
- 按质量自检清单核对（结构完整/纵向衔接/理论依据/无顿号）

#### 步骤 8：生成教学策略图（仅 AI 生图）

- 调用 `strategy_ai_generator.get_strategy_ai_prompt(curriculum_context=..., label_lang=...)` → `generate_image`（2:3）
- AI 生图失败时 `strategyImg` 留空

#### 步骤 9：生成教学流程图（仅 AI 生图，禁止硬编码模板）

- 调用 `flowchart_ai_generator.get_flowchart_ai_prompt(flowchart_text=..., lesson_data=..., label_lang=...)`
- `flowchart_text` 和 `lesson_data` 必须从教案实际内容传入
- 返回空 prompt 时留空，**禁止用通用模板替代**

#### 步骤 10：生成教学反思

- 调用 `scripts/reflection_prompt.md`，按三段式结构生成
- **课程思政部分必须引用阶段 A 步骤 3 提取的思政主题原文**

**输出**：`strategy` + `strategyImg` + `flowChartImg` + `reflection`

**输出**：`strategy` + `strategyImg` + `flowChartImg` + `reflection`

### 阶段 D：图片素材准备（Agent 自主执行）

> 需要读取 [02-image-spec.md](02-image-spec.md) 和 [06-formation-action.md](06-formation-action.md)。
> **所有图片提示词必须从教案实际内容提取，禁止凭空捏造。**

#### 步骤 11：生成图片素材

按图片规范使用 AI 生图生成：

| 图片 | 数据源 | 失败处理 |
|------|--------|---------|
| **课前图** | `preClass` 字段实际内容 | 留空 |
| **动作图** | 各 `basic[].content` 具体教学内容，每环节独立生成 | 留空；非动作环节不生成 |
| **预计生理负荷图** | `exerciseDensity`/`avgHeartRate`/教学过程时间强度 | 留空 |
| **队形图** | `sport`/`phase`/`org_method`/`n_students` | AI→PIL→占位符→留空 |

**输出**：所有图片路径填入 LESSON_DATA 对应字段

---

### 阶段 E：预览确认与渲染交付

#### 步骤 12：生成前预览确认

向用户汇总展示：
- 课题名称 + 授课对象 + 课时
- 教学策略摘要（前 50 字）
- 图片生成情况（策略图✓/✗、流程图✓/✗、队形图✓/✗、动作图✓/✗）
- 配色方案

用户选择「确认生成」后继续；要求修改时回到对应阶段。

**批量生成模式自动跳过此步骤。**

#### 步骤 13：将 `colorTheme` 写入 LESSON_DATA，JSON 构建校验

- `assert '、' not in json.dumps(data, ensure_ascii=False)`
- 确认所有必填字段非空

#### 步骤 14：渲染 .docx

- 通过 `run_node_docx` 执行 `scripts/blank_template.js` 生成 .docx
> 需要读取 [05-template-structure.md](05-template-structure.md) 了解模板细节。

#### 步骤 15：交付文档

告知用户文件路径，如需更换配色可重新生成。

---

### 生成教案步骤速查

| 步骤 | 阶段 | 内容 | 需要读取 |
|:----:|:----:|------|---------|
| 1 | A | 收集上游文档 | — |
| 2 | A | 逐层提取信息 | — |
| 3 | A | 逻辑链推导 | — |
| 4 | A | 确认推导结果 | — |
| 5 | B | 补全教案字段 | [01-data-schema.md](01-data-schema.md) |
| 6 | B | 偏好确认 | — |
| 7 | C | 教学策略文本 | [03-auto-generation.md](03-auto-generation.md) |
| 8 | C | 教学策略图 | [03-auto-generation.md](03-auto-generation.md) |
| 9 | C | 教学流程图 | [03-auto-generation.md](03-auto-generation.md) |
| 10 | C | 教学反思 | [03-auto-generation.md](03-auto-generation.md) |
| 11 | D | 图片素材 | [02-image-spec.md](02-image-spec.md), [06-formation-action.md](06-formation-action.md) |
| 12 | E | 预览确认 | — |
| 13 | E | JSON 校验 | [01-data-schema.md](01-data-schema.md) |
| 14 | E | 渲染 .docx | [05-template-structure.md](05-template-structure.md) |
| 15 | E | 交付 | — |

---

## 批量生成教案（基于授课计划）

> 批量模式以 **L3 授课计划** 为核心文档，L1/L2 为辅助（提供课程目标和思政主题来源）。
> 批量模式的阶段 A 简化为「提取授课计划结构化数据」，阶段 B-E 逐周执行。

### 前置步骤：提取授课计划结构化数据

生成任何教案之前，先将授课计划文档解析为结构化数据表，**逐周提取以下列原文**：

| 列名 | 提取内容 | 用途 |
|------|---------|------|
| 周次 | 第N周 | → `time` 字段 |
| 教学阶段 | 基础/单练/对练/理论/考核 | → 课程进度上下文 |
| 内容摘要 | 当周全部教学内容（含复习项） | → `topic` / `contentAnalysis` / `basic[].content` |
| 目的要求 | 教学目标 + 课程思政主题 + 量化指标 | → 各分析字段 / `reflection` 思政部分 |
| 教学方式 | 教学方法组合 | → `methodMeans` |

**提取方法**：用 `python-docx` 读取表格。合并单元格会导致重复，用 `list(dict.fromkeys(cells))` 去重。

```python
from docx import Document
doc = Document('授课计划.docx')
for table in doc.tables:
    header = [cell.text.strip() for cell in table.rows[0].cells]
    for row in table.rows[1:]:
        cells = list(dict.fromkeys([c.text.strip() for c in row.cells]))
        week = cells[0]
        stage = cells[1]
        content_summary = cells[2]
        objectives = cells[3]
        methods = cells[4] if len(cells) > 4 else ""
```

### 逐周构建 LESSON_DATA 的强制规则

**规则1：新授内容完整覆盖**

- 授课计划「内容摘要」用分号分隔的多项内容 → 全部出现在教案中，**不得遗漏**
- 校验：将内容摘要拆分为列表，逐项检查是否出现在 `topic` + `contentAnalysis` + `basic[].content` 的并集中

**规则2：复习内容显式对应**

- 「内容摘要」开头的「复习xxx」→ 必须在 `contentAnalysis` 或 `basic` 中**显式标注**

**规则3：课程思政主题严格对齐**

- 「目的要求」中的思政主题 → `reflection` 或 `strategy` 或 `ending.content` 中**引用原文**

**规则4：量化指标引用**

- 「目的要求」中的百分比掌握率 → 体现在 `teachingEval` 中

### 每周教案生成后的自动校验

```python
# --- 辅助函数 ---
import re

def split_content_items(summary):
    """将内容摘要按分号/逗号拆分，去掉「复习xxx」前缀"""
    items = re.split(r'[；;，,]', summary)
    return [re.sub(r'^复习[^：:]*[：:;；]?', '', item).strip() for item in items if item.strip()]

def extract_keywords(text):
    return [w for w in re.findall(r'[\u4e00-\u9fff]{2,}', text)]

def extract_review_prefix(summary):
    m = re.match(r'^(复习[^；;，,]+)', summary)
    return m.group(1).strip() if m else ""

def extract_sz_keywords(objectives):
    patterns = r'(文化自信|吃苦耐劳|红军|止戈为武|工匠精神|开国元勋|气力意|民族团结|爱国主义|集体主义|拼搏|坚韧|团结|纪律|尊师|武德)'
    return re.findall(patterns, objectives)

# --- 校验 ---
lesson_text = (contentAnalysis + " " +
               " ".join([b["content"] for b in basic]) + " " +
               reflection + " " + strategy + " " +
               ending["content"])

# 检查1: 新授内容完整覆盖
content_items = split_content_items(plan_week["内容摘要"])
missing = [item for item in content_items
           if not any(kw in lesson_text for kw in extract_keywords(item))]
assert len(missing) == 0, f"新授内容遗漏: {missing}"

# 检查2: 复习内容显式对应
review_part = extract_review_prefix(plan_week["内容摘要"])
if review_part:
    assert any(kw in lesson_text for kw in extract_keywords(review_part)), \
        f"复习内容缺失: {review_part}"

# 检查3: 课程思政主题对齐
sz_keywords = extract_sz_keywords(plan_week["目的要求"])
for kw in sz_keywords:
    assert kw in lesson_text, f"思政主题缺失: {kw}"
```

校验失败时**禁止继续生成下一周教案**。

### 已知偏差模式与防错机制

> 实战教训：武术模块16周教案批量生成中，教案5-13共发现三类系统性偏差（9处问题）。

| 偏差模式 | 表现 | 根因 | 防错 |
|---------|------|------|------|
| A: 内容遗漏 | 授课计划多项并列内容只取了"主要项" | 凭记忆选取，未逐条对照原文 | 拆分后逐项匹配 |
| B: 复习缺失 | 授课计划写"复习xxx"但教案未标注 | 认为理所应当而省略 | 显式写入 basic[0] |
| C: 思政偏移 | 授课计划指定思政主题但教案自行编写 | 自行推理，未提取原文 | 原文提取+校验 |
| D: 指标遗漏 | 掌握率要求未引用 | 忽略量化指标 | teachingEval 中引用 |
| E: 跨session延续 | 前一个session的偏差延续到后续session | 未系统修正+未复用规则 | 每次严格按规则执行 |

### 批量生成节奏

- 默认每次生成 3 个教案
- 每个教案生成后立即校验
- 一轮完成后向用户报告进度，确认后再开始下一轮

---

## 完善教案

> 用户已有部分教案信息（上传文件或对话描述），补全缺失部分。

1. 读取用户提供的信息
2. 识别已有信息和缺失信息
3. 如有上游文档（教学大纲/授课计划等），尝试从上游文档推导缺失内容（参考阶段 A 步骤 2-3 的逻辑）
4. 如仍有缺失，向用户确认或基于上下文合理补充
5. 偏好确认（如同一会话内已有记录则跳过，见步骤 6）
6. 按图片规范准备图片素材（参考阶段 D 步骤 11）
7. 自动生成"教学分析"区缺失字段（参考阶段 C 步骤 7-10）
8. 按阶段 E 流程预览确认 → 渲染 .docx → 交付

---

## LESSON_DATA JSON 构建规范

构建 JSON 字符串时必须遵守：

1. **禁止中文顿号**：所有「、」替换为分号或逗号
2. **禁止未转义换行**：多行文本用 `\n` 而非实际换行符
3. 生成前执行断言：
   ```python
   assert '\u3001' not in json.dumps(data, ensure_ascii=False)
   assert '\n' not in json.dumps(data, ensure_ascii=False)
   ```
