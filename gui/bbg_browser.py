"""Receive __NEXT_DATA__ from the user's browser extension over loopback HTTP."""

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import urlsplit
import webbrowser


MAX_MESSAGE_BYTES = 16 * 1024 * 1024
EXTENSION_DIRECTORY = Path(__file__).resolve().parents[1] / "browser_extensions" / "bloomberg_bridge"


class BrowserReadError(RuntimeError):
    pass


def article_key(url):
    """Allow the www/canonical redirect and tracking-query changes, not other articles."""
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in
            {"www.bloomberg.com", "bloomberg.com"} or parsed.username or
            parsed.password or parsed.port not in (None, 443)):
        raise BrowserReadError("请使用有效的 https://www.bloomberg.com/ 文章链接。")
    return parsed.path.rstrip("/")


def validate_article_dict(article_dict):
    """Validate every field accessed by the unchanged edit_bbg_article loop.

    Do not rewrite the document or synthesize article content. An incompatible
    document must take the existing (False, {'error': ...}) branch instead.
    """
    value = article_dict
    for key in ("props", "pageProps", "story", "body", "content"):
        if not isinstance(value, dict) or key not in value:
            raise BrowserReadError(
                "已读取 __NEXT_DATA__，但缺少 props.pageProps.story.body.content；"
                "页面可能仅提供订阅提示，或文章数据结构已变化。")
        value = value[key]
    if not isinstance(value, list):
        raise BrowserReadError("__NEXT_DATA__ 中的文章 content 不是列表。")

    def objects(items):
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise BrowserReadError("__NEXT_DATA__ 的段落节点格式不符合原文章解析逻辑。")
        return items

    def text_value(item):
        if item.get("type") == "text" and not isinstance(item.get("value", ""), str):
            raise BrowserReadError("__NEXT_DATA__ 的文字 value 不是字符串。")

    for block in objects(value):
        if block.get("type") != "paragraph":
            continue
        for item in objects(block.get("content", [])):
            text_value(item)
            if item.get("type") in ("entity", "link"):
                for child in objects(item.get("content", [])):
                    text_value(child)
    return article_dict


class _Request:
    def __init__(self, url, timeout):
        self.url = url
        self.token = secrets.token_urlsafe(32)
        self.deadline = time.monotonic() + timeout
        self.connected = threading.Event()
        self.done = threading.Event()
        self.lock = threading.Lock()
        self.raw_json = None
        self.error = None


class _BridgeHandler(BaseHTTPRequestHandler):
    # Requests and secrets must not be written to the normal HTTP access log.
    def log_message(self, *_args):
        pass

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def _reply(self, status, payload, content_type="application/json; charset=utf-8"):
        body = payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        origin = self.headers.get("Origin", "")
        if re.fullmatch(r"chrome-extension://[a-p]{32}", origin):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _authorized(self):
        expected_host = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != expected_host:
            self._reply(403, {"error": "Invalid host"})
            return False
        auth = self.headers.get("Authorization", "")
        if not secrets.compare_digest(auth, "Bearer " + self.server.request_state.token):
            self._reply(403, {"error": "Invalid request token"})
            return False
        if time.monotonic() > self.server.request_state.deadline or self.server.request_state.done.is_set():
            self._reply(410, {"error": "Request expired"})
            return False
        return True

    def do_GET(self):
        if self.path == "/bbg/connect":
            folder = html.escape(str(EXTENSION_DIRECTORY))
            page = f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>Macro Dashboard · 浏览器连接</title>
