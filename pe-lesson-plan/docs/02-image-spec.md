# 图片规范

> 本文档定义教案中所有图片的尺寸、风格、占位符机制、生成策略。
> **核心原则：所有图片提示词必须从教案实际内容提取参数，禁止凭空捏造。**

## 图片规范

### 图片位置与尺寸

**核心原则：图片必须严格匹配单元格大小，避免超出或过小。**

教案表格的列宽分布（DXA，1 英寸 = 1440 DXA）：

| 列 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|----|----|----|----|----|----|----|----|----|
| 宽(DXA) | 495 | 959 | 1641 | 895 | **347** | **1047** | 1304 | 1201 | 811 |
| 宽(英寸) | 0.34 | 0.67 | 1.14 | 0.62 | 0.24 | 0.73 | 0.91 | 0.83 | 0.56 |

**列宽调整说明**：
- **col 5 (W[4])**：260 → 347 DXA（+33.5%，即"加宽 1/3"），"预计生理负荷"标签 cell 用
- **col 6 (W[5])**：1134 → 1047 DXA（保持 W[4]+W[5] 总和 = 1394 DXA 不变）
- col 1 (W[0])、col 2 (W[1]) 保持原值（495 + 959 = 1454 DXA），仅在"教学评价" cell 中以竖排显示 4 个汉字

各图片对应单元格内容区宽度：

