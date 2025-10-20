'''Emini 期货数据'''

import os
import logging
import time
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
    CancellationToken,
    DataDownloader,
)

class EMDownloader(DataDownloader):
    def __init__(
            self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.json_dict = json_dict
        self.url_half = "https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100"
        options = Options()
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options = options)

    def _emini_future_vol_open_interest(self, file_name: str, check_cancel):
        """Emini开仓量与持仓数据"""
        url = self.url_half + ".volume.html"
        try:
            check_cancel()
            self.driver.maximize_window()
            self.driver.get(url)

            # click cookie button
            try:
                cookies_button = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
                )
                cookies_button.click()
            except:
                pass

            check_cancel()
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1.5)  # 等待内容加载

            html = self.driver.page_source
            soup = BeautifulSoup(html, "lxml")
            error_text = "并没有找到td名称的tag // Failed to find td tag"
            index = 0

            # set lists for content store
            heights = []
            line_heights = []
            date_list = []
        except Exception as e:
            logging.error("Error in downloading CME-emini-future")
            return

        # get bar height data
        check_cancel()
        try:
            while True:
                boxes = soup.select(f'path.bb-shape-{index}.bb-bar-{index}')
                if not boxes:
                    break  # 没有更多的 bar，则退出

                for box in boxes:
                    d_attr = box.get("d")
                    parts = d_attr.split("V")

                    y_top = float(parts[1].split()[0][0:11])  # 顶部Y（第一个V之后）
                    y_bottom = float(parts[2][0:11])  # 底部Y（第二个V之后）
                    height = y_bottom - y_top
                    heights.append(height)
                index += 1
        except Exception as e:
            logging.error(error_text + "// BAR HEIGHT")
            print(error_text + "// BAR HEIGHT")
            return

        # get line (open interest data)
        check_cancel()
        try:
            line = soup.find("path", class_ = "bb-shape bb-shape bb-line bb-line-futureOi open-interest-line")
            d = line.get("d")
            parts = d.split(",")
            bottom = float(243.201)

            for i in parts[1:]:
                line_h = bottom - float(i.split(".")[0])
                line_heights.append(line_h)
        except Exception as e:
            logging.error(error_text + "// LINE NUMBER")
            print(error_text + "// LINE NUMBER")
            return

        # get date
        check_cancel()
        try:
            g = soup.find_all("g", class_ = "tick")
            if g:
                for tag in g:
                    date = tag.find("tspan")
                    if date:
                        dates = date.get_text()
                        date_list.append(dates)
        except Exception as e:
            logging.error(error_text + "// DATE")
            print(error_text + "// DATE")
            return

        # get reference data
        check_cancel()
        try:
            ref = soup.find("div", class_ = "main-table-wrapper")
            if ref:
                td_num = ref.find_all("td")
                vol = float(td_num[0].get_text().replace(",",""))
                open_interest = float(td_num[9].get_text().replace(",",""))
            else:
                raise Exception("REFERENCE DATA报错")
        except Exception as e:
            logging.error(error_text + "// REFERENCE DATA")
            print(error_text + "// REFERENCE DATA")
            return

        # calculate data and store in lists
        volume_data_list = []
        open_interest_data_list = []

        # calc index
        vol_index = vol / heights[-1] # data / height, for future * height
        open_index = open_interest / line_heights[-1]

        # calc volume, open
        check_cancel()
        for h in heights:
            volume_data_list.append(vol_index * h)
        for o in line_heights:
            open_interest_data_list.append(open_index * o)
        date_list = date_list[:30]
        duplicate_list = date_list[:30] #创建多余的一列，用于在table func中统一被删除

        # create df and save file
        check_cancel()
        df = pd.DataFrame({
            "empty" : duplicate_list,   # 这一列会在table里面统一删除
            "date" : date_list,
            "volume" : volume_data_list,
            "open_interest" : open_interest_data_list
        })
        self._save_file(df, file_name, check_cancel=check_cancel)
        self.driver.quit()

    def _save_file(self, df : pd.DataFrame, file_name : str, check_cancel):
        """Save data to csv"""
        check_cancel()
        try:
            table_path = os.path.join(CSV_DATA_FOLDER, "A_TABLE_DATA")
            if not os.path.exists(table_path):
                os.makedirs(table_path)
            file_folder_path = os.path.join(table_path, file_name)
            if not os.path.exists(file_folder_path):
                os.makedirs(file_folder_path)
            file_path = os.path.join(file_folder_path, f"{file_name}.csv")
            df.to_csv(file_path, index = False)
        except Exception as e:
            logging.error(f"Failed to save file: {e}")
            return

    def to_db(
            self,
            return_csv = False,   # None time series data should directly download csv
            max_workers: Optional[int] = None,
            cancel_token: Optional[CancellationToken] = None,
    ) -> None:

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        token = cancel_token
        for table_name, table_config in self.json_dict.items():
            _check_cancel()
            data_name = table_config["name"]
            self._emini_future_vol_open_interest(data_name, check_cancel=_check_cancel)


if __name__ == "__main__":
    json_dict = {
        "cme_emini_future_vol_open_interest": {
            "name": "CME_E_mini_Volume_and_Open_Interest"
        }
    }
    ism = EMDownloader(json_dict = json_dict, api_key = "1", request_year = 2020)
    ism.to_db(return_csv=True)