<style>body{{font:17px/1.7 system-ui;max-width:760px;margin:64px auto;padding:0 24px}}
code{{background:#eee;padding:4px;overflow-wrap:anywhere}}</style>
<h1>正在连接浏览器扩展</h1>
<p id="status">连接成功后，此标签页会自动打开你请求的文章。</p>
<p>首次使用时，请在这个浏览器中加载扩展：</p>
<ol><li>进入 Chrome 或 Edge 的“扩展 → 管理扩展”，开启开发者模式。</li>
<li>点击“加载已解压的扩展”，选择这个文件夹：<br><code>{folder}</code></li>
<li>回到本页刷新；如果工作台已提示超时，请重新点击工作台的文章加载按钮。</li></ol>
<p>请使用你平时能正常打开彭博的浏览器和用户配置。无需打开 F12。</p></html>"""
            self._reply(200, page, "text/html; charset=utf-8")
            return
        if self.path != "/request":
            self._reply(404, {"error": "Not found"})
            return
        if self._authorized():
            state = self.server.request_state
            state.connected.set()
            self._reply(200, {"protocol": 1, "url": state.url,
                              "timeout_ms": max(1, int((state.deadline - time.monotonic()) * 1000))})

    def do_POST(self):
        if self.path != "/result":
            self._reply(404, {"error": "Not found"})
            return
        if not self._authorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_MESSAGE_BYTES:
                self._reply(413, {"error": "Invalid message size"})
                return
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Expected application/json")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object")
            state = self.server.request_state
            if article_key(payload.get("url", "")) != article_key(state.url):
                raise ValueError("Article URL does not match the request")
            raw_json, error = payload.get("json"), payload.get("error")
            if not (isinstance(raw_json, str) and raw_json.strip()) and not (isinstance(error, str) and error):
                raise ValueError("Missing article JSON or error")
        except (ValueError, TypeError, AttributeError, BrowserReadError) as exc:
            self._reply(400, {"error": str(exc)})
            return
        with state.lock:
            if state.done.is_set():
                self._reply(410, {"error": "Request already completed"})
                return
            state.raw_json, state.error = raw_json, error
            try:
                self._reply(200, {"ok": True})
            finally:
                state.done.set()


class BloombergBrowser:
    """A normal browser plus a temporary receiver; owns no browser windows."""

    def __init__(self, timeout=180):
        self.timeout = timeout
        self._active = None
        self._lock = threading.Lock()

    def fetch_article(self, url):
        article_key(url)
        state = _Request(url, self.timeout)
        with self._lock:
            if self._active is not None:
                raise BrowserReadError("已有文章正在读取，请等待当前请求完成。")
            self._active = state
        server = None
        server_thread = None
        try:
            server = ThreadingHTTPServer(("127.0.0.1", 0), _BridgeHandler)
            server.daemon_threads = True
            server.request_state = state
            server_thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
            server_thread.start()
            connect_url = f"http://127.0.0.1:{server.server_port}/bbg/connect#{state.token}"
            if not webbrowser.open_new_tab(connect_url):
                raise BrowserReadError("无法打开默认浏览器。请检查 Windows 默认浏览器设置。")
            if not state.done.wait(max(0, state.deadline - time.monotonic())):
                if not state.connected.is_set():
                    raise BrowserReadError(
                        f"未连接到浏览器扩展。请在日常浏览器加载 {EXTENSION_DIRECTORY}，然后重新点击加载。")
                raise BrowserReadError("等待 __NEXT_DATA__ 超时。请检查文章是否仍在加载、需要人机验证或扩展已停用。")
            if state.error:
                raise BrowserReadError(state.error)
            try:
                article_dict = json.loads(state.raw_json)
            except (ValueError, TypeError) as exc:
                raise BrowserReadError("收到的 __NEXT_DATA__ 不是有效 JSON。") from exc
            return validate_article_dict(article_dict)
        finally:
            if server is not None:
                if server_thread is not None:
                    server.shutdown()
                    server_thread.join(timeout=2)
                server.server_close()
            with self._lock:
                self._active = None

    def close(self):
        # Compatibility with the unchanged error branch; never close personal tabs.
        with self._lock:
            if self._active is not None:
                with self._active.lock:
                    self._active.error = "文章读取已取消。"
                    self._active.done.set()

    def minimize_window(self):
        # The original parser calls this on success. Leave the personal browser alone.
        pass
