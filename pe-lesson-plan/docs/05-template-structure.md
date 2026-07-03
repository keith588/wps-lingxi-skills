# 模板结构

> 本文档说明 .docx 模板的表格布局、列宽 DXA、心率图 V2 等技术细节。

## 模板结构

模板为单一表格，9列网格（总宽8700 DXA），A4页面，边距720 DXA，宋体/Times New Roman。

列宽分布：W = [495, 959, 1641, 895, 260, 1134, 1304, 1201, 811]

表格行结构：

| 行 | 结构 | 说明 |
|----|------|------|
| 1-3 | 标签×2 + 值 + 标签×2 + 值 + 标签 + 值×2 | 基本信息三行 |
| 4-10 | 标签×2 + 内容×7 | 分析字段七行（课题名称→教学重难点） |
| 11 | 分页行 | 分页符（教学重难点后，策略内容从新页开始） |
| 12 | 标签×2 + 内容×7（策略文字+图上下排列） | 教学策略：**文字和图片在同一单元格内上下排列，不分两栏**，行高自适应 |
| 13 | 分页行 | 分页符（策略后，流程图从新页开始） |
| 14 | 标签×2 + 内容×7（含流程图图片） | 教学流程图 |
| 15 | 标签×2 + 内容×7（含课前图片） | 课前 |
| 16 | 标签跨9列 | 教学方法与手段 |
| 17 | 课的部分 + 教学内容×3 + 组织教法×4 + 时间 | 教学过程表头 |
| 18 | 准备部分（组织教法列含队形图） | 教学过程 |
| 19+ | 基本部分×N（教学内容列含动作图，组织教法列含队形图） | 教学过程 |
| 20+ | 结束部分（组织教法列含队形图） | 教学过程 |
| 21-22 | 教学评价(纵合并) + 预计生理负荷(纵合并+图片) + 练习密度/平均心率 | 评价区域 |
| 23 | 课后 | |
| 24 | 教学反思 | |


### 预计生理负荷图（V2 增强版）

V2 增强版由 `scripts/heart_rate_curve_v2.py` 生成，配合 `integrate_heart_curve.py` 自动集成到 LESSON_DATA。
特征：三色强度分区（低/中/高）+ 平滑曲线 + 峰谷标记 + 平均心率虚线，输出 800×480 PNG。
实现细节见脚本源码。


预计生理负荷图是教案"评价与反思"区的核心可视化，决定了整份教案的专业度和科学性。V2 增强版在风格统一的基础上支持**跨教案的曲线个性化**——任何教案调用 V2 时，自动按课程时段生成对应的心率曲线，所有图片风格/尺寸/色系完全一致。

#### V2 vs 原版对比

| 模块 | 原版（pe_lesson_images.py） | V2 增强版（heart_rate_curve_v2.py） |
|------|---------------------------|----------------------------------|
| 折线 | 2 px 直角折线 | 3 px **Catmull-Rom 平滑曲线** |
| 数据点 | r=3 纯黑 | **r=6 白边 + r=4 黑芯**（视觉跳出）|
| 强度分区 | 无 | **低 60-120 / 中 120-150 / 高 150-180** 三色柔色背景 + 区间数值标注 |
| 曲线下区域 | 无 | 自适应 alpha 渐变填充（顶 70→ 底 20）|
| 峰谷标记 | 无 | 红色三角 + 白底圆角标签（峰值）/ 蓝色三角（谷值）|
| 平均心率 | 无 | 灰色虚线 + 圆角白底标签（与曲线视觉分离）|
| 图例 | 无 | 顶部低/中/高三色块 + 心率范围中文标注 |
| 中文字体 | 缺失 | Noto Sans CJK SC（index=1 显式指定）|

输出尺寸：**800 × 480 像素**（4.17 × 2.5 英寸 @ 192 DPI），嵌入"预计生理负荷"标签旁的图片 cell（col 6-8，maxWidth 边距 -40 DXA）。

- 旧版 590×340 在 Word 中按 96 DPI 解读会被压缩到约 252×145 px（占单元格 60%）
- V3 版 800×480 在 Word 中按 96 DPI 解读会被压缩到约 215×129 px（占单元格 95%+），大源图仍清晰
- 标签 cell 跨 2 列（col 4-5 = 1394 DXA = 0.97"），足够容纳 6 个汉字居中显示

#### 集成协议（4 种入口，按优先级）

LESSON_DATA 中可新增 4 类字段生成心率曲线：

