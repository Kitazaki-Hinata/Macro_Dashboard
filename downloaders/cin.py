"""Cleveland Inflation Now_casting downloader implementation."""


from __future__ import annotations
from datetime import date
import os
import time
import pandas as pd
from typing import Any, Dict, Optional
from pathlib import Path
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
)

class CINDownloader(DataDownloader):
    def __init__(
            self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.url = "https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting"
        self.json_dict : dict = json_dict

        # path
        self.download_path = Path.home() / "Downloads"
        self.csv_folder_path = CSV_DATA_FOLDER
        self.table_folder_path = os.path.join(self.csv_folder_path, "A_TABLE_DATA")

        # dates
        self.end_year = date.today().year
        self.end_month = date.today().month

    def _quarter(self, end_month):
        '''Used in Cross_series, inflation_nowcasting, file_name matching
        用在cross_series 模块，用于匹配下载的文件'''
        match end_month:
            case 1 | 2 | 3:
                return 1
            case 4 | 5 | 6:
                return 2
            case 7 | 8 | 9:
                return 3
            case 10 | 11 | 12:
                return 4
            case _:
                return 0

    def _inflation_nowcasting(self, data_name, check_cancel):
        check_cancel()
        driver = webdriver.Chrome()

        # path variables
        folder_path = os.path.join(self.table_folder_path, data_name)  # 文件夹地址
        os.makedirs(folder_path, exist_ok=True)  # 确保创建文件夹

        filename = f"QuarterlyAnnualizedPercentChange-{self.end_year}-q{str(self._quarter(self.end_month))}.csv"  # 文件名
        xlsx_file = self.download_path / filename  # 下载的文件的自身地址
        target_location_path = os.path.join(folder_path, f"{data_name}.csv")  # 转移后xlsx文件

        # 删除重复文件名称的旧版excel file
        for f in [xlsx_file, target_location_path]:
            try:
                os.remove(f)
                time.sleep(0.3)
            except Exception as e:
                pass

        # download data
        driver.get(self.url)
        time.sleep(1)
        button = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-NowcastDownload-quarter"]'))
        )
        driver.execute_script("arguments[0].click();", button)

        for _ in range(30):  # maximum waiting for 30 seconds
            if xlsx_file.exists():
                break
            else:
                time.sleep(1)

        if xlsx_file.exists():
            # 确保目标目录存在
            xlsx_file.rename(target_location_path)
            driver.quit()

            # 修改csv，需要用pd转换成df，因为table模块会默认删除一列
            df = pd.read_csv(target_location_path)
            df.insert(0, '', '')
            df.to_csv(target_location_path, index=False)

        else:
            logging.error("Failed to download Cleveland inflation data")
            driver.quit()
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
            self._inflation_nowcasting(data_name = data_name, check_cancel = _check_cancel)





if __name__ == "__main__":
    json_dict = {
    "cleveland_inflation_nowcasting": {
        "name": "Cleveland_Inflation_Nowcasting"
        }
    }
    ism = CINDownloader(json_dict = json_dict, api_key = "1", request_year = 2020)
    ism.to_db(return_csv=True)