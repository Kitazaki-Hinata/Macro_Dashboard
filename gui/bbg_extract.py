# 提取 bloomberg 文章

import logging
import requests
from typing import Optional, Tuple
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

class BloombergExtractor:
    def __init__(self):
        # 不在此处传入 URL，使实例可以复用
        self.session = requests.Session()
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.bloomberg.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
        })

    def _fetch_bbg_article(self, bbg_url: str):
        """
        获取 Bloomberg 文章的完整 JSON 数据（__NEXT_DATA__）
        Args: bbg_url: Bloomberg 文章的 URL
        Returns:
            True, dict  成功时返回完整 JSON 数据
            False, dict("error": err_text)  失败时返回错误说明
        """
        try:
            logger.info(f"Fetching {bbg_url}")



        except Exception as e:
            return False, {"error" : f'Failed to fetch, reason is {e}'}

    def edit_bbg_article(self, bbg_url: str) -> Tuple[bool, str]:
        '''gui调用的槽函数是这个，流程是，函数被调用后，先使用fetch_bbg_article内部方法
        获取json数据，然后再在这个函数中判断是否获取成功，并从json文件中提取文本'''

        # 调用fetch_bbg_article，先获取文章的完整 JSON 数据
        return_bool, dict_or_text = self._fetch_bbg_article(bbg_url)

        # 判断是否获取失败。如果失败，直接返回false和原因
        if return_bool is False and dict_or_text is not None:
            return (False, dict_or_text["error"])
        elif return_bool is False and dict_or_text is None:
            return (False, "Unknown error. There is neither json nor error message returned")

        # 根据json数据提取原文






