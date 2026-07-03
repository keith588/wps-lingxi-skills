---
name: scholar-mocs
description: |
  Obsidian目录页自动生成与维护。递归扫描论文笔记和概念库目录，
  自动生成带wikilink的索引页。
  触发词："更新索引"、"刷新目录"
---

# Scholar MOCs — Obsidian 索引页自动生成

自动扫描 Obsidian Vault 中的论文笔记和概念库目录，生成带 `[[wikilink]]` 的 Map of Content (MOC) 索引页。

**Pipeline 位置**：
```
daily-paper-scout → [论文笔记/*.md]
                          ↓
                   [scholar-mocs] → 索引页 (MOC .md files)
                          ↑
                   [_概念/*.md]
```

---

## 工作流程

### Step 1: 读取配置

从 `../_shared/scholar-config.json` 读取：
- `paths.obsidian_vault` — Vault 根目录
- `paths.paper_notes_folder` — 论文笔记目录名（默认 `论文笔记`）
- `paths.concepts_folder` — 概念库目录名（默认 `_概念`）

### Step 2: 运行生成脚本

```bash
python "~/.claude/skills/scholar-mocs/generate_mocs.py" --mode all
```

可选 `--mode` 参数：
| 值 | 扫描范围 |
|---|---------|
| `concepts` | 仅扫描 `_概念/` 下的 6 个子分类 |
| `papers` | 仅扫描 `论文笔记/`（排除 `_概念` 子目录） |
| `all` | 两者都扫描（默认） |

加 `--dry-run` 可预览变更但不写文件。

### Step 3: 输出结果

脚本为每个包含 `.md` 文件的目录生成一个索引文件 `_Index.md`，内容结构：

```markdown
# 目录名

> Auto-generated MOC · 共 N 篇笔记 · 更新于 YYYY-MM-DD HH:MM

## 子目录
- [[子目录A/_Index|子目录A]] (12 篇)
- [[子目录B/_Index|子目录B]] (8 篇)

## 笔记
- [[笔记文件名1]]
- [[笔记文件名2]]
- ...
```

---

## 硬规则

1. **幂等**：内容无变化时不重写文件，保持 git 干净
2. **仅管理 `_Index.md`**：不修改任何用户笔记文件
3. **排除规则**：跳过 `_Index.md` 自身、`.obsidian/`、模板目录
4. **Windows 兼容**：全程使用 `pathlib`，不依赖 Unix 路径
5. **wikilink 格式**：使用不含 `.md` 后缀的文件名，Obsidian 标准格式

---

## 概念库子分类（6 类）

`_概念/` 目录下预期存在以下子目录：

| 子目录 | 说明 |
|--------|------|
| 理论框架 | Theories & Frameworks |
| 核心构念 | Core Constructs |
| 研究方法 | Research Methods |
| 统计方法 | Statistical Methods |
| 量表工具 | Scales & Instruments |
| 领域术语 | Domain Terms |

---

## Quick Commands

**更新全部索引**：
```
更新索引
```

**仅刷新概念库目录**：
```
刷新目录 --mode concepts
```

**仅刷新论文笔记目录**：
```
刷新目录 --mode papers
```

**预览变更（不写入）**：
```
更新索引 --dry-run
```

---

## Startup Behavior

当用户触发本 skill 时：

1. 读取 `scholar-config.json` 获取 Vault 路径
2. 执行 `generate_mocs.py --mode all`
3. 报告结果：
   - 扫描了多少个目录
   - 新建了多少个索引页
   - 更新了多少个索引页
   - 跳过了多少个（无变化）

> **索引已刷新！** 扫描了 X 个目录，新建 Y 个索引页，更新 Z 个，跳过 W 个（无变化）。

---

## 关联 Skills

| Skill | 关系 |
|-------|------|
| `daily-paper-scout` | 上游（产出论文笔记） |
| `literature-management` | 平行（文献检索与管理） |
