---
name: Chinese-Sport-Science-Journal-Skills
description: 中国体育学期刊投稿技能包。基于 12 本 CSSCI 体育学来源期刊的征稿偏好与录用规律，提供从选题定位到投稿前核查的全流程指引。覆盖体育科学、北京体育大学学报、上海体育大学学报、成都体育学院学报、体育学刊、体育学研究等核心期刊。
triggers:
  - 体育科学
  - 北京体育大学学报
  - 上海体育大学学报
  - 成都体育学院学报
  - 体育学刊
  - 体育学研究
  - 天津体育学院学报
  - 武汉体育学院学报
  - 沈阳体育学院学报
  - 西安体育学院学报
  - 体育科技
  - 体育科技文献通报
  - 体育期刊投稿
  - sport journal
---

# 中国体育学期刊 AI 投稿技能包

基于 12 本 CSSCI 体育学来源期刊的征稿偏好与录用规律，提供从选题定位到投稿前核查的全流程指引。

## 适用场景

- 为体育人文社会学、运动人体科学、竞技训练、学校体育等子学科的中文稿件推荐适配期刊
- 在投稿前核查选题定位、方法门槛、写作风格、格式规范
- 路由到具体期刊的投稿指引

## 路由逻辑

先识别子学科和投稿类型，再匹配最合适的期刊 SKILL.md：

| 子学科 | 推荐期刊 |
|--------|----------|
| 体育人文社会学 / 理论 | 体育科学、体育学研究、体育学刊、上海体育大学学报 |
| 武术文化 / 民族传统体育 | 成都体育学院学报、上海体育大学学报、北京体育大学学报 |
| 青少年体质健康 / 学校体育 | 体育学刊、天津体育学院学报、北京体育大学学报 |
| 数字体育 / 体育产业 | 上海体育大学学报、体育科学、体育学研究 |
| 红色体育 / 体育史 | 成都体育学院学报、体育学研究、体育学刊 |
| 运动人体科学 | 体育科学、天津体育学院学报、武汉体育学院学报 |

## 子技能目录

本技能包包含以下子技能（位于 `skills/` 子目录）：

| 子技能 | 对应期刊 |
|--------|----------|
| cn-sport-journal-workflow | 路由 skill，根据子学科推荐期刊 |
| china-sport-science | 《体育科学》 |
| china-sport-science-and-technology | 《体育科技文献通报》 |
| journal-of-beijing-sport-university | 《北京体育大学学报》 |
| journal-of-chengdu-sport-university | 《成都体育学院学报》 |
| journal-of-physical-education | 《体育学刊》 |
| journal-of-shanghai-university-of-sport | 《上海体育大学学报》 |
| journal-of-shenyang-sport-university | 《沈阳体育学院学报》 |
| journal-of-sports-research | 《体育学研究》 |
| journal-of-tianjin-university-of-sport | 《天津体育学院学报》 |
| journal-of-wuhan-sports-university | 《武汉体育学院学报》 |
| journal-of-xian-physical-education-university | 《西安体育学院学报》 |
| sports-and-science | 《体育科技》 |

使用时请指定具体期刊名称，将自动路由到对应的子技能。