| 优先级 | 字段 | 类型 | 用途 |
|--------|------|------|------|
| 1（最高）| `intensityPoints` | `list[(int, int)]` | 完全自定义强度数据 |
| 2 | `intensityProfile` | `str` | 直接指定预置 profile，如 `"足球/耐久跑"` |
| 3 | `intensityProject` | `str` | 项目名（自动按规则匹配）|
| 4 | `intensityType` | `str` | 课型名（与 intensityProject 配合）|
| 辅 | `intensityTitle` | `str` | 自定义图标题（默认从 courseName 推断）|

**优先级逻辑**：
1. 若 `intensityPoints` 存在且非空 → 完全使用自定义数据
2. 否则按 `intensityProject` + `intensityType` 查预置库 → `match_profile_v2(project, type)`
3. 否则按 `intensityProfile`（如 `"篮球/新授课"`）查预置库
4. 都没有则用第一预置的兜底曲线

**总时长自动推断**：从 `prepare`/`basic`/`ending` 的 `time` 字段累加（支持 `'15'`/`'15'`/`'15min'`/`'15分'` 等格式），数据点的时间轴自动按总时长缩放。

#### 项目-曲线预置库

`scripts/load_curve_profiles.py` 内置 11 类项目 × 20 套曲线，覆盖常见体育课：

| 项目 | 课型覆盖 | 数据点数 |
|------|---------|---------|
| 篮球 | 新授课 / 复习课 / 考核课 | 19/19/21 |
| 足球 | 新授课 / 耐久跑 | 17/17 |
| 排球 | 新授课 / 复习课 | 17/17 |
| 田径-短跨 | 新授课 / 复习课 | 21/21 |
| 田径-中长跑 | 新授课 / 耐久跑 | 17/17 |
| 武术 | 综合课 / 新授课 | 19/19 |
| 体操 | 新授课 | 17 |
| 健康操 | 新授课 | 17 |
| 游戏 | 竞赛课 | 21 |
| 力量训练 | 新授课 | 21 |
| 球类（通用）| 新授课 / 竞赛课 | 17/21 |

**32 个别名映射**（口语/习惯名 → 预置项目名）：
- 跨栏/110米栏/100米栏 → 田径-短跨
- 太极/长拳/少年拳/五步拳/防身术/散打 → 武术
- 耐久跑/800米/1500米/3000米/5000米 → 田径-中长跑
- 健美操/有氧操/瑜伽 → 健康操
- 引体向上/深蹲/核心力量 → 力量训练
- 羽毛球/乒乓球/网球 → 球类
- 跳远/跳高 → 田径-跳跃（暂无数据，回退到田径-短跨）
- 追逐游戏/抢球/接力 → 游戏

**课型归一化**：新授→新授课、复习/巩固→复习课、考核/测验/考试/测试→考核课、综合→综合课、耐力→耐久跑。

#### 端到端调用（推荐）

```python
import sys, os, json, importlib.util
sys.path.insert(0, '/home/lingxi/skills/pe-lesson-plan/scripts')
sys.path.insert(0, '/home/lingxi/skills/docx/scripts')

# 加载 3 个核心模块
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

base = '/home/lingxi/skills/pe-lesson-plan/scripts'
mod_ihc = load_mod('integrate_heart_curve', f'{base}/integrate_heart_curve.py')
from run_code_docx import run_node_docx

# 1) 准备 LESSON_DATA
lesson_data = {
    "title": "...", "courseName": "...", "colorTheme": "ocean",
    "prepare": {"time": "5'"},
    "basic": [{"time": "15'"}, {"time": "20'"}],
    "ending": {"time": "5'"},
    "intensityProject": "跨栏",      # 项目名（自动匹配预置库）
    "intensityType": "复习课",        # 课型
    # 或完全自定义：intensityPoints: [(0,75), (10,130), (25,160), ...]
    ...
}

# 2) 自动集成心率图（生成 V2 PNG + 计算加权平均心率）
ic = mod_ihc.integrate_load_curve(lesson_data, out_dir='/home/lingxi/workspace/load_curves')
lesson_data["heartRateImg"] = ic["heartRateImg"]
lesson_data["avgHeartRate"] = f"约 {ic['weighted_avg']:.0f} 次/分（详见曲线）"

# 3) 渲染 .docx
```python
# 详见 scripts/blank_template.js，核心接口：
# run_node_docx('scripts/blank_template.js', env={'LESSON_DATA': json.dumps(data)})
```

