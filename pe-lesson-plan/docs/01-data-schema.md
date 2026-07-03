# LESSON_DATA 数据格式

> 本文档定义教案数据的完整 JSON schema。
> 所有字段均通过环境变量 `LESSON_DATA` 传入 `blank_template.js`。

## 数据格式

教案数据通过环境变量 `LESSON_DATA` 传入 JSON 字符串，字段如下：

### 配色主题

| 字段 | 说明 |
|------|------|
| `colorTheme` | 可选，配色主题标识（`default` / `ocean` / `forest`） |

| 主题 | 标识 | 标签底色 | 表头底色 | 视觉风格 |
|------|------|---------|---------|---------|
| 淡灰（默认） | `default` | `#F0F0F0` | `#E0E0E0` | 沉稳素雅，适合日常教学 |
| 淡蓝 | `ocean` | `#E8F0FE` | `#D2E3FC` | 清爽明亮，适合球类/水上项目 |
| 淡绿 | `forest` | `#E6F4EA` | `#CEEAD6` | 活力自然，适合田径/户外项目 |

### 基本信息（6组标签-值对）

| 字段 | 说明 |
|------|------|
| `title` | 教案标题，默认"体育课教案" |
| `courseName` | 课程名称 |
| `courseModule` | 课程模块 |
| `courseCategory` | 课程类别 |
| `target` | 授课对象 |
| `time` | 授课时间 |
| `location` | 授课地点 |
| `format` | 授课形式 |
| `hours` | 课时（用户未指定时默认 **90 分钟**） |
| `equipment` | 场地器材 |

### 教学分析（长文本字段）

| 字段 | 说明 |
|------|------|
| `topic` | 课题名称 |
| `contentAnalysis` | 教学内容分析 |
| `studentAnalysis` | 学情分析 |
| `knowledgePoints` | 知识点 |
| `abilityPoints` | 能力点 |
| `qualityPoints` | 素质点 |
| `keyDifficult` | 教学重、难点 |
| `strategy` | 教学策略（自动生成） |
| `strategyImg` | 教学策略图示图片路径（仅 AI 生图）<br>渲染时策略文字与图片拆为独立两行：文字行自适应高度，图片行 `trHeight=10200 DXA, hRule=exact`<br>无图时不生成图片行，不会留空白 |
| `flowChart` | 教学流程图（文字描述） |
| `flowChartImg` | 教学流程图图片路径（可选，宽度 470px） |
| `preClass` | 课前（文字描述） |
| `preClassImg` | 课前图片路径（可选，宽度 470px） |
| `methodMeans` | 教学方法与手段 |

### 教学过程（结构化对象）

教学过程分为三个部分，每部分为 `{content, orgMethod, time}` 对象：

- `prepare`: 准备部分（单个对象）
- `basic`: 基本部分（对象数组，支持多行）
- `ending`: 结束部分（单个对象）

每个对象字段：
- `content`: 教学内容（支持 `\n` 换行）
- `orgMethod`: 组织教法与要求
- `time`: 时间分配

基本部分每个对象额外支持：
- `contentImg`: 动作图路径（可选，嵌入教学内容列，宽度 222px）
- `orgImg`: 队形图路径（可选，嵌入组织教法列，宽度 249px）

准备部分和结束部分通过顶层字段传入图片：
- `prepareOrgImg`: 准备部分队形图路径（可选，宽度 249px）
- `endingOrgImg`: 结束部分队形图路径（可选，宽度 249px）

### 评价与反思

| 字段 | 说明 |
|------|------|
| `teachingEval` | 教学评价 |
| `exerciseDensity` | 练习密度 |
| `avgHeartRate` | 平均心率 |
| `homework` | 课后作业 |
| `reflection` | 教学反思（自动生成，支持 Markdown 渲染） |
| `heartRateImg` | 预计生理负荷心率曲线图片路径（可选，800×480） |

