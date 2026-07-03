# 队形图与动作图

> 本文档详解队形图（AI/PIL 双引擎）和动作图（动态内容驱动）的生成策略。

## 队形图与动作图（v3.6+ 升级）

从 v3.6 开始，队形图与动作图由两套**新的生成器**提供，质量与一致性显著优于 `pe_lesson_images.py` 的火柴人版本。

### 0. 按运动项目差异化（v3.6+ 核心特性）

队形图与动作图**不再"死板使用同一张图"**，而是按运动项目差异化生成与 fallback。

**支持 7 个运动项目**（覆盖中小学与高校常见课程）：

| 项目键 | 典型主题 | 队形图特征 | 动作图风格 |
|--------|---------|-----------|-----------|
| 篮球 | 行进间上篮/投篮/运球 | NBA 标准半场（限制区/三分线/球筐）| 深肤色 + 蓝色球服 + 橙球 |
| 排球 | 垫球/传球/扣球 | 标准排球场（球网+中线+进攻线）| 深肤色 + 蓝色球服 + 白黄排球 |
| 足球 | 运球/射门/4v4 | 标准足球场（中圈+球门+禁区）| 深肤色 + 蓝色球服 + 黑白足球 |
| 田径 | 跨栏/跳远/起跑 | 跑道+起跑线+栏架/沙坑 | 深肤色 + 蓝色背心短裤 |
| 武术 | 少年拳/五步拳 | 武术场地+对练队列 | 白色武术服 |
| 体操 | 前滚翻/平衡木 | 体操场地+器械 | 蓝色连体服 |
| 通用 | 未识别项目 | 通用场地 | 通用球服 |

**自动识别机制**（位于 `blank_template.js`）：

```js
function detectSport(topic, courseName) {
  const text = (topic || '') + ' ' + (courseName || '');
  for (const sport of ['篮球','排球','足球','田径','武术','体操']) {
    if (text.indexOf(sport) >= 0) return sport;
  }
  return '通用';  // fallback
}
```

**差异化 fallback 流程**（`resolveImage` 函数）：

1. 用户未提供 `orgImg` → 调用 `resolveImage(null, 'formation:prepare')`
2. 解析 key 前缀 `formation:` → 提取位置 `prepare`
3. 查表 `SPORT_FORMATION_FILES[sport][pos]` → 返回项目专属文件名
4. 例：排球教案的 `formation:basic_3` → `formation_volleyball_circle.png`（围圈队形）

**项目专属占位符**（`scripts/images/`，共 35 张 = 7 项目 × 5 张）：

| 项目 | prepare | basic_1 | basic_2 | basic_3 | ending |
|------|---------|---------|---------|---------|--------|
| 篮球 | `..._prepare.png` | `..._basic_1.png` | `..._basic_2.png` | `..._basic_3.png` | `..._ending.png` |
| 排球 | `..._prepare.png` | `..._2v2.png` | `..._2v2.png` | `..._circle.png` | `..._relax.png` |
| 足球 | `..._prepare.png` | `..._4v4.png` | `..._4v4.png` | `..._basic_3.png` | `..._ending.png` |
| 田径 | `..._prepare.png` | `..._start.png` | `..._start.png` | `..._basic_3.png` | `..._ending.png` |
| 武术 | `..._prepare.png` | `..._duilian.png` | `..._duilian.png` | `..._duilian.png` | `..._ending.png` |
| 体操 | `..._prepare.png` | `..._groups.png` | `..._groups.png` | `..._groups.png` | `..._ending.png` |
| 通用 | `..._prepare.png` | `..._basic_1.png` | `..._basic_2.png` | `..._basic_3.png` | `..._ending.png` |

动作图占位符（位于 `PLACEHOLDERS`）：`placeholder_action.png`（通用，灰色火柴人 fallback）+ `placeholder_action_<sport>.png` 系列（v3.6.3 已批量补齐 6 张项目专属占位符，详见上方「动作图项目占位符 key」表格）。

**端到端验证**（最近一次回归测试）：

