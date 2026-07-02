# 编辑 DOCX 文档

> 完整 API（参数、返回值、正则示例、低层 XML 编辑）见 `references/edit-docx-api.md`。

通过 **bash 工具**执行文本替换（内部自动：解包 → 合并同样式 run → 替换 → 重打包 → 校验）：

```bash
bash "$SKILL_PATH_BASH/docx/scripts/docx.sh" edit /path/to/input.docx -o /path/to/output.docx \
  --replace "旧公司名称=新公司名称" \
  --replace "2024年=2025年"
```

**替换命中数为 0？** 通常是目标文本被 Word 拆成了多个 XML run，退回低层 `unpack` / `pack` 手动处理，详见 `references/edit-docx-api.md` "低层 XML 编辑"章节。

## 编辑规则

- `edit_docx()` 只做文本替换，不负责批注、修订和复杂域代码
- 解包时自动合并相邻同样式 run，提高命中率
- `pack_docx()` 自动修复常见的 XML 空白属性和 `durableId` 溢出问题

---

## Troubleshooting

| 问题 | 处理方式 |
|------|----------|
| `replacements_applied` 中某项 `count` 为 0 | 先 `bash "$SKILL_PATH_BASH/docx/scripts/docx.sh" unpack` 检查目标文本是否被拆成多个 XML run |
| `DOCX 验证失败` | 检查修改过的 XML 文件是否有语法错误 |
