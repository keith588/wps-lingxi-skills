# 社科概念库分类体系

概念库位置：`{CONCEPTS_PATH}`

先用 `ls {CONCEPTS_PATH}` 查看已有子目录，再按下表分类：

| 子目录 | 归类标准 | 示例 |
|--------|----------|------|
| `1-理论框架` | 有明确提出者、有核心主张、被多篇论文引用的理论 | Self-Determination Theory, Uses and Gratifications Theory, Social Comparison Theory, Theory of Planned Behavior |
| `2-核心构念` | 可操作化测量的心理或社会构念，通常作为IV/DV/中介/调节 | FoMO, Self-Esteem, Social Media Addiction, Academic Burnout, Well-Being |
| `3-测量工具` | 有发表的信效度检验、被多项研究使用的标准化量表 | FoMOs (Przybylski 2013), BSMAS, RSES, PHQ-9, MBI |
| `4-研究方法` | 研究设计、统计技术、数据分析方法 | SEM, Mediation Analysis, Meta-Analysis, Longitudinal Design, ESM |
| `5-统计概念` | 统计指标、效应量、模型拟合指标 | Cronbach's Alpha, Effect Size, CFI, RMSEA, Bootstrap, Cohen's d |
| `6-人群与场景` | 特定研究人群、文化背景、社会情境 | University Students, Adolescents, Generation Z, East Asian Culture |
| `0-待分类` | **仅在完全无法判断时**才用，应尽量避免 | — |

---

## 1-理论框架

心理学、传播学、教育学、社会学、管理学等学科的理论框架和模型。

**收录标准**：有明确提出者、有核心主张、被多篇论文引用的理论。

**笔记模板**：

```markdown
---
type: theory
domain: "{心理学/传播学/教育学/社会学/管理学}"
proposer: "{提出者}"
year: {首次提出年份}
aliases: [{中文别名}, {英文缩写}]
tags: [概念库, 理论]
---

# {Theory Name}（{中文名}）

## 定义
{该理论的核心定义，2-3句话}

## 核心命题
1. {命题1}
2. {命题2}
3. {命题3}

## 关键构念
- **{构念1}**: {定义}
- **{构念2}**: {定义}
- **{构念3}**: {定义}

## 代表性研究
- {原始文献引用}
- {重要综述/元分析引用}

## 相关理论
- [[{Related Theory 1}]] — {关系说明}
- [[{Related Theory 2}]] — {关系说明}

## 引用本理论的论文
- [[{FirstAuthor1}{Year}]]
- [[{FirstAuthor2}{Year}]]
```

**常见示例**：
- Self-Determination Theory（自我决定理论）
- Uses and Gratifications Theory（使用与满足理论）
- Social Comparison Theory（社会比较理论）
- Theory of Planned Behavior（计划行为理论）
- Compensatory Internet Use Theory（补偿性网络使用理论）
- Cognitive-Behavioral Model（认知行为模型）
- Social Learning Theory（社会学习理论）
- Attachment Theory（依恋理论）

---

## 2-核心构念

可操作化测量的心理或社会构念，通常作为研究中的自变量、因变量或中介/调节变量。

**收录标准**：有操作性定义、有成熟量表、在多篇论文中被测量的构念。

**笔记模板**：

```markdown
---
type: construct
domain: "{心理学/传播学/教育学}"
first_defined_by: "{首次定义者}"
year: {首次定义年份}
aliases: [{中文别名}, {英文缩写}]
tags: [概念库, 构念]
---

# {Construct Name}（{中文名}）

## 定义
{该构念的标准学术定义，注明来源}

## 测量
| 量表 | 作者 | 条目数 | 适用人群 |
|------|------|--------|----------|
| [[{Scale 1}]] | {Author, Year} | {N} | {人群} |

## 前因变量
- [[{Antecedent 1}]] — {关系方向和典型效应量}
- [[{Antecedent 2}]] — {关系方向和典型效应量}

## 结果变量
- [[{Outcome 1}]] — {关系方向和典型效应量}
- [[{Outcome 2}]] — {关系方向和典型效应量}

## 相关构念
- [[{Construct 1}]] — {区别/联系}
- [[{Construct 2}]] — {区别/联系}

## 引用本构念的论文
- [[{FirstAuthor1}{Year}]]
```

**常见示例**：
- Fear of Missing Out / FoMO（错失恐惧）
- Self-Esteem（自尊）
- Social Media Addiction（社交媒体成瘾）
- Academic Burnout（学业倦怠）
- Psychological Well-Being（心理幸福感）
- Self-Regulation（自我调节）
- Loneliness（孤独感）
- Life Satisfaction（生活满意度）

---

## 3-测量工具

标准化的心理测量工具、问卷量表。

**收录标准**：有发表的信效度检验、被多项研究使用的标准化量表。

**笔记模板**：

