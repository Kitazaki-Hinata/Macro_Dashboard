"""应用入口（GUI）

职责：
- 初始化异步日志系统（见 `logging_config.start_logging`）
- 读取请求配置 `request_id.json`
- 启动 Qt 界面并进入事件循环

备注：
- 若需要在无界面模式测试下载逻辑，可参考底部注释的示例使用 `DownloaderFactory`。
"""

import json
import sys
import threading
import traceback
from types import TracebackType
from typing import Any, Dict, Optional, cast
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from gui.ui_mainwindow import mainWindow
from downloaders import DownloaderFactory  # type: ignore  # 示例引用，避免静态检查器误报未使用
from logging_config import start_logging, stop_logging
from gui.logging_i18n import log_critical, log_error, log_info, log_warning
from gui.ui_prestart_window import Prestart_ui
from gui.i18n_support import set_locale, translate

SMART_QUOTES_MAP = {
    "\u201c": '"',
    "\u201d": '"',  # 左/右双引号
    "\u2018": "'",
    "\u2019": "'",  # 左/右单引号
    "\u2013": "-",
    "\u2014": "-",  # 短/长破折号
    "\u00a0": " ",  # 不换行空格
}


def _format_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType],
) -> str:
    return "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))


def _show_exception_dialog(summary: str, detail: str) -> None:
    app = QApplication.instance()
    if app is None:
        sys.stderr.write(detail)
        sys.stderr.flush()
        return

    def _present() -> None:
        box = QMessageBox()
        box.setWindowTitle(translate("errors.unhandled.title"))
        box.setIcon(QMessageBox.Icon.Critical)
        box.setText(translate("errors.unhandled.message"))
        box.setInformativeText(summary)
        box.setDetailedText(detail)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()

    QTimer.singleShot(0, _present)


def _handle_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType],
) -> None:
    if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    detail = _format_exception(exc_type, exc_value, exc_traceback)
    summary = str(exc_value).strip() or exc_type.__name__

    log_critical(
        "system.uncaught_exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    _show_exception_dialog(summary, detail)


def _install_global_exception_handlers() -> None:
    sys.excepthook = _handle_uncaught_exception

    if hasattr(threading, "excepthook"):

        def _thread_hook(args: threading.ExceptHookArgs) -> None:  # type: ignore[attr-defined]
            exc_type = args.exc_type or Exception
            exc_value = args.exc_value or exc_type()
            _handle_uncaught_exception(exc_type, exc_value, args.exc_traceback)

        threading.excepthook = _thread_hook  # type: ignore[attr-defined]


class SafeApplication(QApplication):
    """安全包装 QApplication，捕获事件循环中的未处理异常。"""

    def notify(self, receiver: QObject, event: QEvent) -> bool:  # type: ignore[override]
        try:
            return super().notify(receiver, event)
        except Exception:  # noqa: BLE001
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_type is None or exc_value is None:
                raise
            _handle_uncaught_exception(exc_type, exc_value, exc_traceback)
            return False


def _normalize_smart_chars(text: str) -> str:
    for k, v in SMART_QUOTES_MAP.items():
        if k in text:
            text = text.replace(k, v)
    return text


def _load_json_raw(path: Path) -> Optional[Dict[str, Any]]:
    """底层读取函数：多编码尝试 + 智能字符清洗。"""
    if not path.exists():
        log_error("read_json.file_not_found", {"path": str(path)})
        return None
    raw = path.read_bytes()
    tried_encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "gbk",
    ]  # cp1252 兼容 0x93, 最后尝试 gbk 以便日志更友好
    last_err: Optional[Exception] = None
    for enc in tried_encodings:
        try:
            text = raw.decode(enc)
            if enc != "utf-8":
                log_warning("read_json.fallback_encoding", {"encoding": enc})
            text = _normalize_smart_chars(text)
            return json.loads(text)
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    log_error(
        "read_json.failed_all",
        {
            "encodings": ", ".join(tried_encodings),
            "error": str(last_err) if last_err else "",
        },
    )
    return None


def read_json() -> Dict[str, Any]:
    """读取 `request_id.json`，带编码回退与智能字符清洗。

    读取顺序：utf-8 -> utf-8-sig -> cp1252 -> gbk；并替换 Word/网页复制的智能引号。
    失败时返回空字典，并记录日志。
    """
    path = Path("request_id.json")
    data = _load_json_raw(path)
    if data is None:
        return {}
    preview_keys = list(data.keys())[:6]
    log_info(
        "read_json.loaded",
        {"path": str(path), "keys": ", ".join(map(str, preview_keys))},
    )
    return data


def _load_language_from_settings() -> str:
    settings_path = Path(__file__).resolve().parent / "gui" / "settings.json"
    try:
        with settings_path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except Exception:
        return set_locale("zh")

    if not isinstance(raw, dict):
        return set_locale("zh")

    raw_dict = cast(Dict[str, Any], raw)
    preferred = raw_dict.get("language")
    if not isinstance(preferred, str):
        preferred = "zh"
    return set_locale(preferred)


if __name__ == "__main__":
    try:
        _install_global_exception_handlers()
        app = SafeApplication([])

        # 先显示预启动窗口
        prestart_window = Prestart_ui()
        prestart_window.setWindowFlags(
            prestart_window.windowFlags()
            | Qt.WindowType.WindowStaysOnTopHint  # 始终置顶 prestart window
        )
        prestart_window.show()
        app.processEvents()  # 立刻渲染prestart window

        # 初始化日志和配置
        start_logging(process_tag="gui")
        json_data: Dict[str, Any] = read_json()
        preferred_locale = _load_language_from_settings()

        # 使用定时器延迟创建主窗口
        def load_main_window():
            global window
            window = mainWindow(language=preferred_locale)
            window.show()
            prestart_window.close()  # 关闭预启动窗口

        # 预启动窗口先显示
        QTimer.singleShot(0, load_main_window)

        app.exec()
    finally:
        # 进程退出前停止日志监听，关闭文件句柄
        stop_logging()

    # --- 以下为测试下载的参考示例（保留注释即可） ---
    # 使用方式：取消注释并按需修改源与年份；在非 GUI 场景下验证下载逻辑。
    #
    # request_year: int = 2020
    # fred_downloader = DownloaderFactory.create_downloader(
    #     source = "fred",
    #     json_data = json_data,
    #     request_year = request_year
    # )
    # fred_downloader.to_db(return_csv = False)