| 教案 | 嵌入图数 | 队形图（按项目） |
|------|---------|---------------|
| 排球·正面双手垫球 | 7 张 | volleyball_prepare / 2v2 / circle / relax |
| 足球·脚内侧运球 | 8 张 | football_prepare / 4v4 / basic_3 / ending |
| 武术·五步拳 | 7 张 | martial_prepare / duilian(×3) / ending |

**已修复**（v3.6.3）：6 个项目专属动作图占位符（basketball/volleyball/football/athletics/martial/gym）已批量生成并写入 `PLACEHOLDERS`，fallback 链按「项目专属 → 通用版」顺序工作，端到端测试 6 份教案均嵌入正确动作图。

### 0. 队形图生成策略（队形图，v4.1 — AI 优先，PIL fallback）

**核心原则**：队形图优先使用 AI 生图（方案 A），当 AI 生图不可用时自动 fallback 到 PIL 程序化绘制（方案 B），最后 fallback 到预生成占位符（方案 C）。

**三级 Fallback 链**：

| 优先级 | 方案 | 工具/脚本 | 输出质量 | 适用场景 |
|-------|------|----------|---------|---------|
| **A（首选）** | AI 生图 | `generate_image` + `formation_ai_generator.py` | 定制化、美观、与教案内容强相关 | 有 AI 生图能力的环境 |
| **B（备选）** | PIL 程序化绘制 | `formation_composer.py`（v4.0 引擎） | 卡通人形剪影、稳定可靠、< 1秒 | 无 AI 生图 / AI 生图失败 |
| **C（兜底）** | 预生成占位符 | `scripts/images/formation_*.png`（52 张） | 静态图、按项目匹配 | PIL 执行失败 |

**方案 A：AI 生图流程**

1. 导入 `formation_ai_generator`：
   ```python
   from formation_ai_generator import get_ai_prompt
   ```
2. 调用 `get_ai_prompt(sport, phase, topic=..., n_students=..., label_lang="zh")` 获取英文提示词和输出文件名（`label_lang`: "zh"=中文标注 / "en"=英文标注，默认"zh"）
3. 用 `generate_image` 工具生成图片（`aspect_ratio: "6:5"`）
4. 将生成的图片路径写入 `LESSON_DATA` 的 `orgImg` / `prepareOrgImg` / `endingOrgImg` 字段

