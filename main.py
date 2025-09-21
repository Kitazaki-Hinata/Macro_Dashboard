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
from typing import Any, Dict
from PySide6.QtWidgets import QApplication
from gui.ui_mainwindow import mainWindow
from download import DownloaderFactory  # type: ignore  # 示例引用，避免静态检查器误报未使用
from logging_config import start_logging, stop_logging

def read_json() -> Dict[str, Any]:
    """读取 `request_id.json` 并返回其内容。

    Returns:
        dict: JSON 的顶层字典；若读取失败返回空字典。
    """
    try:
        with open("request_id.json", "r", encoding="utf-8") as file:
            data_identity: Dict[str, Any] = json.load(file)
            logging.info( "read_json Successfully load json file")
        return data_identity
    except:
        logging.error("read_json, ERROR: FAILED to LOAD json file")
    return {}


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











