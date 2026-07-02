import json
from typing import TypedDict

import core, util


async def _snapshot() -> str:
    browser = await util.get_browser()

    return await browser.call_extension("snapshot", "snapshot")


async def _display_screenshot() -> None:
    try:
        browser = await util.get_browser()
        data = await browser.screenshot(format="jpeg", quality=90, full_page=False)
        display(Image(data=data))  # type: ignore
    except Exception:
        pass


class NavigateResult(TypedDict):
    snapshot: str | None


async def navigate(
    url: str,
    with_snapshot: bool = False,
    with_screenshot: bool = False,
) -> NavigateResult:
    browser = await util.get_browser()

    await browser.create_and_attach_target(url)
    await util.wait_dom_content_loaded(browser)
    util.save_url(url)

    snapshot = None
    if with_snapshot:
        snapshot = await _snapshot()
    if with_screenshot:
        await _display_screenshot()

    return {"snapshot": snapshot}


class ClickResult(TypedDict):
    snapshot: str | None


async def click(
    element_index: int,
    with_snapshot: bool = False,
    with_screenshot: bool = False,
) -> ClickResult:
    browser = await util.get_browser()

    async with util.BrowserAutoSwitchTarget(browser):
        backend_node_id = await browser.call_extension(
            "snapshot", "get_backend_node_id", element_index
        )
        await browser.scroll_into_view(backend_node_id)
        await browser.call_function_on_backend_node(
            backend_node_id, "function() { this.click(); }"
        )

    snapshot = None
    if with_snapshot:
        snapshot = await _snapshot()
    if with_screenshot:
        await _display_screenshot()

    return {"snapshot": snapshot}


class FillResult(TypedDict):
    snapshot: str | None


async def fill(
    element_index: int,
    text: str,
    press_enter: bool = False,
    with_snapshot: bool = False,
    with_screenshot: bool = False,
) -> FillResult:
    browser = await util.get_browser()

    async with util.BrowserAutoSwitchTarget(browser):
        backend_node_id = await browser.call_extension(
            "snapshot", "get_backend_node_id", element_index
        )
        await browser.scroll_into_view(backend_node_id)
        await browser.focus(backend_node_id)
        await browser.call_function_on_backend_node(
            backend_node_id, "function() { this.value = ''; }"
        )
        await browser.insert_text(text)
        if press_enter:
            await browser.key_event("Enter")

    snapshot = None
    if with_snapshot:
        snapshot = await _snapshot()
    if with_screenshot:
        await _display_screenshot()

    return {"snapshot": snapshot}


class SelectOptionResult(TypedDict):
    snapshot: str | None


async def select_option(
    element_index: int,
    option_text: str | None = None,
    option_value: str | None = None,
    option_index: int | None = None,
    with_snapshot: bool = False,
    with_screenshot: bool = False,
) -> SelectOptionResult:
    browser = await util.get_browser()

    async with util.BrowserAutoSwitchTarget(browser):
        backend_node_id = await browser.call_extension(
            "snapshot", "get_backend_node_id", element_index
        )
        await browser.scroll_into_view(backend_node_id)
        label_j = json.dumps(option_text)
        val_j = json.dumps(option_value)
        idx_j = json.dumps(option_index)
        await browser.call_function_on_backend_node(
            backend_node_id,
            f"""function() {{
    const opts = Array.from(this.options);
    let idx = -1;
    const label = {label_j};
    const val = {val_j};
    const i = {idx_j};
    if (label !== null) {{
        idx = opts.findIndex(o => (o.text || '').trim() === label);
    }} else if (val !== null) {{
        idx = opts.findIndex(o => o.value === val);
    }} else if (i !== null && i !== undefined) {{
        idx = i;
    }}
    if (idx < 0 || idx >= opts.length) {{
        throw new Error('未找到匹配的 option 或索引无效');
    }}
    this.selectedIndex = idx;
    this.dispatchEvent(new Event('input', {{ bubbles: true }}));
    this.dispatchEvent(new Event('change', {{ bubbles: true }}));
}}""",
        )

    snapshot = None
    if with_snapshot:
        snapshot = await _snapshot()
    if with_screenshot:
        await _display_screenshot()

    return {"snapshot": snapshot}


class GetInteractiveElementsResult(TypedDict):
    interactive_elements: list[dict]


async def get_interactive_elements() -> GetInteractiveElementsResult:
    browser = await util.get_browser()
    interactive_elements = await browser.call_extension("snapshot", "extract_elements")
    return {"interactive_elements": interactive_elements}


class ExecuteScriptResult(TypedDict):
    result: str | None


async def execute_script(script: str) -> ExecuteScriptResult:
    browser = await util.get_browser()

    result = None
    async with util.BrowserAutoSwitchTarget(browser):
        try:
            result = await browser.evaluate(script)
        except core.EvaluateError as e:
            # 顶层 return 在裸表达式里非法；包进 IIFE 后重试，兼容 `return ...` 写法。
            # 仅在确实是 Illegal return 时重试，避免破坏裸表达式/自包 IIFE 的写法。
            if "Illegal return" in e.description:
                try:
                    result = await browser.evaluate(f"(function() {{\n{script}\n}})()")
                except core.EvaluateError as e2:
                    result = e2.description
            else:
                result = e.description

    return {"result": result}


class ScreenshotResult(TypedDict):
    data: bytes | None


async def screenshot(
    format: str = "jpeg", quality: int = 90, full_page: bool = False
) -> ScreenshotResult:
    browser = await util.get_browser()
    data = await browser.screenshot(format=format, quality=quality, full_page=full_page)
    return {"data": data}


class RequestManualResult(TypedDict):
    success: bool


async def request_manual() -> None:
    browser = await util.get_browser(manual=True)
    url = util.load_url()
    await browser.create_and_attach_target(url)
    await util.wait_dom_content_loaded(browser)


class ExportToPdfResult(TypedDict):
    data: bytes | None


async def export_to_pdf() -> ExportToPdfResult:
    browser = await util.get_browser()
    data = await browser.export_to_pdf()
    return {"data": data}