**提示词自动包含**：
- **统一场景约束**（`SCENE_STYLE`）：同一节课所有阶段的背景场景（室内/室外、场地类型、色调、光照）完全一致
- **统一人物约束**（`CHARACTER_STYLE`）：大学生(18-22岁)体型，男=深蓝T(#1A3A5C)+白短裤+白鞋，女=白T+深蓝短裤(#1A3A5C)+白鞋，教师=红Polo(#D23030)+黑裤+黑鞋，扁平矢量插画风格
- **标注语言控制**（`label_lang`）："zh"=中文标注（教师/男生/女生/热身活动），"en"=英文标注（Teacher/Male/Female/Warm-up）
- 运动项目专属场地描述（篮球半场/排球场地/足球绿茵场/武术太极图等）
- 教学阶段队形特征（集合整队/分组练习/对抗比赛/放松总结等）
- 学生人数和编组信息
- 教师位置和标注要求
- 方向箭头、图例框、标题栏等可视化标注

**一致性保障机制（v4.5）**：
1. **`CHARACTER_STYLE`**：统一定义人物外观为大学生体型（18-22岁），男女服装颜色区分（男深蓝T+白短裤，女白T+深蓝短裤），教师红Polo+黑裤，扁平矢量插画风格，禁止 AI 画出不同形态的人物
2. **`SCENE_STYLE`**：按运动项目锁定场景类型（室内/室外）、场地布局、色调、光照条件，所有阶段共享完全相同的背景描述
3. **提示词结构化**：场景 → 人物风格 → 阶段内容 → 元素 → 标注 → 质量，固定拼接顺序确保一致性约束始终前置
4. **`label_lang` 参数**：统一控制所有标注文字语言，默认"zh"（中文）

**方案 B：PIL fallback 流程**

当 AI 生图不可用（如大模型无 `generate_image` 工具）或 AI 生图失败时：
```python
import sys
sys.path.insert(0, "/home/lingxi/skills/pe-lesson-plan/scripts")
from formation_ai_generator import generate_formation_image

# use_ai=False 直接走方案 B
path = generate_formation_image(
    sport="篮球", phase="prepare",
    topic="行进间单手肩上投篮", n_students=24,
    output_dir="/home/lingxi/workspace",
    use_ai=False,
    label_lang="zh",  # "zh"=中文标注, "en"=英文标注
)
```

**方案 C：占位符兜底**

当 PIL 也失败时，`generate_formation_image` 自动返回预生成的项目专属占位符路径。

**SKILL.md 中的执行规则**：

Agent 在生成教案时，队形图生成步骤应遵循以下判断逻辑：
1. **检查环境是否有 `generate_image` 工具** → 有：走方案 A；无：直接跳到方案 B
2. **方案 A 执行**：调用 `get_ai_prompt(label_lang=...)` 获取提示词（`label_lang` 由用户在步骤 4 中选择，默认"zh"）→ 调用 `generate_image` → 成功则写入 LESSON_DATA
3. **方案 A 失败**（`generate_image` 报错/超时）→ 自动跳到方案 B
4. **方案 B 执行**：调用 `generate_formation_image(use_ai=False)` → 成功则写入 LESSON_DATA
5. **方案 B 失败** → 返回占位符路径，`resolveImage` 兜底机制继续生效

**覆盖范围**：9 个运动项目 × 5 个教学阶段 = 45 种组合，全部有提示词模板和 PIL 绘制函数。


### 0.1 教学策略图生成策略（教学策略图，v4.3 — AI 优先，PIL fallback）

教学策略图从纯 PIL/matplotlib 绘制升级为"AI 生图优先，PIL fallback"的双引擎策略，根据教案策略内容生成定制化的教学策略图示。

**新增文件**：`scripts/strategy_ai_generator.py`

#### 判断逻辑

1. **检查 AI 生图可用性**：当前环境是否有 `generate_image` 工具
2. **方案 A 执行**：调用 `get_strategy_ai_prompt(label_lang=...)` 获取提示词（`label_lang` 由用户在步骤 4 中选择，默认"zh"）→ 调用 `generate_image` → 成功则写入 LESSON_DATA
3. **方案 A 失败**（`generate_image` 报错/超时）→ 自动跳到方案 B
4. **方案 B 执行**：调用 `strategy_visualizer.py` 的 `generate_from_template()` 或 `generate_strategy_diagram()` → 成功则写入 LESSON_DATA
5. **兜底**：两者均失败时 `strategyImg` 留空，模板自动使用 `placeholder_strategy.png`

#### 方案 A — AI 生图（优先）

- 根据运动项目 + 课时类型 + 教学策略文本 + 理论依据 + 课题名称 + 授课对象自动构建提示词
- 覆盖 5 种视觉风格（默认 auto 自动匹配）
- **标注语言控制**（`label_lang`）："zh"=中文标注（准备部分/基本部分/结束部分/策略标签/理论依据/学习目标），"en"=英文标注（Preparation/Main Practice/Closing/Key strategies/Theoretical foundation/Learning goals）
- 五种视觉风格（`sporty` / `athletic` / `cultural` / `fluid` / `clean`），默认 `auto` 自动匹配
  - 配置来源：`scripts/style_config.py`
- 输出纵向 2:3 宽高比（4.64×6.97 英寸，占页面三分之二高度）
- 通过 `generate_image` 工具执行

**代码示例**：
```python
from strategy_ai_generator import get_strategy_ai_prompt

info = get_strategy_ai_prompt(
    sport="篮球", lesson_type="新授课",
    strategy_text="情境设问—领会探究—分层比赛—反思复盘",
    theory="TGfU 领会教学法", topic="篮球传切配合",
    target="大二女生", style="auto",
    curriculum_context="..."  # v4.0 新增：课程进度上下文（从教学计划提取，无大纲时传空字符串）
)
# 返回 dict: prompt, output_filename, aspect_ratio, fallback_script, fallback_func, fallback_placeholder
# Agent 调用: generate_image(prompt=info["prompt"], aspect_ratio="2:3", ...)
```

#### 方案 B — PIL fallback（备选）

- AI 生图不可用时 fallback 到 `strategy_visualizer.py`（matplotlib）
- 4.64×6.97 英寸，2:3 宽高比，纵向布局
- 三套预设模板（`basketball_new` / `track_hurdle_review` / `wushu_young_fist`）
- 五种视觉风格（`sporty` / `athletic` / `cultural` / `fluid` / `clean`）
- 稳定可靠，< 3 秒生成

**图片风格要求**：
- 方案 A（AI 生图）：彩色教育信息图风格，根据运动项目和课型自动匹配视觉主题
- 方案 B（PIL）：模块化设计，五大区块（标题/三段策略/项目特异/目标/页脚），支持彩色

### 1. 队形图库（`formation_lib.py` + `formation_composer.py`）

**库**：基于 PIL 直接绘制，启动快（< 1 秒），不依赖 matplotlib。

**核心特性**：
- **7 种运动场地**（`formation_lib.py`）：
  - 篮球（NBA 标准半场 14m × 12m，含限制区/罚球圈/三分线/球筐/方位标识）
  - 排球（标准排球场，含球网+中线+进攻线+发球区）
  - 足球（标准足球场，含中圈+球门+禁区+角球区）
  - 田径（直道+弯道+起跑线+栏架+沙坑）
  - 武术（武术场地+对练站位+兵器架）
  - 体操（自由体操场地+器械+保护垫）
  - 通用（占位场地，未识别项目 fallback）
- **球员位置严格在场地线外**：避免与场地标线重叠
- **编号规律统一**：
  - 4 列 × 6 行横队：从前到后 + 左到右递增（编号 1-24）
  - 排球 2v2：双方各 2 人
  - 足球 4v4：红队 A1-A4 / 蓝队 B1-B4
  - 围圈展示：1-N 从左到右
  - 武术对练：A1-A4 / B1-B4 双人对练
- **三级字号规范**：TITLE 22pt / LABEL 14pt / ANNO 12pt
- **独立标题/底部区**：与场地完全分离，绝不重叠

**高阶接口**（按项目差异化）：

```python
from formation_composer import (
    # 按项目差异化的队形绘制
    draw_formation_prepare,              # 通用：四列横队集合
    draw_formation_3v3,                 # 篮球：3v3 半场对抗
    draw_formation_grouped_rotation,    # 通用：A/B/C 三组分层轮换
    draw_formation_circle_demo,         # 通用：围圈展示 + 影像反馈
    draw_formation_relax,               # 通用：四列横队放松
    draw_formation_custom,              # 自由队形
    # 各项目专用队形
    draw_formation_volleyball_2v2,      # 排球：2v2 隔网对抗
    draw_formation_volleyball_circle,   # 排球：围圈垫球
    draw_formation_volleyball_prepare,  # 排球：集合整队
    draw_formation_football_4v4,        # 足球：4v4 小场地比赛
    draw_formation_athletics_start,     # 田径：起跑准备
    draw_formation_martial_duilian,     # 武术：对练队列
    draw_formation_gym_groups,          # 体操：分组练习
    draw_formation_general_prepare,     # 通用：标准准备队形
    # 一键生成（推荐）
    generate_all_formations,            # 通用：5 张固定接口
    generate_formations_by_topic,       # ★ 按 topic/courseName 自动识别项目
    generate_sport_formations,          # 按运动项目生成 5 张
)

# ★ 方式 1：按 topic 自动识别项目（推荐）
#    "排球-正面双手垫球" → 排球场 + 2v2/circle/relax
#    "足球-脚内侧运球"   → 足球场 + 4v4/4v4/basic_3/ending
#    "武术-五步拳"       → 武术场 + duilian/duilian/duilian/ending
paths, sport = generate_formations_by_topic(
    topic="排球-正面双手垫球",
    course_name="排球",
    output_dir="/home/lingxi/workspace/pe_lesson_demo",
)
# 返回: ({'prepare': '...', 'basic_1': '...', 'basic_2': '...', 'basic_3': '...', 'ending': '...'}, '排球')

# 方式 2：按运动项目直接指定
paths = generate_sport_formations(
    sport="足球",
    output_dir="/home/lingxi/workspace/pe_lesson_demo",
)
# 返回: 5 张足球场队形图（prepare/4v4/4v4/basic_3/ending）

# 方式 3：通用 5 张接口（默认篮球场）
paths = generate_all_formations(
    output_dir="/home/lingxi/workspace/pe_lesson_demo",
    tasks=("A 组 · 完整跨步上篮", "B 组 · 固定点跨步起跳+拨球", "C 组 · 行进间 3 步急停"),
    n_students=24,
)
# 返回: {'prepare': '...', 'basic_1': '...', ...}
```

**嵌入教案**：将 `formation_prepare.png` 等路径填入 `LESSON_DATA`：
- `prepareOrgImg`: 准备部分队形图
- `basic[i].orgImg`: 第 i 段基本部分的队形图
- `endingOrgImg`: 结束部分队形图

**自定义队形**（高级用法）：

```python
from formation_composer import draw_formation_custom

path = draw_formation_custom(
    title="基本部分：足球 4v4 比赛",
    subtitle="小场地比赛 · 20 分钟",
    duration="20 分钟",
    players=[
        (3.0, 6.0, fl.STUDENT, "B1", 0.55),  # x, y, color, number, size
        (5.0, 6.5, fl.STUDENT, "B2", 0.55),
        # ... 更多球员
    ],
    teacher=(11.0, 10.5, 0.55),
    balls=[(3.0, 6.0, 0.20)],
    arrows=[
        (3.0, 6.0, 6.0, 3.0, fl.OPP_RED, 3, "进攻方向"),  # 带文字标签
    ],
    footer_lines=["4v4 比赛 | 进攻战术演练", "教师观察 + 即时反馈"],
    output_path="formation_football.png",
)
```

### 2. 动作图生成器（`action_image_generator.py`）

**库**：基于 AI 生图（`generate_image` 工具）生成写实、统一风格的动作分解图。

**核心特性（v4.8.0 更新）**：
- **动态内容驱动**：每个动作图的提示词必须从教案中该环节的具体教学内容（`content` 字段）动态构建，**禁止使用与教案无关的预设通用动作描述**
- **每张独立生成**：每个基本部分环节的动作图独立调用 AI 生图，反映该环节独有的教学细节
- **不适用时不生成**：不该有图的地方（如理论讲解、课堂常规等非动作环节）不生成动作图
- **风格参考库**（`SPORT_TEMPLATES`）：提供 15 组预设运动项目的外观参数（球衣颜色、器材等），仅用于保持视觉一致性，**不用于替代教案内容**

**推荐调用方式（v4.8.0 动态内容模式）**：

```python
from action_image_generator import get_action_ai_prompt_from_content

# 遍历 basic 数组的每个环节
for idx, part in enumerate(lesson_data["basic"]):
    action_content = part.get("content", "")
    if not action_content or not is_movement_content(action_content):
        continue  # 非动作环节，不生成图

    info = get_action_ai_prompt_from_content(
        sport=lesson_data["courseName"],       # 运动项目
        action_content=action_content,           # 该环节的具体教学内容（从教案提取）
        step_label=f"基本部分{idx+1}",
        step_index=idx,
        label_lang="zh",
    )
    if info["prompt"]:  # 提示词非空才生成
        # Agent 调用: generate_image(prompt=info["prompt"], aspect_ratio="1:1", ...)
        part["contentImg"] = generated_image_path
```

**预设外观参考库**（`SPORT_TEMPLATES`，仅提供球衣/器材等视觉参数，不提供动作描述）：

| 键 | 球服 | 器材 | 用途 |
|---|------|------|------|
| `篮球-上篮` | 蓝色背心+短裤 | 橙色篮球 | 视觉参考（不直接使用 steps） |
| `篮球-投篮` | 蓝色背心+短裤 | 橙色篮球 | 视觉参考 |
| `排球-传球` | 蓝色背心+短裤 | 白黄排球 | 视觉参考 |
| `排球-扣球` | 蓝色背心+短裤 | 白黄排球 | 视觉参考 |
| `足球-射门` | 蓝色球衣+短裤 | 黑白足球 | 视觉参考 |
| `田径-跨栏` | 蓝色背心+短裤 | 无 | 视觉参考 |
| `田径-跳远` | 蓝色背心+短裤 | 无 | 视觉参考 |
| `武术-少年拳` | 白色武术服 | 无 | 视觉参考 |
| `体操-前滚翻` | 蓝色连体服 | 无 | 视觉参考 |
| `羽毛球-*` / `乒乓球-*` / `健美操-*` | 见代码 | 见代码 | 视觉参考 |

> **注意**：旧版 `generate_action_sequence(sport_key=...)` 直接使用预设模板的 `steps` 动作描述生成图片，**已不推荐**，因为那些动作描述可能与当前教案实际教学内容不一致。请使用 `get_action_ai_prompt_from_content(action_content=...)` 从教案内容动态构建。

### 4. 完整工作流示例（v4.8.0 · 动态内容驱动）

```python
import sys, os, json
sys.path.insert(0, "/home/lingxi/skills/pe-lesson-plan/scripts")
from formation_composer import generate_formations_by_topic
from action_image_generator import get_action_ai_prompt_from_content

OUT = "/home/lingxi/workspace/pe_lesson_demo"

# === 0. 课程信息（用户输入）===
course_name = "排球"
topic = "排球-正面双手垫球"

# === 教案实际教学过程（用户提供的教案内容）===
basic_parts = [
    "正面双手垫球：学生分两组面对面站立，距离3米，一人抛球一人垫球，要求：击球部位在腕关节以上10厘米处，双臂夹紧伸直",
    "垫球-抛球配合：两人一组，一人连续抛球，另一人连续垫球，每10次交换，强调脚步移动和身体正对来球",
    "垫球游戏：6人围成圆形，中间一人向四周垫球，接球者迅速垫回，不掉球为胜",
]

# 1. 生成队形图（按项目自适应）
formation_paths, detected_sport = generate_formations_by_topic(
    topic=topic, course_name=course_name, output_dir=OUT,
)

# 2. 动作图：从每个基本部分的实际教学内容动态构建提示词
#    ★ 每张图反映该环节独有的教学细节，不使用预设通用模板
action_imgs = []
for idx, part_content in enumerate(basic_parts):
    info = get_action_ai_prompt_from_content(
        sport=course_name,
        action_content=part_content,  # ← 教案实际教学内容
        step_label=f"练习{idx+1}",
        step_index=idx,
        label_lang="zh",
    )
    if info["prompt"]:
        # Agent 调用: generate_image(prompt=info["prompt"], aspect_ratio="1:1", ...)
        img_path = f"{OUT}/action_basic_{idx+1}.png"
        action_imgs.append(img_path)

# 3. 组装 LESSON_DATA
data = {
    "courseName": course_name,
    "topic": topic,
    "prepareOrgImg": formation_paths.get("prepare"),
    "basic": [
        {"content": basic_parts[0], "contentImg": action_imgs[0] if len(action_imgs) > 0 else None, "orgImg": formation_paths.get("basic_1")},
        {"content": basic_parts[1], "contentImg": action_imgs[1] if len(action_imgs) > 1 else None, "orgImg": formation_paths.get("basic_2")},
        {"content": basic_parts[2], "contentImg": action_imgs[2] if len(action_imgs) > 2 else None, "orgImg": formation_paths.get("basic_3")},
    ],
    "endingOrgImg": formation_paths.get("ending"),
}

# 4. 调用 blank_template.js 生成 docx
os.environ["LESSON_DATA"] = json.dumps(data, ensure_ascii=False)
```

**核心要点**：
- 动作图提示词从教案 `basic[].content` 动态构建，**每张图反映具体教学细节**
- 不适用动作图的环节（如理论讲解）不生成，`contentImg` 留空
- 队形图保持原有按项目自适应逻辑



