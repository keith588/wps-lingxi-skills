from pathlib import Path

import api
import util


def _make_error_message(action: str, e: Exception) -> str:
    if isinstance(e, TimeoutError):
        return f"{action} 超时"
    extra_info = ""
    if (
        action != "navigate"
        and isinstance(e, RuntimeError)
        and len(e.args) > 0
        and isinstance(e.args[0], dict)
        and "code" in e.args[0]
        and e.args[0]["code"] == -32601  # 'action' wasn't found
    ):
        extra_info += f"\n浏览器可能已关闭，请先执行 navigate 操作打开浏览器，再重新执行 {action} 操作"
    return f"{action} 失败：\n{e}{extra_info}"


def navigate(url: str) -> str:
    action = "navigate"
    try:
        result: api.NavigateResult = util.run_coroutine_threadsafe(
            api.navigate(url, with_snapshot=True, with_screenshot=True)
        )
    except Exception as e:
        return _make_error_message(action, e)
    return f"{action} 成功：\n{result['snapshot']}"


def click(element_index: int) -> str:
    action = "click"
    try:
        result: api.ClickResult = util.run_coroutine_threadsafe(
            api.click(element_index, with_snapshot=True, with_screenshot=True)
        )
    except Exception as e:
        return _make_error_message(action, e)
    return f"{action} 成功：\n{result['snapshot']}"


def fill(element_index: int, text: str, press_enter: bool = False) -> str:
    action = "fill"
    try:
        result: api.FillResult = util.run_coroutine_threadsafe(
            api.fill(
                element_index,
                text,
                press_enter,
                with_snapshot=True,
                with_screenshot=True,
            )
        )
    except Exception as e:
        return _make_error_message(action, e)
    return f"{action} 成功：\n{result['snapshot']}"


def select_option(
    element_index: int,
    option_text: str | None = None,
    option_value: str | None = None,
    option_index: int | None = None,
) -> str:
    action = "select_option"
    try:
        result: api.SelectOptionResult = util.run_coroutine_threadsafe(
            api.select_option(
                element_index,
                option_text,
                option_value,
                option_index,
                with_snapshot=True,
                with_screenshot=True,
            )
        )
    except Exception as e:
        return _make_error_message(action, e)
    return f"{action} 成功：\n{result['snapshot']}"


def get_interactive_elements() -> str:
    action = "get_interactive_elements"
    try:
        result: api.GetInteractiveElementsResult = util.run_coroutine_threadsafe(
            api.get_interactive_elements()
        )
    except TimeoutError:
        return f"{action} 超时"
    except Exception as e:
        return f"{action} 失败：\n{e}"
    return f"{action} 成功：\n{result['interactive_elements']}"


def execute_script(script: str) -> str:
    action = "execute_script"
    try:
        result: api.ExecuteScriptResult = util.run_coroutine_threadsafe(
            api.execute_script(script)
        )
    except Exception as e:
        return _make_error_message(action, e)
    return f"{action} 成功：\n{result['result']}"


def screenshot(output: str = "screenshot.jpg", full_page: bool = False) -> str:
    action = "screenshot"
    data = None
    try:
        output_path = Path(output).resolve()
        result: api.ScreenshotResult = util.run_coroutine_threadsafe(
            api.screenshot(
                format={".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png"}.get(
                    output_path.suffix, "jpeg"
                ),
                quality=90,
                full_page=full_page,
            )
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = result["data"]
        output_path.write_bytes(data)
    except Exception as e:
        return _make_error_message(action, e)

    try:
        display(Image(data=data))  # type: ignore
    except Exception:
        pass

    return f"{action} 成功：\n截图已保存到 {output_path}"


def request_manual() -> str:
    action = "request_manual"
    try:
        util.run_coroutine_threadsafe(api.request_manual())
    except Exception as e:
        return _make_error_message(action, e)
    return f"{action} 成功：\n请立即停止当前对话，告知用户浏览器已弹出，请在浏览器窗口中手动完成所需操作，完成后发起新的提问以继续"


__all__ = [
    "navigate",
    "click",
    "fill",
    "select_option",
    "get_interactive_elements",
    "execute_script",
    "screenshot",
    "request_manual",
]
