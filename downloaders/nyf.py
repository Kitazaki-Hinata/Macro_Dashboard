"""New York Fed Data downloader implementation."""

from __future__ import annotations
import logging
from pathlib import Path
import os
import time
import shutil
from typing import Any, Dict, Optional
from datetime import date
import pandas as pd
import urllib.request, urllib.parse
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
)

logger = logging.getLogger(__name__)
class NYFDownloader(DataDownloader):
    def __init__(
            self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.json_dict = json_dict

        # folder path
        self.download_path = Path.home() / "Downloads"
        self.csv_folder_path = CSV_DATA_FOLDER
        self.table_folder_path = os.path.join(self.csv_folder_path, "A_TABLE_DATA")

        # use selenium download xlsx file
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)

    def _change_original_file_path(self, check_cancel):
        """下载的原始文件修改路径，注意这里不是给细分文件的
        先做判断，对文件的日期进行判断，如果日期相同则直接跳过下载
        Judge whether download or not"""

        check_cancel()
        # path variables
        folder_path = os.path.join(os.path.join(self.csv_folder_path, "nyf_original_file"))  # 文件夹地址
        os.makedirs(folder_path, exist_ok=True)  # 创建文件夹

        # 更宽松的匹配模式
        pattern = r"HHD_C_Report*.xlsx"
        matching_files = list(self.download_path.glob(pattern))

        if not matching_files:
            # 增强错误提示，显示当前目录下的所有文件
            all_files = [f.name for f in self.download_path.iterdir() if f.is_file()]
            error_msg = (
                f"未找到匹配的HHD_C_Report文件，当前路径: {self.download_path}\n"
                f"当前目录下的文件列表: {all_files}"
            )
            logging.error(error_msg)
            print(error_msg)
            raise FileNotFoundError(error_msg)

        xlsx_file = matching_files[0]  # 取第一个匹配项
        target_location_path = os.path.join(folder_path, "nyf_original_file.xlsx")  # 转移后的文件路径与名称

        # 等待新文件下载完成
        check_cancel()
        for _ in range(30):
            if xlsx_file.exists():
                break
            else:
                time.sleep(1)

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # 删除整个目录及其内容
            os.makedirs(folder_path, exist_ok=True)

        check_cancel()
        if xlsx_file.exists():
            xlsx_file.rename(target_location_path)
            return
        else:
            error_msg = "Failed to download, because did not found target excel file"
            logging.error(error_msg)
            print(error_msg)
            return

    def _original_file_download(self, check_cancel):
        check_cancel()

        # 先删除任何下载文件夹中的之前的文件
        pattern = r"HHD_C_Report*.xlsx"
        matching_files = list(self.download_path.glob(pattern))
        for file in matching_files:
            try:
                file.unlink()
                logger.info(f"Deleted file: {file}")
            except Exception as e:
                logger.warning(f"Failed to delete file {file}: {e}")
                break

        # initialize info
        url = r"https://www.newyorkfed.org/microeconomics/hhdc.html"
        # file_name = f"nyf_original_file"

        try:
            html = urllib.request.urlopen(url).read()
        except Exception as e:
            error_msg = f"Failed to access URL {url}: {e}"
            logging.error(error_msg)
            print(error_msg)
            return

        soup = BeautifulSoup(html, "lxml")
        iframe = soup.find("iframe", id = "HHDCIframe")
        if iframe:
            iframe_src = iframe.get("src")

            # 访问 iframe 的 src 页面，因为iframe是单独的html所以需要重复访问一次
            full_iframe_url = urllib.parse.urljoin(url, iframe_src)
            try:
                iframe_html = urllib.request.urlopen(full_iframe_url).read()
            except Exception as e:
                error_msg = f"Failed to access iframe URL {full_iframe_url}: {e}"
                logging.error(error_msg)
                print(error_msg)
                return

            iframe_soup = BeautifulSoup(iframe_html, "lxml")

            # 找到下载链接
            link = iframe_soup.find_all("a", class_="glossary-download")
            if link:
                try:
                    href = link[1].get("href")
                except IndexError:
                    error_msg = f"Expected at least 2 download links, but found {len(link)}"
                    logging.error(error_msg)
                    print(error_msg)
                    return

                full_href = urllib.parse.urljoin(full_iframe_url, href)

                self.driver.get(full_href)
                time.sleep(1.5)

            else:
                error_msg = "Failed to find download button"
                logging.error(error_msg)
                print(error_msg)
                return

            # 转移文件 move the location of the file
            self._change_original_file_path(check_cancel = check_cancel)

        else:
            error_msg = "Failed to find iframe"
            logging.error(error_msg)
            print(error_msg)
            return

    def _read_excel_sheets(self, check_cancel):
        """下载完后，读取Excel文件中的所有sheet，并重新整理到新的文本当中"""
        file_name_path = os.path.join(self.csv_folder_path, "nyf_original_file", "nyf_original_file.xlsx")
        check_cancel()

        # 根据配置处理各个数据表
        for table_name, table_config in self.json_dict.items():
            check_cancel()
            data_name = table_config["name"]

            # 匹配sheet名称
            unit = None
            sheet_name = None
            if data_name == "Debt_balance":
                sheet_name = "Page 3 Data"
                unit = "Trillion USD"
            elif data_name == "Credit_quota":
                sheet_name = "Page 10 Data"
                unit = "Trillion USD"
            elif data_name == "30_Days_debt_default":
                sheet_name = "Page 13 Data"
                unit = "%/Pct"
            elif data_name == "90_Days_debt_default":
                sheet_name = "Page 14 Data"
                unit = "%/Pct"
            elif data_name == "Num_of_debts_bankruptcy_and_default":
                sheet_name = "Page 17 Data"
                unit = "Thousands"

            try:
                df_single_data = pd.read_excel(file_name_path, sheet_name=sheet_name)
            except:
                error_msg = f"Failed to read sheet {sheet_name} from file {file_name_path}"
                logging.error(error_msg)
                print(error_msg)
                continue

            if sheet_name == "Page 13 Data" or sheet_name == "Page 14 Data":
                df_single_data = df_single_data.drop(2)

            # 处理df
            df_single_data.columns = df_single_data.iloc[2]
            df_single_data = df_single_data.iloc[4:]
            df_single_data.columns.values[0] = f"Quarter, unit {unit}"
            df_single_data = df_single_data.iloc[-30:].reset_index(drop=True)

            # 对credit quota数据进行单独处理
            try:
                if data_name == "Credit_quota":
                    df_single_data = df_single_data.drop(columns=df_single_data.columns[-1])
                    df_right = df_single_data[["HE Revolving Balance", "HE Revolving Available Credit", "HE Revolving Limit"]]
                    df_left = df_single_data.iloc[:,0:4]

                    # 清除错行的空格
                    df_right = df_right.dropna().reset_index(drop=True)
                    df_left = df_left.dropna().reset_index(drop=True)
                    df_single_data = pd.concat([df_left, df_right], axis = 1)
            except Exception as e:
                print(f"error : {e}")
                logging.error(f"Failed to process credit quota data: {e}")
                continue

            # 清除表17的最后两列多余内容
            if data_name == "Num_of_debts_bankruptcy_and_default":
                df_single_data = df_single_data.iloc[:, :-2]

            try:
                single_file_folder_path = os.path.join(self.table_folder_path, data_name)
                csv_path = os.path.join(single_file_folder_path, f"{data_name}.csv")
                if not os.path.exists(single_file_folder_path):
                    os.makedirs(single_file_folder_path)
                df_single_data.to_csv(csv_path, index=True)
            except Exception as e:
                error_msg = f"Failed to save data to csv file {data_name}: {e}"
                logging.error(error_msg)
                print(error_msg)
                continue



    def to_db(
            self,
              return_csv = False,   # None time series data should directly download csv
              max_workers: Optional[int] = None,
              cancel_token: Optional[CancellationToken] = None,
              ):
        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        try:
            # 在循环外先下载文件，读取文件
            self._original_file_download(_check_cancel)
            self._read_excel_sheets(_check_cancel)

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
        "debt_balance": {
            "name": "Debt_balance"
        },
        "credit_quota" : {
            "name": "Credit_quota"
        },
        "30_days_debt_default" : {
            "name": "30_Days_debt_default"
        },
        "90_days_debt_default" : {
            "name": "90_Days_debt_default"
        },
        "Num_of_debts_bankruptcy_and_default" : {
            "name": "Num_of_debts_bankruptcy_and_default"
        }
    }
    nyf = NYFDownloader(json_dict = json_dict, api_key = "1", request_year = 2020)
    nyf.to_db(return_csv=True)
