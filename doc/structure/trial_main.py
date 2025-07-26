import logging
import json
from dotenv import load_dotenv
from trial import DownloaderFactory


# ====================== 初始化配置 ======================
def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data_pipeline.log'),
            logging.StreamHandler()
        ]
    )

def read_json():
    # 读取json文件
    return {}


# ====================== 主程序 ======================
if __name__ == "__main__":
    setup_logging()  # 初始化日志系统
    json_dict = read_json()
    request_year = 2020  # 请求的开始年份

    bea_downloader = DownloaderFactory.create_downloader('bea', json_dict = json_dict, request_year = request_year)
    input()
