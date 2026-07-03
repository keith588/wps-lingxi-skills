---
name: scholar-scout-fetch
description: |
  论文抓取（3步流水线第1步）。从OpenAlex和Semantic Scholar抓取社科论文，三层关键词打分筛选。
  输出 /tmp/scholar_papers_top.json 供下游 scholar-scout-review 消费。
triggers:
  - "论文抓取"
  - "跑一下论文抓取"
---

# Scholar Scout Fetch — 论文抓取（Step 1/3）

从 OpenAlex + Semantic Scholar 双源抓取社科论文，经三层关键词打分后输出 Top-N JSON。

## Step 0 — 读取配置

1. 读取共享配置 `~/.claude/skills/_shared/scholar-config.json`（Windows: `C:\Users\你的用户名\.claude\skills\_shared\scholar-config.json`）。
2. 如果存在 `scholar-config.local.json`（同目录），用它 deep-merge 覆盖主配置。
3. 关注以下字段：
   - `daily_papers.keywords` — 正向关键词（标题命中 +3，摘要命中 +1）
   - `daily_papers.negative_keywords` — 负向关键词（命中即排除，score = -999）
   - `daily_papers.domain_boost_keywords` — 领域增强词（1 hit +1，2+ hits +2）
   - `daily_papers.min_score` — 最低分数阈值（默认 2）
   - `daily_papers.top_n` — 单日返回篇数（默认 10，多天模式按 top_n × days）
   - `researcher.email` — OpenAlex polite pool 邮箱
   - `researcher.semantic_scholar_api_key` — S2 API key（可选，空串走免费限额）

## Step 1 — 解析时间范围

从用户输入中提取天数参数：

| 用户说法 | 解析结果 |
|---------|---------|
| "过去一周" / "最近7天" | `--days 7` |
| "过去3天" | `--days 3` |
| "昨天的" / "过去1天" | `--days 1` |
| 无明确说明（默认） | `--days 1` |

## Step 2 — 运行抓取脚本

执行 Python 脚本：

```bash
# 默认（1天）
python "~/.claude/skills/scholar-scout/fetch_and_score.py" > /tmp/scholar_papers_top.json

# 多天模式
python "~/.claude/skills/scholar-scout/fetch_and_score.py" --days 7 > /tmp/scholar_papers_top.json
```

脚本内部流程：
1. **OpenAlex Recent** — 按发布日期倒序抓取最新论文
2. **OpenAlex High-Cited** — 按引用量倒序抓取近 12 个月高引论文
3. **Semantic Scholar** — 补充查询，覆盖 OpenAlex 遗漏的论文
4. **Merge & Dedup** — 按 DOI / 标题去重，保留高分版本
5. **History Dedup** — 单日模式下排除历史已推荐论文
6. **Score Filter** — 仅保留 score >= min_score 的论文，按分数降序排列

进度日志输出到 stderr，最终 JSON 数组输出到 stdout（重定向至文件）。

## Step 3 — 校验输出

1. 确认 `/tmp/scholar_papers_top.json` 存在且非空。
2. 用 `python -c "import json; d=json.load(open('/tmp/scholar_papers_top.json')); print(len(d))"` 验证是 valid JSON 并获取论文数量。
3. 如果文件为空或 JSON 无效，报告错误并建议检查网络连接或配置。

## Step 4 — 汇报结果

向用户报告：

- 抓取到 **N** 篇论文（已通过三层打分筛选）
- 数据源：OpenAlex Recent + OpenAlex High-Cited + Semantic Scholar
- 输出位置：`/tmp/scholar_papers_top.json`
- 建议下一步：运行 `/scholar-scout-review` 生成推荐摘要

## 与原 HuggingFace+arXiv 管线的关键差异

| 维度 | 原管线 | 当前管线 |
|------|--------|---------|
| 数据源 | HuggingFace Daily Papers + arXiv | OpenAlex + Semantic Scholar |
| Enrich 步骤 | 需要额外 enrich（arXiv 元数据不全） | 不需要（OpenAlex 已含丰富元数据） |
| 覆盖学科 | 偏 CS/AI | 社科全覆盖 |
| 打分机制 | 单层关键词 | 三层：keywords / negative / domain_boost |
| 引用数据 | 无 | OpenAlex + S2 引用量加分 |
| 期刊质量 | 无 | 内置高影响力社科期刊列表加分 |
