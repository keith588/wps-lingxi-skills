---
name: pptx
description: "当需要执行操作 PPT/幻灯片 的行为时使用本技能，包括：创建或生成幻灯片、演示文稿，读取/解析/提取现有 .pptx 文件中的内容，编辑PPT版式与内容、套用模板与布局等操作对象或产物为PPT的行为。"

---

# PPTX

## 调用方式

所有操作通过 bash 一行调用完成：

```bash
bash "$SKILL_PATH_BASH/pptx/scripts/pptx.sh" <command> <args>
```

### 命令速查

| 分类 | 命令 | 说明 |
|------|------|------|
| 查询 | `query` | 查询幻灯片内容和布局 |
| 查询 | `query-shape` | 查询指定元素的详细信息 |
| 编辑 | `edit-text` | 修改元素文字内容和格式 |
| 编辑 | `copy-shape` | 复制元素 |
| 编辑 | `delete-shape` | 删除元素 |
| 编辑 | `move-shape` | 移动元素或同时调整尺寸 |
| 编辑 | `resize-shape` | 仅调整元素尺寸 |
| 编辑 | `slide-organize` | 页面增删/复制/排序 |
| 编辑 | `export-image` | 导出元素中的图片 |
| 编辑 | `replace-image` | 替换元素中的图片 |
| 编辑 | `get-fonts` | 查询系统可用字体 |
| 生成 | `check-layout` | 检查 HTML 幻灯片跑版 |
| 生成 | `html-to-pptx` | HTML 幻灯片转 PPTX |
| 生成 | `screenshot` | 导出幻灯片截图 |

## PPTX 读取
当用户要求：打开 / 解析 / 提取现有 PPT 内容时，请阅读 skills/pptx/read_ppt.md 获取更多指导。

## PPTX 生成
当用户要求：创建 PPT / 将文档转换为 PPT 时，请阅读 skills/pptx/gen_ppt.md 获取更多指导。

## PPTX 编辑
当用户要求修改上传的 PPT 时，请阅读 skills/pptx/edit_ppt.md 获取更多指导。

## PPTX 讲稿
当用户要求基于 PPT 生成演讲稿时，请阅读 skills/pptx/ppt_speech_writer.md 获取更多指导。

# 注意

## 基本指南
1. 文件读取规则：
- 对于`skills/pptx/`目录下的文件，在任务执行过程中必须按照工作步骤执行到特定环节时，**按需读取**。**禁止**在执行任务前读取所有指南和规范文档。
