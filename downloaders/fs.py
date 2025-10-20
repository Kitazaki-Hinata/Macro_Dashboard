'''Fx swap 外汇掉期数据'''

from __future__ import annotations
import time
import logging
import os
from typing import Any, Dict, Optional

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DataDownloader,
)



class FSDownloader(DataDownloader):
    """外汇掉期汇率数据，selenium实现"""
    def __init__(
            self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.json_dict = json_dict
        self.url = r"https://www.chinamoney.com.cn/chinese/bkcurvfsw/"
        options = Options()
        self.driver = webdriver.Chrome(options = options)
        self.driver.get(self.url)

        # initialize judgement
        repeat_time = 1
        judgement = False

        while repeat_time > 0:
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "fx-sw-data"))
                )   # wait till page load up  加载速度慢
                judgement = True
                break
            except:
                self.driver.refresh()
                logging.debug("尝试刷新... // Refreshing the page...")
                print("尝试刷新... // Refreshing the page...")
                repeat_time -= 1

        if judgement is False:
            print("网页加载失败，请检查网络 // Failed to load webpage")
            return

        time.sleep(2)  # 等待页面加载

    def _swap_forward_fx_curve(self):
        '''封装的提取数据函数 // swap forex curve and future forex '''
        try:
            html = self.driver.page_source
            soup = BeautifulSoup(html, "lxml")

            time_list = []
            pips_list = []
            future_forex_list = []

            # 获取数据
            tds_time = soup.find_all("td", class_ = "cell AC cell-first")
            for td in tds_time:  # 掉期日期
                time_list.append(td.get("data-value", "").strip())

            tds_pips = soup.find_all("td", class_ = "cell AC", attrs = {"data-name" : "points"})
            for td in tds_pips:  # 掉期点
                pips_list.append(td.get("data-value", "").strip())

            tds_forex = soup.find_all("td", class_ = "cell AC", attrs = {"data-name" : "swapAllPrc"})
            for td in tds_forex:   # 掉期远期汇率
                future_forex_list.append(td.get("data-value", "").strip())

            #整合data成df然后返回df
            df = pd.DataFrame({
                "time_period" : time_list,
                "pips" : pips_list,
                "swap_forex" : future_forex_list
            })
            df = df.drop(index = 0)  # 去除空行
            df["pips"] = pd.to_numeric(df["pips"])
            df["swap_forex"] = pd.to_numeric((df["swap_forex"]))
            df.insert(0, '', '') # 添加多余列，在table func中会统一删除
            return df

        except Exception as e:
            logging.error(e)
            return

    def _click_button(self, xpath):
        '''Xpath 是需要选择的货币对的xpath
        input demanded forex swap xpath'''
        try:
            select_dropdown = WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="fx-sw-curv-curr"]'))
            )
            select_dropdown.click()
            time.sleep(2)

            option = WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            option.click()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Failed to click btn in forex swap page, {e}")
            return

    def usdcny_swap(self, file_name : str, check_cancel):
        check_cancel()
        df = self._swap_forward_fx_curve()
        self._save_df_to_csv(df, file_name, check_cancel)

    def eurusd_swap(self, file_name : str, check_cancel):
        check_cancel()
        xpath = '//*[@id="fx-sw-curv-curr"]/option[6]'
        self._click_button(xpath)
        df = self._swap_forward_fx_curve()
        self._save_df_to_csv(df, file_name, check_cancel)

    def usdjpy_swap(self, file_name : str, check_cancel):
        check_cancel()
        xpath = '//*[@id="fx-sw-curv-curr"]/option[7]'
        self._click_button(xpath)
        df = self._swap_forward_fx_curve()
        self._save_df_to_csv(df, file_name, check_cancel)

    def gbpusd_swap(self, file_name : str, check_cancel):
        check_cancel()
        xpath = '//*[@id="fx-sw-curv-curr"]/option[9]'
        self._click_button(xpath)
        df = self._swap_forward_fx_curve()
        self._save_df_to_csv(df, file_name, check_cancel)

    def audusd_swap(self, file_name : str, check_cancel):
        check_cancel()
        xpath = '//*[@id="fx-sw-curv-curr"]/option[10]'
        self._click_button(xpath)
        df = self._swap_forward_fx_curve()
        self._save_df_to_csv(df, file_name, check_cancel)


    def _save_df_to_csv(self, df, file_name, check_cancel)->None:
        check_cancel()
        try:
            self.table_path = os.path.join(CSV_DATA_FOLDER, "A_TABLE_DATA")
            if not os.path.exists(self.table_path):
                os.makedirs(self.table_path)
            self.file_folder_path = os.path.join(self.table_path, file_name)
            if not os.path.exists(self.file_folder_path):
                os.makedirs(self.file_folder_path)
            self.file_path = os.path.join(self.file_folder_path, f"{file_name}.csv")
            df.to_csv(self.file_path, index = False)
        except Exception as e:
            logging.error(f"Failed to save file: {e}")
            return

    def to_db(
            self,
            return_csv = False,   # None time series data should directly download csv
            max_workers: Optional[int] = None,
            cancel_token: Optional[CancellationToken] = None,
    ) -> None:
        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        for table_name, table_config in self.json_dict.items():
            _check_cancel()
            data_name = table_config["name"]

            if data_name == "USD_CNY_Forex_Swap":
                self.usdcny_swap(data_name, _check_cancel)
            elif data_name == "EUR_USD_Forex_Swap":
                self.eurusd_swap(data_name, _check_cancel)
            elif data_name == "USD_JPY_Forex_Swap":
                self.usdjpy_swap(data_name, _check_cancel)
            elif data_name == "GBP_USD_Forex_Swap":
                self.gbpusd_swap(data_name, _check_cancel)
            elif data_name == "AUD_USD_Forex_Swap":
                self.audusd_swap(data_name, _check_cancel)

        self.driver.quit()





if __name__ == "__main__":
    json_dict = {
        "usdcny_swap": {
            "name": "USD_CNY_Forex_Swap"
        },
        "eurusd_swap": {
            "name": "EUR_USD_Forex_Swap"
        },
        "usdjpy_swap": {
            "name": "USD_JPY_Forex_Swap"
        },
        "gbpusd_swap": {
            "name": "GBP_USD_Forex_Swap"
        },
        "audusd_swap": {
            "name": "AUD_USD_Forex_Swap"
        },
        "foreign_ten_year_bonds_in_usd": {
            "name": "Foreign_10Y_Bonds_in_USD"
        }
    }
    ism = FSDownloader(json_dict = json_dict, api_key = "1", request_year = 2020)
    ism.to_db(return_csv=True)