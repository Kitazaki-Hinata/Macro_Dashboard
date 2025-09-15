'''main entrance of the software, connect gui'''

import json
import logging
from PySide6.QtWidgets import QApplication
from gui.ui_mainwindow import mainWindow
from download import DownloaderFactory
from logging_config import start_logging, stop_logging

def read_json() -> dict:
    '''read request_id.json file, return whole json context as a whole dictionary'''
    try:
        with open("request_id.json", "r", encoding="utf-8") as file:
            data_identity : dict = json.load(file)
            logging.info( "read_json Successfully load json file")
        return data_identity
    except:
        logging.error("read_json, ERROR: FAILED to LOAD json file")
        return {}


if __name__ == "__main__":
    start_logging(process_tag="gui")  # 初始化异步日志系统
    try:
        json_data: dict = read_json()

        app = QApplication([])
        window = mainWindow()
        window.show()
        app.exec()
    finally:
        # 确保进程退出前停止日志监听，优雅关闭文件句柄
        stop_logging()

    '''Testing download file'''
    # request_year: int = 2020
    # fred_downloader = DownloaderFactory.create_downloader(
    #     source = "yf",
    #     json_data = json_data,
    #     request_year = request_year
    # )
    # fred_downloader.to_db(return_csv = False)