```markdown
---
type: instrument
measures: "[[{对应构念}]]"
original_author: "{原作者}"
year: {开发年份}
aliases: [{缩写}, {中文名}]
tags: [概念库, 量表]
---

# {Scale Full Name}（{缩写}）

## 基本信息
- **测量构念**: [[{Construct}]]
- **开发者**: {Author, Year}
- **维度**: {维度结构描述}
- **条目数**: {原始版本条目数}
- **信度范围**: α = {最低值} ~ {最高值}（跨研究）

## 效度证据
- **内容效度**: {证据}
- **结构效度**: CFA: CFI = {值}, RMSEA = {值}
- **效标效度**: 与 [[{相关构念}]] 的相关 r = {值}

## 相关构念
- [[{Construct 1}]] — {关系}
- [[{Construct 2}]] — {关系}

## 使用本量表的论文
- [[{FirstAuthor1}{Year}]]
```

**常见示例**：
- Fear of Missing Out Scale / FoMOs（Przybylski et al., 2013）
- Bergen Social Media Addiction Scale / BSMAS
- Rosenberg Self-Esteem Scale / RSES
- Patient Health Questionnaire / PHQ-9
- Maslach Burnout Inventory / MBI
- Big Five Inventory / BFI
- Satisfaction with Life Scale / SWLS

---

## 4-研究方法

研究方法、研究设计范式、数据分析策略。

**收录标准**：有明确方法论来源、在社科研究中被广泛使用的方法或技术。

**笔记模板**：

```markdown
---
type: method
category: "{研究设计/统计方法/数据收集/抽样方法}"
aliases: [{中文名}, {缩写}]
tags: [概念库, 方法]
---

# {Method Name}（{中文名}）

## 定义
{方法的定义，1-2句}

## 适用场景
- {场景1}
- {场景2}

## 关键步骤
1. {步骤1}
2. {步骤2}
3. {步骤3}

## 前提假设
- {假设1}
- {假设2}

## 优势与局限
### 优势
- {优势1}
- {优势2}

### 局限
- {局限1}
- {局限2}

## 使用本方法的论文
- [[{FirstAuthor1}{Year}]]
```

**常见示例**：
- Structural Equation Modeling / SEM（结构方程模型）
- Mediation Analysis（中介分析）
- Meta-Analysis（元分析）
- Longitudinal Design（纵向设计）
- Experience Sampling Method / ESM（经验取样法）
- Thematic Analysis（主题分析）
- Multilevel Modeling / HLM（多层线性模型）
- PROCESS Macro（PROCESS 宏）

---

## 5-统计概念

统计指标、效应量、模型拟合指标、统计检验方法。

**收录标准**：在社科定量研究中频繁出现、需要准确理解的统计概念。

**笔记模板**：

```markdown
---
type: statistic
category: "{效应量/拟合指标/检验方法/描述统计}"
aliases: [{中文名}, {符号}]
tags: [概念库, 统计]
---

# {Concept Name}（{中文名}）

## 定义
{统计概念的定义}

## 公式（如适用）
$$
{公式}
$$

## 解释方法
{如何解读该指标的含义}

## 常用阈值
| 水平 | 阈值 | 含义 |
|------|------|------|
| {水平1} | {值} | {含义} |
| {水平2} | {值} | {含义} |

## 相关概念
- [[{Related Concept 1}]] — {关系}
- [[{Related Concept 2}]] — {关系}

## 引用本概念的论文
- [[{FirstAuthor1}{Year}]]
```

**常见示例**：
- Cronbach's Alpha（克伦巴赫信度系数）
- Cohen's d（科恩 d 值）
- Effect Size（效应量）
- CFI / Comparative Fit Index（比较拟合指数）
- RMSEA（近似误差均方根）
- Bootstrap（自举法）
- Harman's Single Factor Test（哈曼单因素检验）
- Variance Inflation Factor / VIF（方差膨胀因子）

---

## 6-人群与场景

特定的研究人群、文化背景、社会情境。

**收录标准**：作为研究对象被反复关注的特定群体或情境，有独特的研究发现。

**笔记模板**：

```markdown
---
type: population
category: "{人群/文化/情境}"
aliases: [{中文名}]
tags: [概念库, 群体]
---

# {Population/Context Name}（{中文名}）

## 定义
{该群体/情境的定义和范围}

## 特征
- **人口学特征**: {年龄、教育、地域等}
- **关键特点**: {与研究主题相关的独特特征}

## 常见研究议题
- {该群体被关注的主要议题1}
- {该群体被关注的主要议题2}

## 抽样注意事项
- {研究该群体时的抽样和方法学注意事项}
- {伦理考虑}

## 相关群体
- [[{Related Population}]] — {比较说明}

## 研究该群体的论文
- [[{FirstAuthor1}{Year}]]
```

**常见示例**：
- University Students（大学生群体）
- Adolescents（青少年群体）
- Generation Z（Z世代）
- East Asian Collectivistic Culture（东亚集体主义文化）
- International Students（国际留学生）
- Early-Career Researchers（青年学者/青椒）
- K-12 Teachers（中小学教师）

---

## 维护规则

1. **新增概念**：读论文时遇到新概念，判断归入哪个分类，按模板创建文件
2. **更新概念**：已有概念被新论文引用时，在「引用本XX的论文」列表追加 `[[wikilink]]`
3. **合并概念**：发现同一概念有多个名称时，保留最通用的名称，其余设为 aliases
4. **概念关联**：在相关字段中使用 `[[wikilink]]` 实现概念间双向链接
5. **质量标准**：每个概念至少有定义 + 1篇引用论文才算有效条目
