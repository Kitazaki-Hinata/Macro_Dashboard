"""应用入口（GUI）

职责：
- 初始化异步日志系统（见 `logging_config.start_logging`）
- 读取请求配置 `request_id.json`
- 启动 Qt 界面并进入事件循环

备注：
- 若需要在无界面模式测试下载逻辑，可参考底部注释的示例使用 `DownloaderFactory`。
"""

import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.ui_mainwindow import mainWindow
from download import DownloaderFactory  # type: ignore  # 示例引用，避免静态检查器误报未使用
from logging_config import start_logging, stop_logging

SMART_QUOTES_MAP = {
    '\u201c': '"', '\u201d': '"',  # 左/右双引号
    '\u2018': "'", '\u2019': "'",  # 左/右单引号
    '\u2013': '-',  '\u2014': '-',   # 短/长破折号
    '\u00a0': ' ',                    # 不换行空格
}

def _normalize_smart_chars(text: str) -> str:
    for k, v in SMART_QUOTES_MAP.items():
        if k in text:
            text = text.replace(k, v)
    return text

def _load_json_raw(path: Path) -> Optional[Dict[str, Any]]:
    """底层读取函数：多编码尝试 + 智能字符清洗。"""
    if not path.exists():
        logging.error("read_json ERROR: file not found: %s", path)
        return None
    raw = path.read_bytes()
    tried_encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'gbk']  # cp1252 兼容 0x93, 最后尝试 gbk 以便日志更友好
    last_err: Optional[Exception] = None
    for enc in tried_encodings:
        try:
            text = raw.decode(enc)
            if enc != 'utf-8':
                logging.warning("read_json: decoded with fallback encoding=%s", enc)
            text = _normalize_smart_chars(text)
            return json.loads(text)
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    logging.error("read_json FAILED: all encodings tried %s, last_err=%s", tried_encodings, last_err)
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
    logging.info("read_json loaded file=%s keys=%s", path, list(data.keys())[:6])
    return data


if __name__ == "__main__":
    start_logging(process_tag="gui")  # 初始化异步日志系统
    try:
        json_data: Dict[str, Any] = read_json()
        app = QApplication([])
        window = mainWindow()
        window.show()
        app.exec()
    finally:
        # 确保进程退出前停止日志监听，关闭文件句柄
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











