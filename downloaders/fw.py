"""CME FedWatch downloader implementation."""

from __future__ import annotations
import re
import shutil
import logging
import random
import os
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
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
)


class CMEfedWatchDownloader(DataDownloader):
    '''The probability of rate decision for future Fed meetings,
    use tables or integrate bar chart as means of visualizing data
    这个直接放表格，因为展示的是未来几次议息会议加息/降息的概率
    如果要是可以的话，可以做成那种纵向排列的多个柱状图，展示不同时期的概率分布
    只有最后cme fed watch 那个方法才是最终的引用的方法，其他的是为了方便后期维护而做的封装'''
    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int):
        self.url = r"https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict


        # 创建文件夹
        table_data_folder_path = os.path.join(os.fspath(CSV_DATA_FOLDER), "A_TABLE_DATA")
        if not os.path.exists(table_data_folder_path):
            os.makedirs(table_data_folder_path, exist_ok=True)  # exist_ok 创建文件夹的时候，如果文件夹已经存在，则不报错

        # cme_fedwatch 文件夹
        self.cme_folder_path = os.path.join(os.fspath(table_data_folder_path), "fed_watch")
        if not os.path.exists(self.cme_folder_path):
            os.makedirs(self.cme_folder_path, exist_ok=True)


        # create new webdriver
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")  # 无头浏览器
        options.add_argument("--start-maximized")   # 全屏浏览器
        self.driver = webdriver.Chrome(options=options)
        self.total_df = pd.DataFrame()  # ism df

    def get_start_num(self, rate_str):
        """用于处理利率排序"""
        start_num = int(rate_str.split("-")[0].replace(",", ""))
        return start_num

    def parse_single_file(self, file_path):
        """单独处理每个抓取数据的csv的内部数据排序然后储存到一个字典当中，方便后续整理"""
        df_raw = pd.read_csv(file_path, skiprows = 4, header = None)
        df_raw.columns = ["index", "data"]
        marker_row = df_raw[df_raw["data"].astype(str).str.contains('Data as of', na=False)].index[0]  # find marker row

        # create new df to store data
        df_output = pd.DataFrame()
        df_output["Rate"] = df_raw.iloc[:marker_row, 1].reset_index(drop=True)
        df_output["Probabilities"] = df_raw.iloc[marker_row + 1: marker_row * 2 + 1, 1].reset_index(drop=True)
        df_output.set_index("Rate")

        return df_output

    def cme_get_data(self, check_cancel = None):
        check_cancel()
        self.driver.get(self.url)
        time.sleep(random.uniform(0.2, 1))
        date_include = False  # 后面会涉及到提取仅一次日期，所以这里先定义一个变量

        # click cookies button
        try:
            cookies_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            cookies_button.click()
        except:
            logging.info("提示：未识别到CME fedwatch cookies按钮，程序继续 // Notify: Cookies button haven't been identified but continued...")
            pass

        # 有 iframe 的话，先切换
        check_cancel()
        try:
            iframe = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="cmeIframe-jtxelq2f"]'))
            )
            self.driver.switch_to.frame(iframe)
        except Exception:
            logging.info("提示：未识别到CME fedwatch iframe，程序继续 // Notify: Iframe haven't been identified but continued...")
            pass

        # 滚动页面以确保按钮加载
        for i in range(2):
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.2)

        # 定义按钮路径
        button_xpaths = [
            f'//*[@id="ctl00_MainContent_ucViewControl_IntegratedFedWatchTool_uccv_lvMeetings_ctrl{i}_lbMeeting"]'
            for i in range(16)
        ]

        # 循环点击
        for index, xpath in enumerate(button_xpaths):
            try:
                check_cancel()
                element = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                self.driver.execute_script("arguments[0].click();", element)

                time.sleep(0.65)

                # get data from html 获取html
                original_html = self.driver.page_source
                soup = BeautifulSoup(original_html, "lxml")

                check_cancel()
                # 提取按钮上的日期
                keyword = "do-mobile no-mobile"
                if date_include is False:
                    pattern = re.compile(keyword)
                    elements = soup.find_all("li", class_=pattern)
                    self.date_list = [date.get_text(strip=True).replace("月", "m") for date in elements]

                    # 由于抓取的数据出现日期错位，因此这里先添加一个无用内容标记，后续删除重复的数据
                    self.date_list.insert(0, "extra")
                    self.date_list.pop()
                    date_include = True

                check_cancel()
                # interest rate range 提取利率区间
                sheet_rate = soup.find_all("td", class_="center")
                rates = [rate.text.strip() for rate in sheet_rate]
                # probability 提取概率
                sheet_num = soup.find_all("td", class_ = "number highlight")
                nums = [num.text.strip() for num in sheet_num]

                check_cancel()
                self.total_df = pd.concat(
                    [pd.DataFrame(rates),
                     pd.DataFrame(nums)]
                )

                try:
                    os.makedirs(self.cme_folder_path, exist_ok = True)
                    csv_path = os.path.join(self.cme_folder_path, f"{self.date_list[index]}.csv")
                    self.total_df.to_csv(csv_path, index = True)
                except Exception as e:
                    logging.info(f"fw.py line 163, Data download successfully but failed to download csv, save_to_csv报错，原因是{e}")

            except Exception as e:
                logging.error(f"Failed to press button, reason is {e}")
                return

        self.driver.quit()
        return



    def cme_fed_watch(self, check_cancel = None)->pd.DataFrame:
        """final output function // 最后的引用方程"""
        check_cancel()
        self.cme_get_data(check_cancel = check_cancel) # get data
        df_storage_list = []
        num = 1
        for path in self.date_list:
            csv_path = os.path.join(self.cme_folder_path, path + ".csv")

            # 调用下载好的多个csv数据
            df_storage_list.append(self.parse_single_file(csv_path))
            num = num + 1
        del df_storage_list[0]           # 这里删除重复的数据

        # 下一步处理dataframe list里面，第一列分布不均匀的问题
        check_cancel()
        all_rates = sorted(
            set(rate for df in df_storage_list for rate in df['Rate']),
            key=self.get_start_num
        )  # set 保留唯一值，sort排序
        standard_index = pd.DataFrame({"Rate": all_rates})

        check_cancel()
        aligned_dfs = []
        for df in df_storage_list:
            df_merged = standard_index.merge(df, on='Rate', how='left')
            df_merged['Probabilities'] = df_merged['Probabilities'].fillna("0.0%")
            aligned_dfs.append(df_merged)

        prob_dfs = [df.set_index("Rate")["Probabilities"] for df in aligned_dfs]
        final_df = pd.concat(prob_dfs, axis=1).reset_index()
        final_df.columns = ["Rate"] + self.date_list[1:]

        check_cancel()
        prob_cols = [col for col in final_df.columns if col != "Rate"]
        for col in prob_cols:
            final_df[col] = final_df[col].str.rstrip('%').astype(float) / 100

        # 检查每行：是否至少有一个概率列 > 0  // check each line
        mask = (final_df[prob_cols] > 0).any(axis=1)
        final_df = final_df[mask]

        # 转回百分比字符串
        for col in prob_cols:
            final_df[col] = (final_df[col] * 100).astype(str) + '%'

        return final_df


    def to_db(
            self,
            return_csv = False,   # None time series data should directly download csv
            max_workers: Optional[int] = None,
            cancel_token: Optional[CancellationToken] = None,
    ) -> Optional[Dict[str, pd.DataFrame]]:

        return_csv = True
        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        try:
            _check_cancel()
            for table_name, table_config in self.json_dict.items():
                # !!! 调用ism类内的函数
                df = self.cme_fed_watch(check_cancel=_check_cancel)

                # 如果df是空的，传入log，然后直接开始下一轮循环，下载下一个数据
                if df is None:
                    logging.error(
                        "FAILED TO EXTRACT %s, check PREVIOUS loggings", table_name
                    )
                    return

                # 调用write_to_db，尽管不用写入数据库但是需要它的下载顺序和console信息
                converter = DatabaseConverter()
                _check_cancel()

                # useless params but must need, for console info
                converter.write_into_db(
                    df=df,
                    start_date = "2020-01-01",
                    data_name=table_config["name"],
                    is_time_series=False,
                    is_pct_data=False,
                )

                _check_cancel()
                df_dict : dict = {}
                df_dict[table_name] = df
                if df_dict is None:
                    logging.error("No data downloaded from ISM")
                    return None

                _check_cancel()
                for name, df in df_dict.items():
                    try:
                        for file in os.listdir(self.cme_folder_path):
                            # 先去除所有csv文件
                            if file.endswith('.csv'):
                                file_path = os.path.join(self.cme_folder_path, file)
                                os.remove(file_path)

                        # 再写入新的文件
                        csv_path = os.path.join(self.cme_folder_path, f"{name}.csv")
                        df.to_csv(csv_path, index=True)
                        logging.info("%s saved to %s Successfully!", name, csv_path)
                    except Exception as err:
                        logging.error(
                            "%s FAILED DOWNLOAD CSV in method 'to_db', since %s", name, err
                        )
                        continue

        except CancelledError:
            raise

        finally:
            # 去除没用的 data 文件夹，并quit driver
            try:
                current_file_path = os.path.abspath(os.path.dirname(__file__))
                useless_path = os.path.join(current_file_path, "..", "data")
                if os.path.exists(useless_path):
                    shutil.rmtree(useless_path)
                self.driver.quit()
            except Exception:
                pass

        return df_dict if return_csv else None


# testing
if __name__ == "__main__":
    json_dict = {
        "fed_watch": {
            "name": "FedWatch"
        }
    }
    ism = CMEfedWatchDownloader(json_dict = json_dict, api_key = "1", request_year = 2020)
    ism.to_db(return_csv=True)