import json
import logging
from download import DownloaderFactory

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
    request_year : int = 2020  # 请求的开始年份

    bea_downloader = DownloaderFactory.create_downloader(
        source='bea',
        json_data = json_data,
        request_year = request_year
    )
    bea_downloader.to_db()

    # yf_downloader = DownloaderFactory.create_downloader(
    #     source = "yf",
    #     json_data = json_data,
    #     request_year = request_year
    # )
    # yf_downloader.to_db()
    #
    # # fred_downloader = DownloaderFactory.create_downloader(
    # #     source = "fred",
    # #     json_data = json_data,
    # #     request_year = request_year
    # # )
    # # fred_downloader.to_db()
    #
    # bls_downloader = DownloaderFactory.create_downloader(
    #     source = "bls",
    #     json_data = json_data,
    #     request_year = request_year
    # )
    # bls_downloader.to_db()

    # te_downloader = DownloaderFactory.create_downloader(
    #     source = "te",
    #     json_data = json_data,
    #     request_year = request_year
    # )
    # te_downloader.to_db()








