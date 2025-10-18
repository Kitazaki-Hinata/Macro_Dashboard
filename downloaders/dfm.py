'''Dallas Fed 达拉斯联储制造业数据'''

from __future__ import annotations
import logging
import os
import time
from typing import Any, Dict, Optional
import pandas as pd
from datetime import date
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from downloaders.common import (
    CancelledError,
    CancellationToken,
    DataDownloader,
)

logger = logging.getLogger(__name__)
class DFMDownloader(DataDownloader):
    '''show table data and first line data
    由于细分数据太多，因此ts当中只展示第一列的数据
    其他细分数据在cs当中只使用table表格的形式展示'''
    def __init__(
            self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict

        # download info
        self.year = date.today().year
        self.year_last_two_digit = str(self.year)[2:4]
        self.month = f"{date.today().month:02d}"
        self.url_1 :  str = f"https://www.dallasfed.org/research/surveys/tmos/{self.year}/{self.year_last_two_digit}{self.month}#tab-data"
        self.url_2 : str = f"https://www.dallasfed.org/research/surveys/tmos/{self.year}/{self.year_last_two_digit}{int(self.month)-1:02d}#tab-data"

        # file path info
        self.download_path = Path.home() / "Downloads"  # 下载文件夹的文件夹地址
        self.current_file_path = os.path.dirname(os.path.abspath(__file__))
        self.csv_folder = os.path.join(self.current_file_path, "..", "csv", "A_TABLE_DATA")

        # check folder exists
        if not os.path.exists(self.csv_folder):
            os.makedirs(self.csv_folder)

        # driver
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options = options)

    def _remove_last_space(self, df : pd.DataFrame)-> pd.DataFrame:
        """Remove last space in dataframe, 下载的数据最后可能有空值，所以要去除"""
        if len(df) > 1144:  # 确保数据足够长，避免切片越界
            df = df.iloc[150:-1044]
        else:
            df = df.iloc[150:]  # 如果行数太少，只去掉前100行
        return df

    def _dallas_manufacture_index_unadj_get_data(self, file_name : str, check_cancel = None):
        """No seasonal adjustments data"""
        check_cancel()

        # local data folder path
        downloaded_file = None
        dallas_data_folder_path = os.path.join(os.path.join(self.csv_folder, file_name))
        os.makedirs(dallas_data_folder_path, exist_ok=True)  # 创建本数据文件夹
        raw_data_name = "index.xlsx"  # 原始文件的文件名
        xlsx_file = self.download_path / raw_data_name  # 下载的文件的自身地址
        target_location_path = os.path.join(dallas_data_folder_path, raw_data_name)  # 转移后xlsx文件
        final_csv_location_path = os.path.join(dallas_data_folder_path, f"{file_name}.csv")  # 转移后修改表头的最终csv

        # 删除重复文件名称的旧版excel file
        for file in [xlsx_file, target_location_path, final_csv_location_path]:
            check_cancel()
            if os.path.exists(file):
                try:
                    os.remove(file)
                    time.sleep(0.3)
                except Exception as e:
                    pass

        # download data
        try:
            for url in [self.url_1, self.url_2]:
                check_cancel()
                self.driver.get(url)
                time.sleep(1)
                if self.driver.find_elements(By.XPATH, '//h1[@class="dal-headline" and contains(text(), "HTTP Error 404")]'):
                    continue

                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="tmos-historicaldata"]/table[1]/tbody/tr[1]/td/a/strong'))
                )
                button.click()  # press the download button

                for _ in range(30):  # maximum waiting for 30 seconds
                    if xlsx_file.exists():
                        break
                    else:
                        time.sleep(1)
                        check_cancel()

                if xlsx_file.exists():
                    # 确保目标目录存在
                    downloaded_file = xlsx_file.rename(target_location_path)
                    break
                else:
                    logging.error("Failed to download data of Dallas manufacture index")
                    return

        except Exception as e:
            logging.error(f"Failed to download data of Dallas manufacture index, error is {e}")
            return

        # change column name
        time.sleep(0.3)
        try:
            df = pd.read_excel(downloaded_file, sheet_name="Index")
        except:
            logging.error("Failed to read downloaded file, probably error 404 from web")
            return

        # remove useless columns and rename columns
        check_cancel()
        columns_to_drop= [
            "Fcapu",
            "Fgro",
            "Fvshp",
            "Dtm",
            "Fdtm",
            "Ffgi",
            "Fwgs",
            "Fnemp",
            "Avgwk",
            "Favgwk",
            "Fcexp",
            "Fcolk",
            "Fbact",
            "Uncr"
        ]
        df.drop(columns=columns_to_drop, axis=1, inplace=True)
        df.columns = [
            "Date",
            "Production",
            "Future production",
            "Capacity utilization",
            "New orders",
            "Future new orders",
            "Growth rate of orders",
            "Unfilled orders",
            "Future unfilled orders",
            "Shipments",
            "Finished goods inventories",
            "Prices paid for raw material",
            "Future prices paid for raw material",
            "Prices received for finished goods",
            "Future prices received for finished goods",
            "Wage and benefits",
            "Employment",
            "Capex",
            "Company outlook",
            "General business activity"
        ]   # rename columns
        df = self._remove_last_space(df)
        df.to_csv(final_csv_location_path)

        # 去除raw data文件
        if os.path.exists(os.path.join(dallas_data_folder_path, raw_data_name)):
            os.remove(os.path.join(dallas_data_folder_path, raw_data_name))
        return

    def _dallas_manufacture_index_adj_get_data(self, file_name : str, check_cancel = None):
        """有季调的制造业指数，通常是数据网站给的数据
        include seasonal adjustments"""
        downloaded_file = None

        # path variables
        check_cancel()
        dallas_data_folder_path = os.path.join(os.path.join(self.csv_folder, file_name))
        os.makedirs(dallas_data_folder_path, exist_ok=True)  # 创建本数据文件夹
        raw_data_name = "index_sa.xlsx"
        xlsx_file = self.download_path / raw_data_name
        target_location_path = os.path.join(dallas_data_folder_path, raw_data_name)
        final_csv_location_path = os.path.join(dallas_data_folder_path, f"{file_name}.csv")

        # 删除重复文件名称的旧版excel file
        for file in [xlsx_file, target_location_path, final_csv_location_path]:
            check_cancel()
            if os.path.exists(file):
                try:
                    os.remove(file)
                    time.sleep(0.3)
                except Exception as e:
                    pass

        # download data
        try:
            for url in [self.url_1, self.url_2]:
                check_cancel()
                self.driver.get(url)
                time.sleep(1)
                if self.driver.find_elements(By.XPATH, '//h1[@class="dal-headline" and contains(text(), "HTTP Error 404")]'):
                    continue
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="tmos-historicaldata"]/table[1]/tbody/tr[2]/td/a/strong'))
                )
                button.click()  # press the download button

                # maximum waiting for 30 seconds
                for _ in range(30):
                    if xlsx_file.exists():
                        break
                    else:
                        time.sleep(1)
                        check_cancel()

                # 将下载的xlsx移动位置并重命名
                if xlsx_file.exists():
                    downloaded_file = xlsx_file.rename(target_location_path)
                    break
                else:
                    logging.error("Failed to download data of Dallas manufacture index")
                    return

        except Exception as e:
            logging.error(f"Failed to download data of Dallas manufacture index, error is {e}")
            return

        # change column name
        check_cancel()
        time.sleep(0.3)
        try:
            df = pd.read_excel(downloaded_file, sheet_name="Indexes Seasonally Adjusted")
        except:
            logging.error("Failed to read downloaded file, probably error 404 from web")
            return

        # remove useless columns and rename columns
        check_cancel()
        columns_to_drop= [
            "Fcapu",
            "Fgro",
            "Fvshp",
            "Dtm",
            "Fdtm",
            "Ffgi",
            "Fwgs",
            "Fnemp",
            "Avgwk",
            "Favgwk",
            "Fcexp",
            "Fcolk",
            "Fbact",
            "Uncr"
        ]
        df.drop(columns=columns_to_drop, axis=1, inplace=True)
        df.columns = [
            "Date",
            "Production",
            "Future production",
            "Capacity utilization",
            "New orders",
            "Future new orders",
            "Growth rate of orders",
            "Unfilled orders",
            "Future unfilled orders",
            "Shipments",
            "Finished goods inventories",
            "Prices paid for raw material",
            "Future prices paid for raw material",
            "Prices received for finished goods",
            "Future prices received for finished goods",
            "Wage and benefits",
            "Employment",
            "Capex",
            "Company outlook",
            "General business activity"
        ]   # rename columns
        df = self._remove_last_space(df)
        df.to_csv(final_csv_location_path)

        # 去除raw data文件
        if os.path.exists(os.path.join(dallas_data_folder_path, raw_data_name)):
            os.remove(os.path.join(dallas_data_folder_path, raw_data_name))
        return

    def to_db(
            self,
            return_csv = False,   # None time series data should directly download csv
            max_workers: Optional[int] = None,
            cancel_token: Optional[CancellationToken] = None,
    ) -> Optional[Dict[str, pd.DataFrame]]:

        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        try:
            # 构造循环，遍历传入的json并依次处理
            for table_name, table_config in self.json_dict.items():
                _check_cancel()
                data_name = table_config["name"]
                if data_name == "Unadj_Dallas_Federal_Manu_Index":
                    self._dallas_manufacture_index_unadj_get_data(
                        file_name = data_name,
                        check_cancel = _check_cancel
                    )
                elif data_name == "Adj_Dallas_Federal_Manu_Index":
                    self._dallas_manufacture_index_adj_get_data(
                        file_name = data_name,
                        check_cancel = _check_cancel
                    )
                else:
                    logging.error(f"dfm data failed to identified, line 308, {data_name} is not supported")

        except CancelledError:
            raise
        finally:
            try:
                self.driver.quit()
            except:
                pass

        return None


if __name__ == "__main__":
    json_dict = {
        "dallas_fed_manufacture_unadj": {
            "name": "Unadj_Dallas_Federal_Manu_Index"
        },
        "dallas_fed_manufacture_adj": {
            "name": "Adj_Dallas_Federal_Manu_Index"
        }
    }
    dfm = DFMDownloader(json_dict = json_dict, api_key = "1", request_year = 2020)
    dfm.to_db(return_csv=True)
