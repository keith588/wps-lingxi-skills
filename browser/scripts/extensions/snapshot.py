import os
import time
import asyncio
from pathlib import Path

import core


class SnapshotExtension(core.Extension):
    MAX_TEXT_LEN = 10000
    MAX_ELEMENTS = 100

    def __init__(self, browser: core.Browser):
        super().__init__(browser)  # self.browser = browser
        self._last_backend_node_ids: list[int] = []

    async def get_backend_node_id(self, element_index: int) -> int:
        if element_index < 0 or element_index >= len(self._last_backend_node_ids):
            raise IndexError(
                f"element_index={element_index} 超出范围，"
                f"当前共 {len(self._last_backend_node_ids)} 个元素，"
                f"请先调用 get_interactive_elements() 刷新列表"
            )
        backend_node_id = self._last_backend_node_ids[element_index]
        if backend_node_id < 0:
            raise RuntimeError(
                f"element_index={element_index} 对应的 backendNodeId 无效"
            )
        return backend_node_id

    async def extract_page_text(self) -> str:
        raw = await self.browser.evaluate(
            "(function(){ return document.body ? document.body.innerText : ''; })()"
        )
        result = []
        for line in str(raw or "").splitlines():
            s = line.strip()
            if not s or len(s) > 1000:
                continue
            alnum = sum(1 for c in s if c.isalnum() or "\u4e00" <= c <= "\u9fff")
            if alnum >= len(s) * 0.3:
                result.append(s)
        return "\n".join(result)

    async def extract_elements(self) -> str:
        # CDP 按 DOM 顺序返回 backendNodeId，与 JS querySelectorAll 顺序严格一致
        all_backend_node_ids = await self.browser.query_selector_all(
            "a, button, input, select, textarea"
        )

        # JS 纯只读：可见性过滤 + 属性采集，返回结构化列表
        items: list[dict] = (
            await self.browser.evaluate(
                """
(function() {
    var MAX = 200;
    var all = Array.from(document.querySelectorAll('a, button, input, select, textarea'));
    var result = [];
    var visible_count = 0;
    for (var i = 0; i < all.length && visible_count < MAX; i++) {
        var el = all[i];
        var r = el.getBoundingClientRect();
        var s = window.getComputedStyle(el);
        if (r.width <= 0 || r.height <= 0
                || s.visibility === 'hidden'
                || s.display === 'none'
                || parseFloat(s.opacity || '1') <= 0) continue;

        var tag = el.tagName.toLowerCase();
        var type = (el.getAttribute('type') || '').toLowerCase();
        if (tag === 'input' && type === 'hidden') continue;

        var parts = [tag];
        if (type && type !== tag) parts.push('type="' + type + '"');
        var name = el.getAttribute('name') || '';
        if (name) parts.push('name="' + name + '"');
        var ph = el.getAttribute('placeholder') || '';
        if (ph) parts.push('placeholder="' + ph.substring(0, 40) + '"');
        var href = el.getAttribute('href') || '';
        if (href) parts.push('href="' + href.substring(0, 60) + '"');

        var display = '';
        if (tag === 'select') {
            var opts = Array.from(el.options).map(function(o) { return o.text.trim(); });
            var sel = el.options[el.selectedIndex]
                ? el.options[el.selectedIndex].text.trim() : '';
            var optsStr = opts.slice(0, 10).join(' / ');
            if (opts.length > 10) optsStr += ' \u2026 (+' + (opts.length - 10) + ')';
            display = 'selected="' + sel + '" options=[' + optsStr + ']';
        } else if (tag === 'input' && el.value) {
            display = el.value.substring(0, 40);
        } else {
            display = (el.innerText || '').trim().substring(0, 60);
        }

        var desc = parts.join(' ');
        if (display) desc += ' | ' + display;
        result.push({domIdx: i, desc: desc});
        visible_count++;
    }
    return result;
})()
"""
            )
            or []
        )

        # 用 domIdx 将可见元素映射到对应的 CDP backendNodeId
        self._last_backend_node_ids = [
            (
                all_backend_node_ids[item["domIdx"]]
                if item["domIdx"] < len(all_backend_node_ids)
                else -1
            )
            for item in items
        ]
        return "\n".join(f"{i}[:] {item['desc']}" for i, item in enumerate(items))

    def _save_text(self, text: str, prefix: str) -> str:
        workspace = Path(os.environ.get("WORKSPACE_DIR", "/tmp"))
        filename = f"{prefix}_{time.time_ns()}.txt"
        path = workspace / filename
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except Exception:
            path = Path("/tmp") / filename
            path.write_text(text, encoding="utf-8")
        return str(path)

    async def snapshot(self) -> str:
        page_text = await self.extract_page_text()
        elements = await self.extract_elements()
        # 元素与文本同时为空，通常是页面内容尚在异步渲染（如搜索结果懒加载），
        # 短暂等待后重试一次，避免快照抓到空页面、调用方被迫再手动刷新。
        if not page_text.strip() and not elements.strip():
            await asyncio.sleep(1)
            page_text = await self.extract_page_text()
            elements = await self.extract_elements()
        title = await self.browser.evaluate("document.title") or ""
        url = await self.browser.evaluate("location.href") or ""

        text_note = ""
        if len(page_text) > self.MAX_TEXT_LEN:
            saved = self._save_text(page_text, "page_text")
            text_note = f"\n[文本共 {len(page_text)} 字符，此处显示前 {self.MAX_TEXT_LEN} 字符，完整内容已保存至 {saved}]"
            page_text = page_text[: self.MAX_TEXT_LEN]

        elements_note = ""
        element_lines = elements.splitlines()
        if len(element_lines) > self.MAX_ELEMENTS:
            saved = self._save_text(elements, "page_elements")
            elements_note = f"\n[可交互元素共 {len(element_lines)} 个，此处显示前 {self.MAX_ELEMENTS} 个，完整列表已保存至 {saved}]"
            elements = "\n".join(element_lines[: self.MAX_ELEMENTS])

        return "\n".join(
            [
                "---",
                f"Title: {title}",
                f"URL: {url}",
                "---",
                "Interactive elements (index[:]info):",
                elements + elements_note,
                "---",
                "Page Text:",
                page_text + text_note,
            ]
        )
