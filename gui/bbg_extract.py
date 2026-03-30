# 提取 bloomberg 文章

import logging
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


logger = logging.getLogger(__name__)

class BloombergExtractor:
    def __init__(self, url : str):
        # 不在此处传入 URL，使实例可以复用
        self.bbg_article_url = url
        options = Options()
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options = options)

    def _fetch_bbg_article(self):
        """
        获取 Bloomberg 文章的完整 JSON 数据（__NEXT_DATA__）
        Args: bbg_url: Bloomberg 文章的 URL
        Returns:
            True, dict  成功时返回完整 JSON 数据
            False, dict("error": err_text)  失败时返回错误说明
        """
        try:
            logger.info(f"Fetching {self.bbg_article_url}")
            self.driver.maximize_window()
            self.driver.get(self.bbg_article_url)
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            article_dict : dict = self.driver.execute_script(
                "return window.__NEXT_DATA__"  # Bloomberg用Next.js
            )
            return True, article_dict

        except Exception as e:
            return False, {"error" : f'Failed to fetch, reason is {e}'}

    def edit_bbg_article(self) -> Tuple[bool, str]:
        '''gui调用的槽函数是这个，流程是，函数被调用后，先使用fetch_bbg_article内部方法
        获取json数据，然后再在这个函数中判断是否获取成功，并从json文件中提取文本'''

        # 调用fetch_bbg_article，先获取文章的完整 JSON 数据
        return_bool, article_dict = self._fetch_bbg_article()

        # 判断是否获取失败。如果失败，直接返回false和原因
        if return_bool is False and article_dict is not None:
            return (False, article_dict["error"])
        elif return_bool is False and article_dict is None:
            return (False, "Unknown error. There is neither json nor error message returned")
        elif article_dict is None:
            return(False, "Failed to extract. Check if it is identified as a robot. 检查是否是被识别为机器人 ")

        # 从json中提取全文
        body_content = article_dict['props']['pageProps']['story']['body']['content']
        paragraphs = []
        for block in body_content:
            if block.get('type') == 'paragraph':
                text = ''
                for item in block.get('content', []):
                    if item.get('type') == 'text':
                        text += item.get('value', '')
                    elif item.get('type') == 'entity':
                        # 链接文字也提取出来
                        for sub in item.get('content', []):
                            if sub.get('type') == 'text':
                                text += sub.get('value', '')
                    elif item.get('type') == 'link':
                        for sub in item.get('content', []):
                            if sub.get('type') == 'text':
                                text += sub.get('value', '')
                if text.strip():
                    paragraphs.append(text.strip())

        return (True, str('\n\n'.join(paragraphs)))

    def close_driver(self):
        # 延迟关闭浏览器
        self.driver.close()
