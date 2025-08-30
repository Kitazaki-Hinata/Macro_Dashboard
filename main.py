'''main entrance of the software, connect gui'''

import json
import logging
from PySide6.QtWidgets import QApplication
from gui.ui_mainwindow import mainWindow
from typing import Dict, Any


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s [line:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('doc/error.log'),
            logging.StreamHandler()
        ]
    )

def read_json() -> Dict[str, Any]:
    '''read request_id.json file, return whole json context as a whole dictionary'''
    try:
        with open("request_id.json", "r", encoding="utf-8") as file:
            data_identity = json.load(file)
            logging.info( "read_json Successfully load json file")
        return data_identity
    except Exception as e:
        logging.error(f"read_json, ERROR: FAILED to LOAD json file: {e}")
        return {}


if __name__ == "__main__":
    setup_logging()  # 初始化日志系统
    json_data: Dict[str, Any] = read_json()
    request_year : int = 2020  # 默认请求的开始年份

    app = QApplication([])
    window = mainWindow()
    window.show()
    app.exec()

    # te_downloader = DownloaderFactory.create_downloader(
    #     source = "te",
    #     json_data = json_data,
    #     request_year = request_year
    # )
    # te_downloader.to_db()








