"""TradingEconomics downloader implementation."""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false

from __future__ import annotations

import logging
import os
import random
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
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


class TEDownloader(DataDownloader):
    url: str = "https://tradingeconomics.com/united-states/"
    time_pause: float = random.uniform(1, 1.3)
    time_wait: int = 10

    def __init__(
        self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.start_year: int = request_year
        self.start_date: str = f"{request_year}-01-01"
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def _calc_function(
        self, x1: float, x2: float, y1: float, y2: float
    ) -> Tuple[float, float]:
        gradient = round((y1 - y2) / (x1 - x2), 3)
        intercept = round((y1 - gradient * x1), 3)
        return float(gradient), float(intercept)

    def _get_data_from_trading_economics_month(
        self,
        data_name: str,
        check_cancel: Optional[Callable[[], None]] = None,
    ) -> Optional[pd.DataFrame]:
        if check_cancel is not None:
            check_cancel()
        url = self.url + data_name.replace("_", "-")
        self.driver.get(url)
        if check_cancel is not None:
            check_cancel()
        time.sleep(TEDownloader.time_pause)

        try:
            if check_cancel is not None:
                check_cancel()
            five_year_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dateSpansDiv"]/a[3]'))
            )
            self.driver.execute_script("arguments[0].click();", five_year_button)
            time.sleep(TEDownloader.time_pause)
        except (
            TimeoutException,
            ElementClickInterceptedException,
            NoSuchElementException,
            StaleElementReferenceException,
        ) as e:
            logger.error("%s FAILED TO CLICK 5y button, %s", data_name, e)
            return None

        try:
            if check_cancel is not None:
                check_cancel()
            chart_type_button = WebDriverWait(
                self.driver, TEDownloader.time_wait
            ).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="chart"]/div/div/div[1]/div/div[3]/div/button')
                )
            )
            self.driver.execute_script("arguments[0].click();", chart_type_button)
            time.sleep(TEDownloader.time_pause)
            if check_cancel is not None:
                check_cancel()
            chart_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="chart"]/div/div/div[1]/div/div[3]/div/div/div[1]/button',
                    )
                )
            )
            self.driver.execute_script("arguments[0].click();", chart_button)
            time.sleep(TEDownloader.time_wait)
        except (
            TimeoutException,
            ElementClickInterceptedException,
            NoSuchElementException,
            StaleElementReferenceException,
        ) as e:
            logger.error("%s FAILED TO CLICK chart buttons, %s", data_name, e)
            return None

        try:
            if check_cancel is not None:
                check_cancel()
            original_html = self.driver.page_source
            soup = BeautifulSoup(original_html, "lxml")
            row = soup.find("tr", class_="datatable-row")
            if isinstance(row, Tag):
                tds = row.find_all("td")
                if len(tds) >= 2:
                    current_num = float(tds[1].text.strip())
                    previous_num = float(tds[2].text.strip())
                    current_data_date = str(tds[4].text.replace(" ", "_"))
                else:
                    raise Exception(
                        f"{data_name}, tds tag's length haven't reach 2, during html convert stage"
                    )
            else:
                raise Exception(
                    f"{data_name}, HAVEN'T FOUND ROWS during html convert stage"
                )

            rects = soup.find_all("rect", class_="highcharts-point")
            heights: List[float] = []
            for rect in rects:
                if isinstance(rect, Tag):
                    h = rect.get("height")
                    if h is not None:
                        try:
                            heights.append(float(str(h)))
                        except Exception:
                            continue

            gradient, intercept = self._calc_function(
                heights[-1], heights[-2], current_num, previous_num
            )
            data_list = [intercept + gradient * num for num in heights]

            month_map = {
                "Jan": 1,
                "Feb": 2,
                "Mar": 3,
                "Apr": 4,
                "May": 5,
                "Jun": 6,
                "Jul": 7,
                "Aug": 8,
                "Sep": 9,
                "Oct": 10,
                "Nov": 11,
                "Dec": 12,
            }
            month_abbr, year_str = current_data_date.split("_")
            month_int: int = month_map[month_abbr]
            year_int: int = int(year_str)
            end_date = datetime(year_int, month_int, 1)
            months_list = [
                (end_date - relativedelta(months=i)).strftime("%b_%Y")
                for i in reversed(range(61))
            ]
            df = pd.DataFrame(data={"date": months_list, "value": data_list})
            return df
        except Exception as e:
            logger.error("%s FAILED TO EXTRACT data from html, %s", data_name, e)
            return None

    def to_db(
        self,
        return_csv: bool = False,
        max_workers: Optional[int] = None,
        cancel_token: Optional[CancellationToken] = None,
    ) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        try:
            for table_name, table_config in self.json_dict.items():
                _check_cancel()
                data_name = table_config["name"]
                df = self._get_data_from_trading_economics_month(
                    data_name=data_name, check_cancel=_check_cancel
                )
                if df is None:
                    logger.error(
                        "FAILED TO EXTRACT %s, check PREVIOUS loggings", table_name
                    )
                    continue
                converter = DatabaseConverter()
                _check_cancel()
                converter.write_into_db(
                    df=df,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"],
                )
                _check_cancel()
                df_dict[table_name] = df
        except CancelledError:
            raise
        finally:
            try:
                self.driver.quit()
            except Exception:
                pass

        if return_csv and df_dict:
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
                    continue

        return df_dict if return_csv else None
