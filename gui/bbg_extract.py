# 提取 bloomberg 文章

import logging
import requests
from typing import Optional, Tuple
from bs4 import BeautifulSoup


class BloombergExtractor:
    def __init__(self):
        # 不在此处传入 URL，使实例可以复用
        self.session = requests.Session()
        # 设置请求头，模拟浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def fetch_bbg_article(self, bbg_url: str) -> Tuple[bool, str]:
        """
        获取 Bloomberg 文章内容
        Args: bbg_url: Bloomberg 文章的 URL
        Returns: Tuple[bool, str]: (是否成功，文章内容或错误信息)
        """
        try:
            # 发送 HTTP GET 请求
            response = self.session.get(
                bbg_url,
                headers=self.headers,
                timeout=15  # 15 秒超时
            )

        except Exception as e:
            return False, f'Failed to fetch, reason is {e}'
