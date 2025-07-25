from abc import ABC, abstractmethod
from typing import Dict
import requests
import os
from dotenv import load_dotenv

# ====================== 抽象基类 ======================
class DataDownloader(ABC):
    """数据下载器抽象基类"""

    @abstractmethod
    def to_db(self) -> None:
        pass

    def to_csv(self):
        pass

# ====================== 具体下载器类 ======================
class BEADownloader(DataDownloader):
    def __init__(self, json_dict: Dict, api_key: str):
        self.json_dict = json_dict
        self.api_key = api_key  # to_db函数里面，request API时需要api key

    def to_db(self, return_df = False) -> None:
        url = "https://xxx.xxx"
        for i in range(1, 10):
            response = requests.get(url, params={"api_key": self.api_key})
            pass
        if self.json_dict["needs_pct"] is True:
            # 如果需要百分比数据，处理df
            pass

    def to_csv(self):
        self.to_db(return_df = True)
        # 传出csv的代码
        pass


# ====================== 工厂类 ======================
class DownloaderFactory:
    # 数据源与API Key名称的映射(load from .env)
    _SOURCE_KEY_MAP = {
        'bea': 'BEA_API_KEY',
        'bls': 'BLS_API_KEY',
        'fred': 'FRED_API_KEY',
        'te': 'TE_API_KEY'
    }

    @classmethod
    def create_downloader(
            cls,
            source: str,
            json_dict: Dict,
            api_key: str = None
    ) -> 'DataDownloader':
        """
        创建下载器实例（自动获取API Key）

        :param source: 数据源类型（自动匹配.env中的KEY）
        :param json_dict: 配置字典
        :param api_key: 可选手动指定API Key
        """
        # 优先使用手动传入的api_key
        if api_key is None:
            api_key = cls._get_api_key(source)

        downloader_classes = {
            'bea': BEADownloader,
            # 其他数据源...
        }

        if source not in downloader_classes:
            raise ValueError(f"Unsupported data source: {source}")

        return downloader_classes[source](
            json_dict=json_dict,
            api_key=api_key
        )

    @classmethod
    def _get_api_key(cls, source: str) -> str:
        """根据数据源名称获取对应的API Key"""
        load_dotenv()  # 确保.env已加载

        key_name = cls._SOURCE_KEY_MAP.get(source)
        if not key_name:
            raise ValueError(f"No API key mapping for source: {source}")

        api_key = os.getenv(key_name)
        if not api_key:
            raise ValueError(f"API key not found in .env: {key_name}")

        return api_key