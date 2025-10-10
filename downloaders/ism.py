"""ISM downloader implementation."""

from __future__ import annotations
import random
import logging
import os
import time
from typing import Any, Dict, Optional, Callable
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException
)
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

logger = logging.getLogger(__name__)
month_dict = {
    "1" : "january",
    "2" : "february",
    "3" : "march",
    "4" : "april",
    "5" : "may",
    "6" : "june",
    "7" : "july",
    "8" : "august",
    "9" : "september",
    "10" : "october",
    "11" : "november",
    "12" : "december"
}



class ISMDownloader(DataDownloader):
    '''ISM制造业与服务业指数，以table方式展示
    只需要用到json_dict参数，但是因为是downloader所以统一api_key和request_year

    ### self.total_df 作为一个不会被垃圾回收的df
    self.total_df : 一个dataframe，会储存之前所有下载好的df，然后添加新的df到里面
    '''
    def __init__(
            self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.url = r"https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/"
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.total_df = pd.DataFrame()

        # initialize driver 初始化driver
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)

    def ism_manu_html_extractor(self, check_cancel: Optional[Callable[[], None]] = None):
        """global method, extract html"""
        try:
            html = self.driver.page_source  # crawl whole html
        except Exception as e:
            logging.error(f"Failed to crawl html, haven't identify url, error:{e}")
            print("Failed to crawl html, haven't identify url")
            self.driver.quit()
            return

        self.success_extract_or_not = True  # 要是没有成功抓取那么就不执行删除最后的语句 drop[-2]
        check_cancel()

        try:   # 有的时候，或者之后永远，都没法获得过去5个月的ism报告，所以要有跳过部分
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find('table', class_='table table-bordered table-hover table-responsive mb-4')
            rows = table.find('tbody').find_all('tr')

            col_values = []  # store values for future dataframe management
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    first_col_text = cells[0].get_text(strip=True)
                    col_values.append(first_col_text)  # append data into list
            df = pd.DataFrame([col_values])
            self.total_df = pd.concat([self.total_df, df], ignore_index=True)
            print(f"成功抓取一份ISM报告数据 // successfully get 1 ISM report data")
            check_cancel()

            del html  # delete variables
            del col_values
        except Exception as e:
            logger.warning(f"Failed to extract one specific ISM report, error: {e}, continue...")
            print(f"Failed to extract one specific ISM report, error: {e}")
            self.success_extract_or_not = False
            pass

    def ism_manufacture(self, check_cancel)->pd.DataFrame:
        """运行方法，首先打开report界面，点击报告抓取当前报告
        然后通过修改report url的月份抓取过去5个月的报告，储存数据
        间隔时间随机，防止被封ip
        Open main url, crawl data, then change url, crawl past data"""

        # initialize : clear total_df and load html
        self.total_df = pd.DataFrame()
        self.driver.get(self.url)
        time.sleep(2)  # wait loading

        # click cookies button
        check_cancel()
        try:
            accept_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            accept_button.click()
            print("Accepted all cookies of ISM website // 已识别cookies按钮并继续")
            time.sleep(random.uniform(0.3, 1))
        except NoSuchElementException:
            logging.warning(f"Haven't detected cookies button in ISM manu, continue")
            print("Haven't detected cookies button in ISM manu, continue")
            pass

        # main to report
        check_cancel()
        try:
            view_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="main"]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[2]/center/p[1]/a[1]'))
            )
            view_button.click()
            time.sleep(random.uniform(0.3, 1)) # load data, random num to prevent IP ban
        except NoSuchElementException:
            logging.error(f"Failed to navigate to report url, no button element, stop crawling")
            print("Failed to navigate to report url, stop crawling ...// 并没有找到元素，停止爬取此数据")
            self.driver.quit()
            return pd.DataFrame()

        # click disclaimer button if exists
        check_cancel()
        try:
            disclaimer_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="alert-modal-disclaimer___BV_modal_body_"]/center/input'))
            )
            disclaimer_button.click()
            print("Accepted disclaimer of ISM website // 已识别disclaimer按钮并继续")
            time.sleep(random.uniform(0.6,1.3))
        except NoSuchElementException:
            logging.warning(f"Haven't detected disclaimer button in ISM manu, continue")
            print("提示：没有识别到ISM manu cookies按钮，程序继续进行 // Notify: Haven't detected cookies button, but continue...")
            pass

        # crawl current data
        check_cancel()
        self.ism_manu_html_extractor(check_cancel = check_cancel)  # Note: data are saved in self.total_df

        # get month list for other data crawling
        url = str(self.driver.current_url)
        extract_month = url.rstrip('/').split("/")[-1].lower()
        reversed_dict = {v: int(k) for k, v in month_dict.items()}  # reverse value and key 双向映射

        month_num = reversed_dict.get(extract_month)
        if not month_num:
            logger.error(f"Cannot find month in URL：{extract_month}")
            print(f"URL中无法识别月份：{extract_month}")
            return pd.DataFrame()

        prev_months = []  # store str "month" name  正常提取5个月报告
        for i in range(1, 5):
            prev_num = (month_num - i - 1) % 12 + 1
            month_name = month_dict[str(prev_num)]
            prev_months.append(month_name)

        for month in prev_months:
            new_url = f"https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/pmi/{month}/"
            check_cancel()
            self.driver.get(new_url)
            time.sleep(random.uniform(0.2,0.9))  # wait loading
            self.ism_manu_html_extractor(check_cancel = check_cancel)
            if self.success_extract_or_not is True:
                self.total_df.drop(columns=self.total_df.columns[-2:], axis=1, inplace=True)

        # convert into csv
        check_cancel()
        print("已经提取所有数据，正在转换成csv文件... // converting to csv...")
        self.total_df.columns = [
            "Manufacture PMI",
            "New Orders",
            "Production",
            "Employment",
            "Supplier Deliveries",
            "Inventories",
            "Customers' Inventories",
            "Prices",
            "Backlog of Orders",  # 积压的
            "New Export Orders",
            "Imports"
        ]
        prev_months.insert(0, extract_month)
        series_month = pd.Series(prev_months)
        self.total_df.insert(0, "Month", series_month)
        print("成功下载ISM manufacture细分数据！// Successfully download ISM manufacture data!")
        return self.total_df

    def ism_service(self, check_cancel)->pd.DataFrame:
        """运行方法，首先打开report界面，点击报告抓取当前报告
        然后通过修改report url的月份抓取过去5个月的报告，储存数据
        间隔时间随机，防止被封ip
        Open main url, crawl data, then change url, crawl past data"""

        # initialize : clear total_df and load html
        self.total_df = pd.DataFrame()
        self.driver.get(self.url)
        time.sleep(2)  # wait loading

        # click cookies button
        check_cancel()
        try:
            accept_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            accept_button.click()
            print("Accepted all cookies of ISM website // 已识别cookies按钮并继续")
            time.sleep(random.uniform(0.3, 1))
        except NoSuchElementException:
            print("提示：没有识别到ISM service cookies按钮，程序继续进行 // Notify: Haven't detected cookies button, but continue...")
            pass

        # main to report
        check_cancel()
        try:
            view_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="main"]/div[2]/div[2]/div/div/div[2]/div/div[2]/div[2]/center/p[1]/a[1]'))
            )
            view_button.click()
        except NoSuchElementException:
            logging.error("Failed to navigate to report url, stop crawling ...// 并没有找到元素，停止爬取此数据")
            print("Failed to navigate to report url, stop crawling ...// 沒有找到元素，停止爬取此數據")
            self.driver.quit()
            return pd.DataFrame()  # return empty df

        # click disclaimer button if exists
        check_cancel()
        try:
            disclaimer_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="alert-modal-disclaimer___BV_modal_body_"]/center/input'))
            )
            disclaimer_button.click()
        except NoSuchElementException:
            logging.warning("Notify: Haven't detected cookies button, but continue...")
            print("提示：没有识别到ISM service cookies按钮，程序继续进行 // Notify: Haven't detected cookies button, but continue...")
            pass

        # crawl current data
        self.ism_manu_html_extractor(check_cancel = check_cancel)  # Note: data are saved in self.total_df

        # get month list for other data crawling
        check_cancel()
        url = str(self.driver.current_url)
        extract_month = url.rstrip('/').split("/")[-1].lower()
        reversed_dict = {v: int(k) for k, v in month_dict.items()}  # reverse value and key 双向映射

        month_num = reversed_dict.get(extract_month)
        if not month_num:
            logging.error(f"Cannot identify month: {extract_month}")
            print(f"URL中无法识别月份：{extract_month}")
            return pd.DataFrame()

        prev_months = []  # store str "month" name
        for i in range(1, 5):
            prev_num = (month_num - i - 1) % 12 + 1
            month_name = month_dict[str(prev_num)]
            prev_months.append(month_name)

        for month in prev_months:
            new_url = f"https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/services/{month}/"
            check_cancel()
            self.driver.get(new_url)
            time.sleep(random.uniform(0.2,0.9))  # wait loading
            self.ism_manu_html_extractor(check_cancel = check_cancel)
            if self.success_extract_or_not is True:
                self.total_df.drop(columns=self.total_df.columns[-3:], axis=1, inplace=True)

        # convert into csv
        check_cancel()
        print("已经提取所有数据，正在转换成csv文件... // converting to csv...")
        self.total_df.columns = [
            "Service PMI",
            "Business Activity",
            "New Orders",
            "Employment",
            "Supplier Deliveries",
            "Inventories",
            "Prices",
            "Backlog of Orders", # 积压的
            "New Export Orders",
            "Imports",
            "Inventory Sentiment" # 库存情绪，表明认为当前库存数量过高还是过低
            # "Customers' Inventories"  # 报告中没有数值，说的是客户的库存数量预期
        ]
        prev_months.insert(0, extract_month)
        series_month = pd.Series(prev_months)
        self.total_df.insert(0, "Month", series_month)
        print("成功下载ISM service细分数据！// Successfully download ISM service data!")
        return self.total_df


    def _main_downloader(
            self,
            data_name: str,
            check_cancel: Optional[Callable[[], None]] = None,
    ) -> pd.DataFrame:
        # 主下载方法，to_db调用, 返回下载的df
        # check_cancel导入的是check cancel方法，用于调用 方法中的方法，从而取消下载

        if data_name == "ISM_service":
            if check_cancel is not None:
                check_cancel()
            df = self.ism_service(check_cancel = check_cancel)
        elif data_name == "ISM_manufacturing":
            if check_cancel is not None:
                check_cancel()
            df = self.ism_manufacture(check_cancel = check_cancel)
        else:
            df = pd.DataFrame()  # return empty df
        return df

    def to_db(
            self,
            return_csv = False,   # None time series data should directly download csv
            max_workers: Optional[int] = None,
            cancel_token: Optional[CancellationToken] = None,
    ) -> Optional[Dict[str, pd.DataFrame]]:
        # 输出格式dict[str, pd.Dataframe] 是数据名称与数据的df对应

        # FORCE : None time series data should directly download csv
        return_csv = True,
        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        try:
            # 构造ism类内循环，这里会通过循环
            # 传入ism manufacture和ism service的参数
            for table_name, table_config in self.json_dict.items():
                _check_cancel()
                data_name = table_config["name"]

                # 调用ism类内的函数
                df = self._main_downloader(
                    data_name=data_name,
                    check_cancel=_check_cancel
                )

                # 如果df是空的，传入log，然后直接开始下一轮循环，下载下一个数据
                if df is None:
                    logger.error(
                        "FAILED TO EXTRACT %s, check PREVIOUS loggings", table_name
                    )
                    continue

                # 调用write_to_db，尽管不用写入数据库但是需要它的下载顺序和console信息
                converter = DatabaseConverter()
                _check_cancel()
                converter.write_into_db(
                    df=df,
                    start_date = "2020-01-01",   # useless params but must need
                    data_name=table_config["name"],
                    is_time_series=False,
                    is_pct_data=False,
                )
                _check_cancel()

                # 创建一个容器，返回df_dict，结构是，数据名称：df
                df_dict : dict = {}
                df_dict[table_name] = df

                if df_dict is None:
                    logging.error("No data downloaded from ISM")
                    return None

                if return_csv and df_dict:
                    # 如果需要下载csv，传入参数=True
                    _check_cancel()
                    for name, df in df_dict.items():
                        try:
                            data_folder_path = os.path.join(os.fspath(CSV_DATA_FOLDER), name)
                            os.makedirs(data_folder_path, exist_ok=True)
                            csv_path = os.path.join(data_folder_path, f"{name}.csv")
                            df.to_csv(csv_path, index=True)
                            logging.info("%s saved to %s Successfully!", name, csv_path)
                        except Exception as err:
                            logging.error(
                                "%s FAILED DOWNLOAD CSV in method 'to_db', since %s", name, err
                            )
                            print("下载csv失败，ism423，前面都正常")
                            continue

        except CancelledError:
            raise
        finally:
            try:
                self.driver.quit()
            except Exception:
                pass

        return df_dict if return_csv else None


if __name__ == "__main__":
    json_dict = {
        "ism_manufacture_m": {
            "name": "ISM_manufacture"
        },
        "ism_service_m": {
            "name": "ISM_service"
        }
    }
    ism = ISMDownloader(json_dict = json_dict, api_key = "1", request_year = 2020)
    ism.to_db(return_csv=True)


