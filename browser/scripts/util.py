import json
import asyncio
import threading
from typing import Any, Coroutine
from pathlib import Path
import os
import logging

import core
from extensions.snapshot import SnapshotExtension


logger = logging.getLogger(__name__)

_loop: asyncio.AbstractEventLoop | None = None
_browser: core.Browser | None = None


def _ensure_loop() -> None:
    """检测 _loop 是否存活，损坏时重建 loop 和后台线程，并重置 browser。"""
    global _loop, _browser
    if _loop is not None and not _loop.is_closed() and _loop.is_running():
        return
    _browser = None
    _loop = asyncio.new_event_loop()
    threading.Thread(target=_loop.run_forever, daemon=True).start()


def run_coroutine_threadsafe(coroutine: Coroutine, timeout: float = 60) -> Any:
    global _loop
    _ensure_loop()
    future = asyncio.run_coroutine_threadsafe(coroutine, _loop)
    return future.result(timeout)


def _parse_browser_config(response: str) -> str:
    browser_config = json.loads(response)
    if browser_config.get("type") == "cdp":
        return browser_config["cdp_endpoint"]
    raise RuntimeError("未找到 cdp_endpoint")


def _get_cdp_endpoint() -> str:
    """向 localserver 请求 cdp_endpoint"""
    response = input(r"__BRWS_REQ__{}")
    return _parse_browser_config(response)


def _request_browser_manual() -> str:
    """向 localserver 请求浏览器手动操作"""
    response = input(r"__BRWS_MAN__{}")
    return _parse_browser_config(response)


async def get_browser(manual: bool = False) -> core.Browser:
    def init_browser(browser: core.Browser) -> None:
        browser.register_extension("snapshot", SnapshotExtension)

    global _browser
    if manual:
        _browser = await core.Browser.create(_request_browser_manual())
        init_browser(_browser)
    elif _browser is None or not await _browser.is_healthy():
        _browser = await core.Browser.create(_get_cdp_endpoint())
        init_browser(_browser)
    return _browser


async def switch_to_new_tab_if_opened(
    browser: core.Browser,
    old_targets: list[dict[str, Any]],
    new_targets: list[dict[str, Any]],
) -> bool:
    old_target_ids = {}
    for target in old_targets:
        old_target_ids[target["targetId"]] = target
    for target in new_targets:
        if target["targetId"] not in old_target_ids:
            await browser.attach_to_target(target["targetId"])
            return True
    return False


async def wait_dom_content_loaded(browser: core.Browser) -> None:
    await asyncio.sleep(1)
    await browser.evaluate(
        """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined, configurable: true });

(() => {
    if (document.readyState === 'complete') return Promise.resolve(null);
    return new Promise((resolve) => {
        window.addEventListener('load', () => resolve(null), { once: true });
    });
})()
""",
        timeout=15,
    )
    await wait_dom_stable(browser)


async def wait_dom_stable(
    browser: core.Browser,
    max_wait: float = 3.0,
    interval: float = 0.4,
    stable_rounds: int = 2,
) -> None:
    """等待 DOM 内容趋于稳定。

    `load` 事件只保证资源加载完成，但很多页面（如搜索结果）的正文是在 load
    之后才由 JS 异步注入的，此时抓快照只能拿到页面外壳。这里轮询页面内容规模
    （可见文本长度 + 可交互元素数），连续 `stable_rounds` 次不再变化即认为渲染
    完成；`max_wait` 秒兜底，避免长轮询/不断刷新的页面无限等待。
    """
    prev = -1
    stable = 0
    waited = 0.0
    while waited < max_wait:
        try:
            size = (
                await browser.evaluate(
                    "(function(){"
                    "var t=document.body?document.body.innerText.length:0;"
                    "var n=document.querySelectorAll('a,button,input,select,textarea').length;"
                    "return t+n;})()"
                )
                or 0
            )
        except Exception:
            return  # 导航中执行上下文失效等异常，停止等待，交由后续快照/重试兜底
        if size == prev:
            stable += 1
            if stable >= stable_rounds:
                return
        else:
            stable = 0
            prev = size
        await asyncio.sleep(interval)
        waited += interval


class BrowserAutoSwitchTarget:
    def __init__(self, browser: core.Browser):
        self.browser = browser

    async def __aenter__(self):
        self.old_targets = await self.browser.get_targets()
        self.old_url = await self.browser.evaluate(
            "(function(){ return window.location.href; })()"
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await asyncio.sleep(0.2)
        new_targets = await self.browser.get_targets()
        if await switch_to_new_tab_if_opened(
            self.browser, self.old_targets, new_targets
        ):
            await asyncio.sleep(1)  # 等待新页面的 Runtime 初始化完成
            await wait_dom_content_loaded(self.browser)
        elif (
            await self.browser.evaluate(
                "(function(){ return window.location.href; })()"
            )
            != self.old_url
        ):
            # 同标签页内发生了导航（URL 变化），同样需等待加载完成，
            # 否则快照会在内容渲染前抓取，导致元素/文本为空。
            await wait_dom_content_loaded(self.browser)
        url = await self.browser.evaluate(
            "(function(){ return window.location.href; })()"
        )
        save_url(url)
        return False


def _get_url_path() -> Path:
    workspace = Path(os.environ.get("WORKSPACE_DIR", "/tmp"))
    return (workspace / ".rundata" / "browser" / "url.txt").resolve()


def save_url(url: str) -> None:
    path = _get_url_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(url, encoding="utf-8")
    except Exception:
        logger.warning("Failed to save URL to %s", path)


def load_url() -> str:
    try:
        return _get_url_path().read_text(encoding="utf-8").strip()
    except Exception:
        return "about:blank"
