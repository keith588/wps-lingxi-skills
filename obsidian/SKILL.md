---
name: obsidian
description: "Obsidian 知识库管理与自动化：读写笔记、搜索内容、管理标签和链接。"
description_zh: "Obsidian 知识库管理与自动化"
description_en: "Manage and automate Obsidian vaults"
version: 2.0.0
homepage: https://help.obsidian.md
---

# Obsidian Vault 管理

Obsidian vault = 磁盘上的普通文件夹，笔记 = `.md` 文件。

## 原则

**直接操作文件。** Obsidian 会实时感知文件变化（增删改），无需 obsidian-cli 也可以完整管理 vault。
仅在 obsidian-cli 可用时（`where obsidian-cli` 成功）才使用它，否则一律用 Python 文件操作。

## 定位 Vault

### Windows
- 配置文件: `%APPDATA%\Obsidian\obsidian.json`
- 读取 JSON，找 `"open": true` 的 vault 路径

### macOS
- 配置文件: `~/Library/Application Support/obsidian/obsidian.json`

### 多 vault
- 不要猜路径；从配置文件读取
- 如用户未指定 vault，提示用户选择或使用当前 open 的 vault

## 核心操作

### 读取笔记
```python
with open(os.path.join(vault_path, note_path), "r", encoding="utf-8") as f:
    content = f.read()
```

### 创建/编辑笔记
```python
with open(os.path.join(vault_path, note_path), "w", encoding="utf-8") as f:
    f.write(content)
```
- Obsidian 会自动刷新，无需重启
- 文件夹不存在时先 `os.makedirs()` 创建

### 搜索笔记
- **按文件名**: `glob.glob(os.path.join(vault_path, "**", f"*{query}*.md"), recursive=True)`
- **按内容**: 遍历 `.md` 文件，用字符串匹配或正则搜索
- **按标签**: 搜索 `#tag` 或 `tags: [tag1, tag2]` frontmatter

### 搜索内容（全文检索）
```python
import os, re
results = []
for root, dirs, files in os.walk(vault_path):
    # 跳过 .obsidian 目录
    dirs[:] = [d for d in dirs if d != ".obsidian"]
    for f in files:
        if f.endswith(".md"):
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, vault_path)
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            if query.lower() in content.lower():
                # 提取匹配行和上下文
                lines = content.splitlines()
                matches = [(i, line) for i, line in enumerate(lines) if query.lower() in line.lower()]
                results.append({"file": rel_path, "matches": matches})
```

### 移动/重命名笔记
```python
os.rename(old_path, new_path)
```
- 注意：直接 `os.rename` 不会更新 `[[wikilinks]]`，如有双向链接需要手动更新引用
- 如果 obsidian-cli 可用，优先用 `obsidian-cli move` 以自动更新链接

### 删除笔记
```python
os.remove(note_path)  # 或 send2trash
```

### 管理 Frontmatter
```python
import re
def get_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    return yaml.safe_load(m.group(1)) if m else {}

def set_frontmatter(content, data):
    fm_str = "---\n" + yaml.dump(data, allow_unicode=True) + "---"
    if content.startswith("---"):
        content = re.sub(r'^---.*?---', fm_str, content, count=1, flags=re.DOTALL)
    else:
        content = fm_str + "\n\n" + content
    return content
```

### 列出所有笔记
```python
notes = []
for root, dirs, files in os.walk(vault_path):
    dirs[:] = [d for d in dirs if d != ".obsidian"]
    for f in files:
        if f.endswith(".md"):
            notes.append(os.path.relpath(os.path.join(root, f), vault_path))
```

### 获取标签统计
```python
from collections import Counter
tags = Counter()
for root, dirs, files in os.walk(vault_path):
    dirs[:] = [d for d in dirs if d != ".obsidian"]
    for f in files:
        if f.endswith(".md"):
            with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            # frontmatter tags
            fm = get_frontmatter(content)
            if isinstance(fm.get("tags"), list):
                for t in fm["tags"]:
                    tags[t] += 1
            # inline tags
            for m in re.finditer(r'(?<!\w)#([\w/]+)', content):
                tags[m.group(1)] += 1
```

## obsidian-cli（可选增强）

当 `obsidian-cli` 在 PATH 中可用时，可使用其高级功能：
- `obsidian-cli search "query"` — 按笔记名搜索
- `obsidian-cli search-content "query"` — 全文搜索（带行号片段）
- `obsidian-cli create "path/note" --content "..." — 创建并打开
- `obsidian-cli move "old" "new"` — 安全重命名（自动更新 wikilinks）
- `obsidian-cli delete "path"` — 删除笔记

检测方式：
```python
import shutil
cli_available = shutil.which("obsidian-cli") is not None
```

## 注意事项

1. **不要修改 `.obsidian/` 目录下的文件**（除非用户明确要求），这是 Obsidian 内部配置
2. **编码始终用 UTF-8**
3. **路径用 `os.path.join()`** 构造，不要硬编码分隔符
4. **创建文件夹时用 `os.makedirs(exist_ok=True)`**
5. **删除文件时优先用 `send2trash`**（可恢复），而非 `os.remove`
6. **大 vault 搜索时加进度反馈**，避免长时间无响应
