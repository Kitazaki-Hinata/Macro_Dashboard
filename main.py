'''main entrance of the software, connect gui'''

import json
import logging
from PySide6.QtWidgets import QApplication
from gui.ui_mainwindow import mainWindow


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

def read_json() ->  dict:
    '''read request_id.json file, return whole json context as a whole dictionary'''
    try:
        with open("request_id.json", "r", encoding="utf-8") as file:
            data_identity = json.load(file)
            logging.info( "read_json Successfully load json file")
        return data_identity
    except:
        logging.error("read_json, ERROR: FAILED to LOAD json file")


if __name__ == "__main__":
    setup_logging()  # 初始化日志系统
    json_data: dict = read_json()

    app = QApplication([])
    window = mainWindow()
    window.show()
    app.exec()