| 图片类型 | 所在区域 | 所在列 | 物理尺寸 | 输出像素(参考) | 生成方式 |
|---------|---------|--------|---------|---------------|---------|
| **教学策略图** | 分析区"教学策略"行 | col 2-8 | **5.0 × 10.0 英寸（纵向，exact 14400 DXA 行高，拉满整页）** | 2:3 宽高比 | **仅 AI 生图**，失败时留空不用占位图 |
| **教学流程图** | 分析区"教学流程图"行 | col 2-8 | **5.0 × 5.5 英寸（纵向，atLeast 行高）** | 1000 × 1100 | **仅 AI 生图**（`flowchart_ai_generator.py` v2.0 动态3~9任务），失败时留空不用占位图 |
| **课前图片** | 分析区"课前"行 | col 2-8 | 5.0 × 2.8 英寸 | 1000 × 560 | **仅 AI 生图**，失败时留空不用占位图 |
| **动作图** | 基本部分 → 教学内容列 | col 1-3 | 2.15 × 1.1 英寸 | 430 × 220 | **仅 AI 生图**，每张图对应具体动作教学内容细节，无图时留空不用占位图 |
| **队形图** | 教学过程 → 组织教法列 | col 4-7 | 2.55 × 2.1 英寸 | 510 × 420 | **A→B→C 三级 fallback**（详见[队形图生成策略](#队形图生成策略v41-ai优先pil-fallback)）|
| **生理负荷图（预计心率曲线）** | 预计生理负荷区 | **标签 col 5 / 图片 col 6-8** | 标签 0.24" / 图片 2.27" | **800 × 480** | **仅 AI 生图**，失败时留空不用占位图 |

**注意**：
- "预计生理负荷"标签 cell 跨 1 列（col 5 = 347 DXA = 0.24"），加宽原列宽 1/3（260 → 347 DXA），6 个汉字竖排
- 图片 cell 跨 3 列（col 6-8 = 3276 DXA = 2.27"），maxWidth 减 40 DXA 边距 = 215 px @ 96 DPI
- 800×480 源图缩到 215×129 px 仍清晰（高 DPI 源图补偿）

**教学策略图尺寸说明（v3.5/v3.6 纵向布局）**：
- 单元格内容区总宽：7394 DXA ≈ 5.13 英寸
- 留 0.13 英寸边距 → 默认 **5.0 英寸宽**
- 受宽度限制改为**纵向布局**，高度 5.5 英寸（向上延伸）
- **默认 DPI = 200**（高清源文件 ~1000×1100 像素）
  - 配合模板中 `imgPara` 的 DXA→像素单位转换，缩放后精确匹配单元格不溢出
- **布局结构（自上而下）**：
  - 顶部标题区（11%）→ 准备部分方框 → 衔接箭头 → 基本部分方框 → 衔接箭头 → 结束部分方框 → 底部双栏（项目特异性+三维目标）
- **字号方案（与 Word 教案正文 10.5pt 一致）**：
  - 标题 14pt / 副标 10.5pt / 阶段名 13pt / 阶段策略 12pt / **阶段详情 10.5pt** / 标签 11pt / 脚注 9pt
- 紧凑模式可缩为 5.0 × 4.8 英寸

### 图片风格要求

- **统一色调**：动作图、队形图、生理负荷图、流程图、课前图均使用黑白灰色调（#333/#666/#999/#DDD）
- **唯一例外**：教学策略图支持彩色，便于呈现"准备/基本/结束"三段并列与项目特异性的视觉层次
- **动作图**：火柴人/简笔画风格的动作分解图
- **队形图**：方案 A（AI 生图）为彩色教育插图风格；方案 B（PIL）为卡通人形剪影（圆形头部+躯干+四肢+手部圆点），学生深蓝、教师红色+"教师"标签，按项目差异化场地
- **生理负荷图（V2 增强版）**：白边黑点+三色强度分区（低/中/高）+ 平滑曲线+峰谷标记+平均心率虚线（详见 [V2 增强版](#v2-增强版)）
- **教学策略图**：模块化设计，五大区块（标题/三段策略/项目特异/目标/页脚）

### 占位符机制

当无法生成实际图片或图片不匹配运动项目时，使用占位符图片代替。占位符风格统一：白底 + 圆角灰色边框 + 居中文字标注。

**通用占位符**（位于 `scripts/images/`）：

| 文件 | 用途 | 尺寸 |
|------|------|------|
| `placeholder_action.png` | 动作图通用（fallback）| 222px 宽 |
| `placeholder_action_basketball.png` | 动作图-篮球 | 222px 宽 |
| `placeholder_action_volleyball.png` | 动作图-排球 | 222px 宽 |
| `placeholder_action_football.png` | 动作图-足球 | 222px 宽 |
| `placeholder_action_athletics.png` | 动作图-田径 | 222px 宽 |
| `placeholder_action_martial.png` | 动作图-武术 | 222px 宽 |
| `placeholder_action_gym.png` | 动作图-体操 | 222px 宽 |
| `placeholder_formation.png` | 队形图通用 | 249px 宽 |
| `placeholder_heart.png` | 心率曲线 | 800×480 |
| `placeholder_flowchart.png` | 教学流程图 | **5.0×5.5 英寸，纵向（1000×1100 px）** |
| `placeholder_preclass.png` | 课前图 | **5.0×2.8 英寸（1000×560 px）** |
| `placeholder_strategy.png` | 教学策略图（仅 AI 生图失败时留空，不再使用占位符） | 2:3 宽高比 |

**项目专属占位符**（v4.0+，51 张 = 9 项目 × 多阶段，命名规则 `formation_<sport>_<pos>.png`，卡通人形剪影风格）：

| 项目 | prepare | basic_1 | basic_2 | basic_3 | ending |
|------|---------|---------|---------|---------|--------|
| 篮球 | `formation_basketball_prepare.png` | `formation_basketball_basic_1.png` | `formation_basketball_basic_2.png` | `formation_basketball_basic_3.png` | `formation_basketball_ending.png` |
| 排球 | `formation_volleyball_prepare.png` | `formation_volleyball_2v2.png` | `formation_volleyball_2v2.png` | `formation_volleyball_circle.png` | `formation_volleyball_relax.png` |
| 足球 | `formation_football_prepare.png` | `formation_football_4v4.png` | `formation_football_4v4.png` | `formation_football_basic_3.png` | `formation_football_ending.png` |
| 田径 | `formation_athletics_prepare.png` | `formation_athletics_start.png` | `formation_athletics_start.png` | `formation_athletics_basic_3.png` | `formation_athletics_ending.png` |
| 武术 | `formation_martial_prepare.png` | `formation_martial_duilian.png` | `formation_martial_duilian.png` | `formation_martial_duilian.png` | `formation_martial_ending.png` |
| 体操 | `formation_gym_prepare.png` | `formation_gym_groups.png` | `formation_gym_groups.png` | `formation_gym_groups.png` | `formation_gym_ending.png` |
| 通用 | `formation_general_prepare.png` | `formation_general_basic_1.png` | `formation_general_basic_2.png` | `formation_general_basic_3.png` | `formation_general_ending.png` |

动作图项目占位符 key（v3.6.3 已批量补齐，写实彩色 + 3 步分解 + 中文标签，430×220 像素）：

| sport | 文件 | 大小 | 代表动作 |
|-------|------|------|---------|
| `basketball` | `placeholder_action_basketball.png` | 159.2 KB | 行进间上篮（半场+三分线+篮筐+红色轨迹）|
| `volleyball` | `placeholder_action_volleyball.png` | 154.9 KB | 正面双手垫球（排球场地+球网+来球轨迹）|
| `football` | `placeholder_action_football.png` | 179.5 KB | 脚弓传球（绿茵场+白色分道线+传球轨迹）|
| `athletics` | `placeholder_action_athletics.png` | 168.5 KB | 蹲踞式起跑（红色跑道+起跑器+蹬离轨迹）|
| `martial` | `placeholder_action_martial.png` | 138.1 KB | 弓步冲拳（木地板训练场+三步动作）|
| `gym` | `placeholder_action_gym.png` | 155.5 KB | 前滚翻准备（蓝色体操垫+团身/蹬地）|
| `general` | `placeholder_action.png` | 7.8 KB | 灰色火柴人通用版（fallback）|

注：另有 `placeholder_action_badminton.png` / `placeholder_action_pingpong.png` / `placeholder_action_aerobics.png` 三个非规范键的旧版占位符保留备用。

**Fallback 优先级**（在 `blank_template.js` 的 `resolveImage` 函数）：

1. **用户提供的实际图**（检查路径存在性）→ 优先使用
2. **项目专属占位符**（根据 `detectSport(topic, courseName)` 选 sport，从 `SPORT_FORMATION_FILES[sport][pos]` 查文件名）→ 第二优先
3. **通用占位符**（`formation_<sport>_general_*.png`）→ 第三优先
4. **无图**（返回 null，单元格留空）→ 兜底

### 图片生成策略

生成教案时的图片处理原则：

**核心原则：所有图片的提示词必须从教案实际内容中提取参数，禁止凭空捏造通用教学描述。**

1. **教学策略图**：从 `strategy` 字段（策略文本）提取 → `strategy_ai_generator.get_strategy_ai_prompt(strategy_text=...)` → `generate_image`。**数据源：教学策略文本、运动项目、课题名称、授课对象、课程进度上下文**。失败时留空。
2. **教学流程图**：从 `flowChart` 字段（流程图文字）+ LESSON_DATA 教学过程提取 → `flowchart_ai_generator.get_flowchart_ai_prompt(flowchart_text=..., lesson_data=...)` → `generate_image`。**数据源：流程图文字描述、教学过程三阶段内容**。提取失败时返回空提示词，**禁止使用硬编码通用模板**，留空。
3. **课前图**：从 `preClass` 字段（课前活动文字）提取关键信息构建提示词 → `generate_image`。**数据源：课前活动描述文字**。失败时留空。
4. **动作图**：从每个基本部分的 `content` 字段（教学内容）动态构建提示词 → `generate_image`。**每个动作独立生成，必须反映该环节的具体教学细节，禁止用通用动作图代替**。调用 `action_image_generator.get_action_ai_prompt_from_content(sport=..., action_content=...)`。不该有图的地方不加图。失败时留空。
5. **预计生理负荷图**：从教案运动强度数据（练习密度、平均心率、各阶段时间分配）构建提示词 → `generate_image`。**数据源：练习密度、平均心率、教学过程各阶段时间与强度**。失败时留空。也可使用 `heart_rate_curve_v2.py` 的 PIL 绘制作为备选（传入实际心率数据点）。
6. **队形图**：AI 生图（优先）→ PIL fallback → 占位符（A→B→C 三级 fallback）。**数据源：运动项目、阶段、组织教法内容、学生人数**。
7. 使用用户提供的实际图片路径（如有）

