from __future__ import annotations

import base64
from typing import Any, Callable

import httpx
from cdp_use.client import CDPClient


class EvaluateError(Exception):
    def __init__(self, description: str):
        self.description = description

    def __str__(self):
        return self.description


class Extension:
    def __init__(self, browser: Browser):
        self.browser = browser

    async def call(self, action: str, *args: Any, **kwargs: Any) -> Any:
        handler = getattr(self, action, None)
        if handler is None:
            raise ValueError(f"Action {action} not found")
        return await handler(*args, **kwargs)


class Browser:
    def __init__(self, cdp: CDPClient):
        self._cdp = cdp
        self._session_id: str = ""
        self._extensions: dict[str, Extension] = {}

    @classmethod
    async def create(cls, cdp_endpoint: str) -> Browser:
        """创建浏览器实例"""

        async with httpx.AsyncClient() as client:
            r = await client.get(f"{cdp_endpoint}/json/version", timeout=10)
        r.raise_for_status()
        ws_url = r.json()["webSocketDebuggerUrl"]
        cdp = CDPClient(ws_url)
        await cdp.start()
        return cls(cdp)

    @staticmethod
    def with_dom(fn: Callable) -> Callable:
        """使用 DOM 域装饰器"""

        async def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            await self._cdp.send.DOM.enable(params={}, session_id=self._session_id)
            try:
                ret = await fn(self, *args, **kwargs)
            finally:
                await self._cdp.send.DOM.disable(params={}, session_id=self._session_id)
            return ret

        return wrapper

    async def is_healthy(self) -> bool:
        """健康检查"""

        try:
            await self._cdp.send.Browser.getVersion(params={})
            return True
        except Exception:
            return False

    async def attach_to_target(self, target_id: str) -> None:
        if self._session_id:
            await self._cdp.send.Target.detachFromTarget(
                params={"sessionId": self._session_id}
            )
        ret = await self._cdp.send.Target.attachToTarget(
            params={"targetId": target_id, "flatten": True}
        )
        self._session_id = ret["sessionId"]

    async def create_and_attach_target(self, url: str) -> None:
        ret = await self._cdp.send.Target.createTarget(params={"url": "about:blank"})
        target_id = ret["targetId"]
        await self.attach_to_target(target_id)
        await self._cdp.send.Page.navigate(
            params={"url": url},
            session_id=self._session_id,
        )

    async def get_targets(self) -> list[str]:
        ret = await self._cdp.send.Target.getTargets(params={})
        return list(
            filter(
                lambda x: x["type"] == "page" and not x["url"].startswith("chrome://"),
                ret["targetInfos"],
            )
        )

    async def evaluate(self, script: str, timeout: float = 60) -> Any:
        """执行 JS 表达式并返回结果"""

        ret = await self._cdp.send.Runtime.evaluate(
            params={
                "expression": script,
                "returnByValue": True,
                "userGesture": True,
                "awaitPromise": True,
                "timeout": int(timeout * 1000),
                "allowUnsafeEvalBlockedByCsp": True,
            },
            session_id=self._session_id,
        )
        if "exceptionDetails" in ret:
            raise EvaluateError(ret["exceptionDetails"]["exception"]["description"])
        return ret["result"].get("value")

    @with_dom
    async def call_function_on_backend_node(
        self, backend_node_id: int, function_declaration: str
    ) -> Any:
        ret = await self._cdp.send.DOM.resolveNode(
            params={"backendNodeId": backend_node_id},
            session_id=self._session_id,
        )
        object_id = ret["object"]["objectId"]

        ret = await self._cdp.send.Runtime.callFunctionOn(
            params={
                "functionDeclaration": function_declaration,
                "objectId": object_id,
                "returnByValue": True,
            },
            session_id=self._session_id,
        )
        if "exceptionDetails" in ret:
            raise EvaluateError(ret["exceptionDetails"]["exception"]["description"])
        return ret["result"].get("value")

    @with_dom
    async def query_selector_all(self, selector: str) -> list[int]:
        ret = await self._cdp.send.DOM.getDocument(
            params={"depth": -1},
            session_id=self._session_id,
        )
        # 遍历树，建立 nodeId → backendNodeId 映射
        node_map: dict[int, int] = {}
        stack: list[dict] = [ret["root"]]
        while stack:
            node = stack.pop()
            node_map[node["nodeId"]] = node.get("backendNodeId", -1)
            stack.extend(node.get("children", []))

        root_node_id = ret["root"]["nodeId"]
        ret = await self._cdp.send.DOM.querySelectorAll(
            params={"nodeId": root_node_id, "selector": selector},
            session_id=self._session_id,
        )
        return [node_map.get(nid, -1) for nid in ret["nodeIds"]]

    @with_dom
    async def scroll_into_view(self, backend_node_id: int) -> None:
        await self._cdp.send.DOM.scrollIntoViewIfNeeded(
            params={"backendNodeId": backend_node_id},
            session_id=self._session_id,
        )

    @with_dom
    async def focus(self, backend_node_id: int) -> None:
        await self._cdp.send.DOM.focus(
            params={"backendNodeId": backend_node_id},
            session_id=self._session_id,
        )

    async def insert_text(self, text: str) -> None:
        """向当前聚焦元素插入文本（替换当前选区，走浏览器输入管道）。"""
        await self._cdp.send.Input.insertText(
            params={"text": text},
            session_id=self._session_id,
        )

    # CDP 仅靠 key 名无法触发默认行为（如回车提交表单），需补全
    # windowsVirtualKeyCode + code + text，否则只派发 DOM 事件而不执行默认动作。
    _KEY_META = {
        "Enter": {"code": "Enter", "windowsVirtualKeyCode": 13, "text": "\r"},
        "Tab": {"code": "Tab", "windowsVirtualKeyCode": 9, "text": "\t"},
        "Backspace": {"code": "Backspace", "windowsVirtualKeyCode": 8},
        "Delete": {"code": "Delete", "windowsVirtualKeyCode": 46},
        "Escape": {"code": "Escape", "windowsVirtualKeyCode": 27},
        "ArrowUp": {"code": "ArrowUp", "windowsVirtualKeyCode": 38},
        "ArrowDown": {"code": "ArrowDown", "windowsVirtualKeyCode": 40},
        "ArrowLeft": {"code": "ArrowLeft", "windowsVirtualKeyCode": 37},
        "ArrowRight": {"code": "ArrowRight", "windowsVirtualKeyCode": 39},
    }

    async def key_event(self, key: str, modifiers: int = 0) -> None:
        """modifiers: 1=Alt 2=Ctrl 4=Meta 8=Shift"""
        meta = self._KEY_META.get(key, {})
        for event_type in ("keyDown", "keyUp"):
            params = {"type": event_type, "key": key, "modifiers": modifiers}
            if "code" in meta:
                params["code"] = meta["code"]
            if "windowsVirtualKeyCode" in meta:
                params["windowsVirtualKeyCode"] = meta["windowsVirtualKeyCode"]
                params["nativeVirtualKeyCode"] = meta["windowsVirtualKeyCode"]
            # text 只在 keyDown 携带，用于触发 char 事件与默认动作
            if event_type == "keyDown" and "text" in meta:
                params["text"] = meta["text"]
            await self._cdp.send.Input.dispatchKeyEvent(
                params=params,
                session_id=self._session_id,
            )

    async def screenshot(
        self, format: str = "jpeg", quality: int = 90, full_page: bool = False
    ) -> bytes:
        if format not in ("jpeg", "png"):
            raise ValueError(f"Invalid format: {format}")
        if quality not in range(0, 101):
            raise ValueError(f"Invalid quality: {quality}")
        params = {
            "format": format,
            "captureBeyondViewport": full_page,
        }
        if format == "jpeg":
            params["quality"] = quality

        ret = await self._cdp.send.Page.captureScreenshot(
            params=params,
            session_id=self._session_id,
        )
        return base64.b64decode(ret["data"])

    async def export_to_pdf(self) -> bytes:
        ret = await self._cdp.send.Page.printToPDF(
            params={},
            session_id=self._session_id,
        )
        return base64.b64decode(ret["data"])

    def register_extension(
        self, name: str, extension_class: Callable[[Browser], Extension]
    ) -> None:
        self._extensions[name] = extension_class(self)

    async def call_extension(
        self, name: str, action: str, *args: Any, **kwargs: Any
    ) -> Any:
        return await self._extensions[name].call(action, *args, **kwargs)
