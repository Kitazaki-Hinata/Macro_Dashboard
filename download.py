# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false

import os
import json
import re
import time
import beaapi
import logging
import sqlite3
import random
import numpy as np
import requests
import debug.mock_api as mock_api
import pandas as pd
import yfinance as yf
import queue
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Tuple
from typing import cast

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        ElementClickInterceptedException, StaleElementReferenceException)
from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 新增: 并发与线程同步
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 全局 DB 写锁，避免并发写入 SQLite 导致数据丢失或锁冲突
DB_WRITE_LOCK = threading.Lock()

# 模块级 logger（与异步日志模块配合使用）
logger = logging.getLogger(__name__)


def _exponential_backoff_delays(max_attempts: int, base: float = 0.5, factor: float = 2.0, jitter: float = 0.25) -> List[float]:
    """Generate delays for exponential backoff with jitter."""
    delays: List[float] = []
    d = base
    for _ in range(max_attempts):
        delays.append(max(0.0, d + random.uniform(-jitter, jitter)))
        d *= factor
    return delays


def http_get_with_retry(url: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: float = 30.0, max_attempts: int = 4) -> requests.Response:
    delays = _exponential_backoff_delays(max_attempts)
    last_exc: Optional[Exception] = None
    for i, delay in enumerate(delays, start=1):
        try:
            t0 = time.perf_counter()
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            dt = time.perf_counter() - t0
            logger.info("HTTP GET %s attempt=%d status=%s in %.3fs", url, i, getattr(resp, 'status_code', 'NA'), dt)
            if resp.ok:
                return resp
            last_exc = Exception(f"status={resp.status_code}")
        except Exception as e:
            last_exc = e
            logger.warning("HTTP GET %s attempt=%d failed: %s", url, i, e)
        if i < max_attempts:
            time.sleep(delay)
    # all failed
    raise Exception(f"GET {url} failed after {max_attempts} attempts: {last_exc}")


def http_post_with_retry(url: str, *, data: Any = None, json_data: Any = None, headers: Optional[Dict[str, str]] = None, timeout: float = 30.0, max_attempts: int = 4, delay_seconds: Optional[float] = None) -> requests.Response:
    # 支持固定重试间隔（例如 BLS 要求 5s），否则使用指数回退
    delays = [delay_seconds] * max_attempts if delay_seconds is not None else _exponential_backoff_delays(max_attempts)
    last_exc: Optional[Exception] = None
    for i, delay in enumerate(delays, start=1):
        try:
            t0 = time.perf_counter()
            resp = requests.post(url, data=data, json=json_data, headers=headers, timeout=timeout)
            dt = time.perf_counter() - t0
            logger.info("HTTP POST %s attempt=%d status=%s in %.3fs", url, i, getattr(resp, 'status_code', 'NA'), dt)
            if resp.ok:
                return resp
            last_exc = Exception(f"status={resp.status_code}")
        except Exception as e:
            last_exc = e
            logger.warning("HTTP POST %s attempt=%d failed: %s", url, i, e)
        if i < max_attempts:
            try:
                if delay is None:
                    # 无延迟（极端情况），直接继续
                    continue
                logger.info("Retrying POST in %.1fs (attempt %d/%d)", float(delay), i + 1, max_attempts)
                time.sleep(float(delay))
            except Exception:
                # 任何睡眠异常都不应阻断重试
                pass
    raise Exception(f"POST {url} failed after {max_attempts} attempts: {last_exc}")


def yf_download_with_retry(symbol: str, *, start: str, end: str, interval: str = "1d", max_attempts: int = 5) -> pd.DataFrame:
    """Wrapper around yfinance.download with exponential backoff.

    - Explicitly sets auto_adjust=False to avoid FutureWarning noise and preserves raw OHLCV.
    - Sets threads=False to reduce internal concurrency (we already manage external concurrency).
    - Retries on YFRateLimitError or empty DataFrame results.
    """
    delays = _exponential_backoff_delays(max_attempts=max_attempts, base=1.0, factor=2.0, jitter=0.5)
    last_err: Optional[Exception] = None
    # Lazy import to avoid hard dependency for exception
    try:
        from yfinance.exceptions import YFRateLimitError  # type: ignore
    except Exception:  # pragma: no cover - fallback when API surface changes
        class YFRateLimitError(Exception):
            pass

    for i, dly in enumerate(delays, start=1):
        try:
            t0 = time.perf_counter()
            df = pd.DataFrame(
                yf.download(
                    symbol,
                    start=start,
                    end=end,
                    interval=interval,
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )
            )
            dt = time.perf_counter() - t0
            logger.info("YF GET %s attempt=%d rows=%d in %.3fs", symbol, i, len(df), dt)
            # If API answers but rate-limited, df could be empty
            if not df.empty:
                return df
            last_err = Exception("empty dataframe")
        except Exception as e:  # catch rate limit and network errors
            last_err = e
            # Heuristics: only warn, we'll retry
            logger.warning("YF GET %s attempt=%d failed: %s", symbol, i, getattr(e, "message", str(e)))
        if i < max_attempts:
            time.sleep(dly)
    # All attempts failed or empty
    raise Exception(f"yfinance download failed for {symbol} after {max_attempts} attempts: {last_err}")


class DatabaseConverter:
    _MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    end_date: date = date.today()

    def __init__(self, db_file: str = 'data.db') -> None:
        self.db_file: str = db_file
        self.conn: sqlite3.Connection = sqlite3.connect(db_file)
        self.cursor: sqlite3.Cursor = self.conn.cursor()

    @staticmethod
    def _convert_month_str_to_num(month_str: str) -> Optional[int]:
        return DatabaseConverter._MONTH_MAP.get(str(month_str).casefold(), None)

    @staticmethod
    def _rename_bea_date_col(df: pd.DataFrame) -> pd.DataFrame:
        '''modify time index, unify all time index in different dataframe(time series dataframe'''
        try:
            # df.drop("TimePeriod", axis=1, inplace=True)  # remove original date index
            date_col = df.pop("date")  # type: ignore
            df.insert(0, "date", date_col)  # type: ignore
            return df
        except Exception as e:
            logging.error(f"{e}, FAILED to write into database")
            df = pd.DataFrame()
            return df

    @staticmethod
    def _format_converter(df: Optional[pd.DataFrame], data_name: str, is_pct_data: bool) -> pd.DataFrame:
        """将不同来源的数据统一为两列: date(YYYY-MM-DD) + value 列名为 data_name。
        足够健壮地应对 None/Timestamp/int 等类型，并容忍短表、重复、缺失。
        """
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.copy()

        def finalize_with_date_first(df_in: pd.DataFrame) -> pd.DataFrame:
            # 统一 date 列为字符串 YYYY-MM-DD，去重、去空
            if "date" not in df_in.columns:
                return df_in
            dates = pd.to_datetime(df_in["date"], errors="coerce")
            df_in = df_in.assign(date=dates.dt.strftime("%Y-%m-%d"))
            df_in = df_in.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
            # 将目标列移到首列
            if data_name in df_in.columns:
                cols = ["date"] + [c for c in df_in.columns if c != "date"]
                df_in = df_in.reindex(columns=cols)
            return df_in

        logger.debug("_format_converter start: data=%s empty=%s columns=%s index_name=%s shape=%s", data_name, df.empty, list(df.columns), getattr(df.index, 'name', None), tuple(df.shape))
        # 1) BEA（索引为 'YYYY' | 'YYYYQn' | 'YYYYMM'）
        try:
            sample = str(df.index[0]) if len(df.index) else ""
            if re.fullmatch(r"\d{4}", sample):
                logger.debug("_format_converter matched BEA annual for %s (sample=%s)", data_name, sample)
                # 年度：用当年末一天
                df["date"] = [f"{int(y)}-12-31" for y in df.index.astype(str)]
                df = DatabaseConverter._rename_bea_date_col(df)
                return finalize_with_date_first(df.rename_axis(None, axis=1))
            if re.fullmatch(r"\d{4}Q[1-4]", sample):
                logger.debug("_format_converter matched BEA quarterly for %s (sample=%s)", data_name, sample)
                def q_to_date(s: str) -> str:
                    y, q = s.split("Q"); y = int(y); q = int(q)
                    m = q * 3 + 1
                    if m > 12:
                        y += 1; m = 1
                    return f"{y}-{m:02d}-01"
                df["date"] = [q_to_date(str(s)) for s in df.index]
                df = DatabaseConverter._rename_bea_date_col(df)
                return finalize_with_date_first(df)
            if re.fullmatch(r"\d{4}M\d{2}", sample):
                logger.debug("_format_converter matched BEA monthly for %s (sample=%s)", data_name, sample)
                def m_to_date(s: str) -> str:
                    y, m = s.split("M"); y = int(y); m = int(m)
                    if m == 12:
                        y += 1; m = 1
                    else:
                        m += 1
                    return f"{y}-{m:02d}-01"
                df["date"] = [m_to_date(str(s)) for s in df.index]
                df = DatabaseConverter._rename_bea_date_col(df)
                return finalize_with_date_first(df)
        except Exception as e:
            logging.warning(f"BEA match failed in _format_converter: {e}")

        # 2) yfinance（OHLCV）
        try:
            ohlcv = {"Open", "High", "Low", "Close", "Volume"}
            if set(df.columns) >= ohlcv:
                logger.debug("_format_converter matched YF OHLCV for %s", data_name)
                # 将索引转为日期字符串（统一使用 to_datetime）
                dates = pd.to_datetime(df.index, errors="coerce").strftime("%Y-%m-%d")
                df = df.assign(date=dates)
                # 仅保留 Close => data_name
                out = pd.DataFrame({
                    "date": df["date"],
                    data_name: df["Close"]
                })
                return finalize_with_date_first(out)
        except Exception as e:
            logging.warning(f"yfinance match failed in _format_converter: {e}")

        # 3) FRED（包含 'date' 列 + 一个数值列）
        try:
            if "date" in df.columns and str(df["date"].iloc[1])[4] == "-":
                logger.debug("_format_converter matched FRED style for %s", data_name)
                # 找到第一个非 date 的数据列
                value_cols = [c for c in df.columns if c != "date"]
                if value_cols:
                    col = value_cols[0]
                    out = df[["date", col]].copy()
                    out = out.rename(columns={col: data_name})
                    return finalize_with_date_first(out)
        except Exception as e:
            logging.warning(f"FRED match failed in _format_converter: {e}")

        # 4) BLS（year, period, value/MoM_growth）
        try:
            cols = list(df.columns)
            if cols == ["year", "period", "value"] or cols == ["year", "period", "MoM_growth"]:
                logger.debug("_format_converter matched BLS style for %s", data_name)
                period = df["period"].astype(str)
                # 统一生成 month 为 Series[str]
                if period.str.startswith("M").any():
                    month_series = period.str[1:].astype(int)
                    month_series = month_series.where(month_series != 12, 0) + 1
                    month_series = month_series.astype(str).str.zfill(2)
                elif period.str.startswith("Q").any():
                    logger.debug("_format_converter BLS quarterly period detected for %s", data_name)
                    def q_to_month(s: str) -> int:
                        try:
                            q = int(s[1:])
                            return {1: 4, 2: 7, 3: 10, 4: 1}.get(q, 1)
                        except Exception:
                            return 1
                    month_series = period.apply(q_to_month).astype(str).str.zfill(2)
                else:
                    month_series = pd.Series(["01"] * len(df), index=df.index)

                year_num = pd.to_numeric(df["year"], errors="coerce")
                year_num = year_num.where(month_series != "01", year_num + 1)
                month_num = pd.to_numeric(month_series, errors="coerce")
                dt = pd.to_datetime({"year": year_num, "month": month_num, "day": 1}, errors="coerce")
                df["date"] = dt.dt.strftime("%Y-%m-%d")
                # 选择数值列
                val_col = "value" if "value" in df.columns else "MoM_growth"
                out = df[["date", val_col]].copy().rename(columns={val_col: data_name})
                return finalize_with_date_first(out)
        except Exception as e:
            logging.warning(f"BLS match failed in _format_converter: {e}")

        # 5) TE（月名_年份）
        try:
            if "date" in df.columns and df["date"].astype(str).str.contains(r"^[A-Za-z]{3}_[0-9]{4}$").any():
                logger.debug("_format_converter matched TE style for %s", data_name)
                df = df.rename(columns={"value": data_name, "date": "Date"})
                split_data = df["Date"].astype(str).str.split("_", expand=True)
                month_str = split_data[0]
                year = pd.to_numeric(split_data[1], errors="coerce")
                dec_mask = (month_str == "Dec")
                year = year.where(~dec_mask, year + 1)
                month = month_str.apply(DatabaseConverter._convert_month_str_to_num)
                month = month.where(~dec_mask, 1)
                month_num = pd.to_numeric(month, errors="coerce")
                dt = pd.to_datetime({"year": year, "month": month_num, "day": 1}, errors="coerce")
                df["date"] = dt.dt.strftime("%Y-%m-%d")
                df = df.drop(columns=["Date"], errors="ignore")
                date_col = df.pop("date")
                df.insert(0, "date", date_col)
                return finalize_with_date_first(df)
        except Exception as e:
            logging.warning(f"TE match failed in _format_converter: {e}")

        # 兜底：如果已有 date 列，则标准化；若无，则尝试从索引转
        try:
            if "date" in df.columns:
                logger.debug("_format_converter fallback by date column for %s", data_name)
                return finalize_with_date_first(df.rename(columns={df.columns[1]: data_name}) if len(df.columns) > 1 else df)
            else:
                logger.debug("_format_converter fallback by index->date for %s", data_name)
                dates = pd.to_datetime(pd.Series(df.index).astype(str), errors="coerce").dt.strftime("%Y-%m-%d")
                out = pd.DataFrame({"date": dates})
                if df.shape[1] >= 1:
                    out[data_name] = list(df.iloc[:, 0])
                return finalize_with_date_first(out)
        except Exception as e:
            logging.warning(f"fallback in _format_converter failed: {e}")
            return df

    def _create_ts_sheet(self, start_date : str) -> sqlite3.Cursor:
        """If time_series_table does not exist, then create new db
        如果sheet不存在，创建sheet"""
        cursor = self.cursor
        logger.debug("ensure Time_Series table exists (start_date=%s)", start_date)

        # 尝试寻找database中是否存在ts表，如果存在，则跳过create
        cursor.execute("SELECT name FROM sqlite_master WHERE type= 'table' AND name  = 'Time_Series'")
        table_exists = cursor.fetchone() is not None  # if table exists, return True

        # 如果没有ts表，则尝试创建一个
        try:
            if not table_exists:
                t0 = time.perf_counter()
                cursor.execute("CREATE TABLE IF NOT EXISTS Time_Series(date DATE PRIMARY KEY)")
                current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                while current_date <= DatabaseConverter.end_date:  # 直接比较date对象   # 添加时间列，循环写入从设置的开始日期一直到今天的所有日期
                    cursor.execute(
                        "INSERT OR IGNORE INTO Time_Series (date) VALUES (?)",
                        (current_date.strftime('%Y-%m-%d'),
                         )
                    )
                    current_date += timedelta(days=1)
                self.conn.commit()
                logger.info("Time_Series table created and initialized (%.3fs)", time.perf_counter() - t0)
                return cursor
            else:
                logger.info("Time_Series table already exists, continue")
                cursor.execute("SELECT MAX(date) FROM Time_Series")
                max_date_str = cursor.fetchone()[0]
                if not max_date_str:
                    # 表存在但没有行的极端情况：初始化最小日期
                    max_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                else:
                    max_date = datetime.strptime(max_date_str, '%Y-%m-%d').date()

                # 计算需要添加的日期
                current_date = datetime.now().date()
                if current_date > max_date:
                    t0 = time.perf_counter()
                    dates_to_add: List[date] = []
                    while current_date > max_date:
                        dates_to_add.append(current_date)
                        current_date -= timedelta(days=1)
                    # 插入数据
                    for d in dates_to_add:
                        cursor.execute("INSERT INTO Time_Series (date) VALUES (?)", (d.strftime('%Y-%m-%d'),))
                    self.conn.commit()
                    logger.info("Time_Series table appended %d date rows (%.3fs)", len(dates_to_add), time.perf_counter() - t0)
                return cursor

        except sqlite3.Error as e:
            logging.error(f"FAILED to create Time_Series table, since {e}")
            return cursor

    def write_into_db(
            self,
            df: pd.DataFrame,
            data_name: str,
            start_date : str,
            is_time_series: bool = False,
            is_pct_data: bool = False
    ):
        '''params df: df that used to write into db
        params data_name: used in db columns and errors
        params start_date, start date of  all data, used when create db sheet
        params is_time_series: judge whether it is time series data, incl. BEA, BLS, YF, TE, FRED
        params is_pct_data: input json data, bool value, "needs_pct"
        '''
        # 串行化整个写入过程，防止 Time_Series 全表替换时的竞态
        with DB_WRITE_LOCK:
            t_all = time.perf_counter()
            self._create_ts_sheet(start_date = start_date)
            cursor = self.cursor
            try:
                logger.info("write_into_db start: data=%s, is_time_series=%s, shape=%s", data_name, is_time_series, tuple(df.shape))
                if df.empty:
                    logger.error(f"{data_name} is empty, FAILED INSERT, locate in write_into_db")
                else:
                    if is_time_series:  # check whether Time_Series table exists
                        t0 = time.perf_counter()
                        df_after_modify_time: pd.DataFrame = DatabaseConverter._format_converter(df, data_name, is_pct_data)
                        logger.debug("%s after format: columns=%s, shape=%s", data_name, list(df_after_modify_time.columns), tuple(df_after_modify_time.shape))
                        if df_after_modify_time.empty or 'date' not in df_after_modify_time.columns:
                            logger.error(f"{data_name} reformat produced empty/invalid dataframe, skip writing")
                            return
                        # 标准化和去重
                        df_after_modify_time = df_after_modify_time.copy()
                        df_after_modify_time['date'] = pd.to_datetime(df_after_modify_time['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                        df_after_modify_time = df_after_modify_time.dropna(subset=['date']).drop_duplicates(subset=['date'], keep='last')
                        try:
                            cursor.execute(f"ALTER TABLE Time_Series ADD COLUMN {data_name} DOUBLE")
                            self.conn.commit()
                            logger.debug("added column '%s' to Time_Series", data_name)
                        except Exception:
                            logger.warning(f"{data_name} col name already exists in Time_Series, continue")

                        df_db = pd.read_sql("SELECT * FROM Time_Series", self.conn)  # 只读取日期列
                        result_db = df_db.merge(df_after_modify_time, on="date", how="left")

                        for col in df_after_modify_time.columns:
                            if col == 'date':
                                continue  # 跳过日期列
                            if f"{col}_x" in result_db.columns and f"{col}_y" in result_db.columns:
                                # 使用combine_first: y列优先，没有y时用x
                                result_db[col] = result_db[f"{col}_y"].combine_first(result_db[f"{col}_x"])
                                # 删除临时列
                                result_db.drop([f"{col}_x", f"{col}_y"], axis=1, inplace=True)

                        t_sql = time.perf_counter()
                        result_db.to_sql(
                            name="Time_Series",  # 同一张表或新表
                            con=self.conn,
                            if_exists="replace",
                            index=False
                        )

                        self.conn.commit()
                        logger.info("write_into_db(Time_Series/%s): wrote %d rows (format %.3fs + to_sql %.3fs, total %.3fs)",
                                    data_name, len(result_db), (t_sql - t0), (time.perf_counter() - t_sql), (time.perf_counter() - t0))

                        # 找到date列的索引位置，选择date列及后面的一列
                        df_after_modify_time = df_after_modify_time.iloc[:, -2:]
                        logger.debug("%s returns last 2 cols shape=%s", data_name, tuple(df_after_modify_time.shape))
                        logger.info("write_into_db finished: data=%s (%.3fs)", data_name, time.perf_counter() - t_all)
                        return df_after_modify_time
                    else:
                        # 其他数据则直接生成新sheet存入database当中
                        t_sql = time.perf_counter()
                        df.to_sql(
                            name=data_name,
                            con=self.conn,
                            if_exists='replace',  # if sheet exist, then replace
                            index=False
                        )
                        self.conn.commit()
                        logger.info("write_into_db(sheet=%s): wrote %d rows (to_sql %.3fs)", data_name, len(df), time.perf_counter() - t_sql)
                        logger.info("write_into_db finished: data=%s (%.3fs)", data_name, time.perf_counter() - t_all)
                        self.conn.close()
                        return df

            except Exception as e:
                logger.error(f"FAILED to write into database, in method write_into_db, since {e}")
                return


class DataDownloader(ABC):
    @abstractmethod
    def to_db(self, return_csv: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        """Download data and either write to DB or return DataFrames per table.
        If return_df=True, return a dict mapping table_name -> DataFrame; otherwise None.
        max_workers: Optional[int] for concurrent downloads (None => sensible default).
        """
        raise NotImplementedError


class BEADownloader(DataDownloader):
    current_year : int = date.today().year
    download_py_file_path : str = os.path.dirname(os.path.abspath(__file__))
    csv_data_folder : str = os.path.join(download_py_file_path, "csv")

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year : int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
        self.request_year: int = request_year
        self.time_range : str= ",".join(map(str, range(request_year, BEADownloader.current_year + 1)))
        self.time_range_lag : str = self.time_range[:-5]  # 去除最后5个字符，即去除最后一年

    def to_db(self, return_csv: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return None

        def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
            try:
                logger.info("BEA start: table=%s code=%s freq=%s years=%s", table_name, table_config.get("code"), table_config.get("freq"), self.time_range)
                try:
                    t0 = time.perf_counter()
                    bea_tbl = beaapi.get_data(
                        self.api_key,
                        datasetname=table_config["category"],
                        TableName=table_config["code"],
                        Frequency=table_config["freq"],
                        Year=self.time_range
                    )
                    logger.info("BEA fetched primary range for %s (%.3fs)", table_name, time.perf_counter() - t0)
                except beaapi.beaapi_error.BEAAPIResponseError:
                    t0 = time.perf_counter()
                    bea_tbl = beaapi.get_data(
                        self.api_key,
                        datasetname=table_config["category"],
                        TableName=table_config["code"],
                        Frequency=table_config["freq"],
                        Year=self.time_range_lag
                    )
                    logger.warning("BEA fallback years used for %s (%.3fs)", table_name, time.perf_counter() - t0)
                df: pd.DataFrame = pd.DataFrame(bea_tbl)
                try:
                    ld_series = df["LineDescription"].fillna("")
                    pick = ld_series.iloc[1] if len(ld_series) > 1 else (ld_series.iloc[0] if len(ld_series) else "")
                except Exception:
                    pick = ""
                df_filtered: pd.DataFrame = df[df["LineDescription"].isin([pick, ""])].copy()
                def _last_or_none(s: pd.Series) -> Any:
                    return s.iloc[-1] if len(s) else None
                df_modified: pd.DataFrame = pd.pivot_table(
                    df_filtered,
                    index="TimePeriod",
                    columns="LineDescription",
                    values="DataValue",
                    aggfunc=_last_or_none
                )
                df_modified.columns = [f"{table_config['name']}"]
                df_modified.index.name = "TimePeriod"
                logger.info(f"BEA_{table_name} Successfully extracted! rows={len(df_modified)}")

                if df_modified.empty:
                    logging.error(f"{table_name} is empty, FAILED INSERT, locate in to_db")
                    return table_name, None
                converter = DatabaseConverter()
                final_result_df = converter.write_into_db(
                    df = df_modified,
                    data_name=table_config["name"],
                    start_date  = str(date(self.request_year, 1, 1)),
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"]
                )
                return table_name, final_result_df
            except Exception as e:
                logger.error(f"{table_name} FAILED DOWNLOAD/REFORMAT in BEA worker: {e}")
                return table_name, None

        env_workers = os.environ.get('BEA_WORKERS')
        workers  = max_workers or (int(env_workers) if env_workers and env_workers.isdigit() else min(8, (os.cpu_count() or 4) * 2))    # workers是int，确认进程数量
        logger.info("BEA submitting %d tasks (workers=%d)", len(items), workers)
        with ThreadPoolExecutor(max_workers=workers) as ex:   # 创建一个线程池
            future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}   # 往线程池里面添加submit，每个submit添加worker函数用于下载，tn数据名称，cfg是json的参数
            for fut in as_completed(future_map):    # 获取线程池中的结果
                tn = future_map[fut]
                try:
                    name, df = fut.result()
                    if df is not None:
                        df_dict[name] = df
                    if return_csv:
                        for name, df in df_dict.items():
                            try:
                                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)
                                os.makedirs(data_folder_path, exist_ok=True)
                                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                                df.to_csv(csv_path, index=True)
                                logging.info(f"{name} saved to {csv_path} Successfully!")
                            except Exception as e:
                                logging.error(f"{name} FAILED DOWNLOAD CSV in method 'to_csv', since {e}")
                                continue
                except Exception as e:
                    logging.error(f"BEA future for {tn} raised: {e}")


class YFDownloader(DataDownloader):
    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key: Optional[str], request_year : int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.start_date : str  = str(request_year)+"-01-01"
        self.end_date : str = str(date.today())

    def to_db(self, return_csv: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return df_dict if return_csv else None

        def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
            try:
                index = table_config["code"]
                logger.info("YF start: table=%s symbol=%s range=%s..%s", table_name, index, self.start_date, self.end_date)
                t0 = time.perf_counter()
                data = yf_download_with_retry(index, start=self.start_date, end=self.end_date, interval="1d")
                logger.info("YF fetched: table=%s rows=%d (%.3fs)", table_name, len(data), time.perf_counter() - t0)
                try:
                    data.columns = data.columns.droplevel(1)
                except Exception:
                    pass
                if data.empty:
                    logger.warning("YF %s returned empty dataframe, skip DB write", table_name)
                    return table_name, None
                converter = DatabaseConverter()
                final_result_df = converter.write_into_db(
                    df=data,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"]
                )
                return table_name, final_result_df
            except Exception as e:
                logger.error("to_db, %s FAILED EXTRACT DATA from Yfinance, %s", table_name, e)
                return table_name, None

        # Lower concurrency to mitigate YF rate limit
        load_dotenv()
        env_workers = os.environ.get('YF_WORKERS')
        workers = max_workers or (int(env_workers) if env_workers and env_workers.isdigit() else min(6, (os.cpu_count() or 4)))
        logger.info("YF submitting %d tasks (workers=%d)", len(items), workers)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}
            for fut in as_completed(future_map):
                tn = future_map[fut]
                try:
                    name, df = fut.result()
                    if df is not None:
                        df_dict[name] = df
                    if return_csv:
                        for name, df in df_dict.items():
                            try:
                                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)
                                os.makedirs(data_folder_path, exist_ok=True)
                                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                                df.to_csv(csv_path, index=True)
                                logging.info(f"{name} saved to {csv_path} Successfully!")
                            except Exception as e:
                                logging.error(f"{name} FAILED DOWNLOAD CSV in method 'to_db', since {e}")
                                continue
                except Exception as e:
                    logging.error(f"YF future for {tn} raised: {e}")


class FREDDownloader(DataDownloader):
    url : str = r"https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year : int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
        self.start_date : str  = str(request_year)+"-01-01"
        self.end_date : str = str(date.today())

    def to_db(self, return_csv: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return df_dict if return_csv else None

        def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
            try:
                params = {
                    "series_id": table_config["code"],
                    "api_key": self.api_key,
                    "observation_start": self.start_date,
                    "observation_end": self.end_date,
                    "file_type": "json"
                }
                log_params = {k: v for k, v in params.items() if k != "api_key"}
                logger.info("FRED GET %s params=%s", FREDDownloader.url, log_params)
                t0 = time.perf_counter()
                resp = http_get_with_retry(FREDDownloader.url, params=params)
                data = resp.json()
                df = pd.DataFrame(data.get("observations", []))
                if df.empty:
                    raise Exception("empty observations")
                keep_cols = [c for c in df.columns if c in ("date", "value")]
                df = df[keep_cols].copy()

                if table_config.get("needs_pct", False):
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    df["MoM_growth"] = df["value"].pct_change()
                    df = df[["date", "MoM_growth"]]
                else:
                    df["value"] = df["value"].replace(".", np.nan)
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    if table_config.get("needs_cleaning", False):
                        df["value"] = df["value"].ffill()
                    df = df[["date", "value"]]

                converter = DatabaseConverter()
                final_result_df = converter.write_into_db(
                    df=df,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"]
                )
                logger.info(f"{table_name} Successfully extracted! rows={len(df)}")
                return table_name, final_result_df
            except Exception as e:
                logger.error(f"{table_name} FAILED EXTRACT DATA from FRED: {e}")
                return table_name, None

        load_dotenv()
        env_workers = os.environ.get('FRED_WORKERS')
        workers = max_workers or (int(env_workers) if env_workers and env_workers.isdigit() else min(12, (os.cpu_count() or 4) * 2))
        logger.info("FRED submitting %d tasks (workers=%d)", len(items), workers)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}
            for fut in as_completed(future_map):
                tn = future_map[fut]
                try:
                    name, df = fut.result()
                    if  df is not None:
                        df_dict[name] = df
                    if return_csv:
                        for name, df in df_dict.items():
                            try:
                                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)
                                os.makedirs(data_folder_path, exist_ok=True)
                                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                                df.to_csv(csv_path, index=True)
                                logging.info(f"{name} saved to {csv_path} Successfully!")
                            except Exception as e:
                                logging.error(f"{name} FAILED DOWNLOAD CSV in method 'to_db', since {e}")
                                continue
                except Exception as e:
                    logging.error(f"FRED future for {tn} raised: {e}")


class BLSDownloader(DataDownloader):
    url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers: Tuple[str, str] = ('Content-type', 'application/json')

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key : str, request_year : int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
        self.start_year: int  = request_year
        self.start_date : str  = str(request_year)+"-01-01"

    def to_db(self, return_csv : bool = False, debug : bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        if debug is True:
            converter = DatabaseConverter()
            converter.write_into_db(
                df=mock_api.return_bls_data(),
                data_name="Trial",
                start_date=self.start_date,
                is_time_series=True,
                is_pct_data=False
            )
        else:
            items = list(self.json_dict.items())
            if not items:
                return df_dict if return_csv else None

            def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
                try:
                    logger.info("BLS POST %s series_id=%s years=%s..%s", BLSDownloader.url, table_config.get("code"), self.start_year, date.today().year)
                    params = json.dumps(
                        {
                            "seriesid": [table_config["code"]],
                            "startyear": self.start_year,
                            "endyear": date.today().year,
                            "registrationKey": self.api_key
                            }
                        )
                    t0 = time.perf_counter()
                    load_dotenv()
                    bls_timeout_env = os.environ.get('BLS_POST_TIMEOUT')
                    bls_timeout = float(bls_timeout_env) if bls_timeout_env else 60.0
                    context = http_post_with_retry(
                        BLSDownloader.url,
                        data=params,
                        headers=dict([BLSDownloader.headers]),
                        timeout=bls_timeout,
                        max_attempts=4,
                        delay_seconds=5.0
                    )
                    json_data = json.loads(context.text)
                    logger.info(f"{table_name} Successfully download data")
                except Exception as e:
                    logger.error(f"{table_name} FAILED EXTRACT DATA from BLS, probably due to API or network issues: {e}")
                    return table_name, None

                try:
                    df = pd.DataFrame(json_data["Results"]["series"][0]["data"]).drop(
                        columns=["periodName", "latest", "footnotes"])
                except Exception:
                    try:
                        df = pd.DataFrame(json_data)
                        logger.warning(f"{table_name} FAILED REFORMAT: DROP USELESS COLUMNS, continue")
                    except Exception as e:
                        logger.error(f"{table_name} FAILED REFORMAT data from BLS, errors in df managing, {e}")
                        return table_name, None

                if table_config["needs_pct"] is True:
                    try:
                        df["value"] = pd.to_numeric(df["value"])
                        df["MoM_growth"] = ((df["value"] - df["value"].shift(1)) / (df["value"].shift(1)) * -1).shift(-1)
                        df = df.drop(df.columns[-2], axis=1)
                    except Exception as e:
                        logger.error(f"{table_name} FAILED REFORMAT PERCENTAGE, probably due to df error, {e}")
                        return table_name, None

                converter = DatabaseConverter()
                final_result_df = converter.write_into_db(
                    df=df,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"]
                )
                logger.info(f"{table_name} Successfully extracted! rows={len(df)}")
                return table_name, final_result_df

            # Keep BLS concurrency conservative to avoid server throttling（支持环境变量覆盖）
            load_dotenv()
            env_workers = os.environ.get('BLS_WORKERS')
            workers = max_workers or (int(env_workers) if env_workers and env_workers.isdigit() else 4)
            logger.info("BLS submitting %d tasks (workers=%d)", len(items), workers)
            with ThreadPoolExecutor(max_workers=workers) as ex:
                future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}
                for fut in as_completed(future_map):
                    tn = future_map[fut]
                    try:
                        name, df = fut.result()
                        if df is not None:
                            df_dict[name] = df
                        if return_csv:
                            for name, df in df_dict.items():
                                try:
                                    data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)
                                    os.makedirs(data_folder_path, exist_ok=True)
                                    csv_path = os.path.join(data_folder_path, f"{name}.csv")
                                    df.to_csv(csv_path, index=True)
                                    logging.info(f"{name} saved to {csv_path} Successfully!")
                                except Exception as e:
                                    logging.error(f"{name} FAILED DOWNLOAD CSV in method 'to_db', since {e}")
                                    continue
                    except Exception as e:
                        logging.error(f"BLS future for {tn} raised: {e}")


class TEDownloader(DataDownloader):
    url : str = "https://tradingeconomics.com/united-states/"
    # 将固定 sleep 降低，更多依赖显式等待；必要时仍有微小 pause
    time_pause : float = 0.2
    time_wait : int = 10  # 最大等待秒数（用于显式等待）

    @staticmethod
    def _build_chrome_options(headless: bool) -> Options:
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        # 更快的页面加载策略：DOMContentLoaded 即返回
        try:
            options.page_load_strategy = 'eager'
        except Exception:
            pass
        # 禁用图片加载，减少资源
        options.add_experimental_option(
            'prefs',
            {
                'profile.managed_default_content_settings.images': 2,
            }
        )
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-first-run")
        return options

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key : str, request_year : int, *, headless: bool = False):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.start_year: int  = request_year
        self.start_date: str = str(request_year) + "-01-01"
        options = TEDownloader._build_chrome_options(headless)
        self.driver = webdriver.Chrome(options=options)
        try:
            self.driver.maximize_window()
        except Exception:
            pass
        try:
            self.driver.set_page_load_timeout(25)
        except Exception:
            pass
        self._headless = headless
        self._popups_dismissed = False
        # 请求级缓存：内存 + 本地 CSV（短期复用）
        self._mem_cache: Dict[str, Tuple[float, pd.DataFrame]] = {}
        try:
            self._cache_ttl_seconds = int(os.environ.get('TE_CACHE_TTL_SECONDS', '600'))
        except Exception:
            self._cache_ttl_seconds = 600
        try:
            self._cache_dir = os.path.join(os.path.dirname(__file__), 'cache', 'te')
        except Exception:
            self._cache_dir = os.path.join(os.getcwd(), 'cache', 'te')
        try:
            os.makedirs(self._cache_dir, exist_ok=True)
        except Exception:
            pass
        logger.info("TE WebDriver initialized (headless=%s)", self._headless)

    def _cache_path(self, data_name: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", data_name)
        return os.path.join(self._cache_dir, f"{safe}.csv")

    def _cache_read(self, data_name: str) -> Optional[pd.DataFrame]:
        now = time.time()
        # 内存缓存优先
        mem = self._mem_cache.get(data_name)
        if mem is not None:
            ts, df = mem
            if now - ts <= self._cache_ttl_seconds:
                logger.info("TE cache hit (memory) for %s", data_name)
                return df.copy()
        # 本地缓存次之
        path = self._cache_path(data_name)
        try:
            if os.path.exists(path):
                mtime = os.path.getmtime(path)
                if now - mtime <= self._cache_ttl_seconds:
                    df = pd.read_csv(path)
                    logger.info("TE cache hit (disk) for %s", data_name)
                    # 回填内存缓存
                    self._mem_cache[data_name] = (now, df)
                    return df
        except Exception as e:
            logger.warning("TE cache read failed for %s: %s", data_name, e)
        return None

    def _cache_write(self, data_name: str, df: pd.DataFrame) -> None:
        try:
            self._mem_cache[data_name] = (time.time(), df.copy())
            path = self._cache_path(data_name)
            df.to_csv(path, index=False)
        except Exception as e:
            logger.warning("TE cache write failed for %s: %s", data_name, e)

    def _get_config_by_name(self, data_name: str) -> Optional[Dict[str, Any]]:
        for tn, cfg in self.json_dict.items():
            try:
                if cfg.get('name') == data_name:
                    return cfg
            except Exception:
                continue
        return None

    def _resolve_locators(self, kind: str, data_name: str, defaults: List[Tuple[str, str]]) -> List[Tuple[Any, str]]:
        # 支持在 json 配置里为某个指标覆写定位器：
        # { "locators": { "fiveY": ["xpath://div...", "css:#dateSpansDiv a:nth-child(3)"] } }
        cfg = self._get_config_by_name(data_name) or {}
        loc_cfg = (cfg.get('locators') or {}).get(kind)
        locs: List[Tuple[Any, str]] = []
        def parse_one(spec: str) -> Tuple[Any, str]:
            s = spec.strip()
            if s.lower().startswith('css:'):
                return (By.CSS_SELECTOR, s[4:])
            if s.lower().startswith('xpath:'):
                return (By.XPATH, s[6:])
            # 默认按 XPATH 处理
            return (By.XPATH, s)
        if isinstance(loc_cfg, list) and loc_cfg:
            for s in loc_cfg:
                try:
                    by, sel = parse_one(str(s))
                    locs.append((by, sel))
                except Exception:
                    continue
        # 追加默认候选，保证兜底
        for kind_by, kind_sel in defaults:
            if isinstance(kind_by, str):
                # 将字符串表述转换为 selenium By
                by = By.CSS_SELECTOR if kind_by.lower() == 'css' else By.XPATH
                locs.append((by, kind_sel))
            else:
                locs.append((kind_by, kind_sel))
        return locs

    def _calc_function(self, x1: float, x2: float, y1: float, y2: float) -> Tuple[float, float]:
        """解二元一次方程，用于计算数据 used for data calculation"""
        gradient = np.round((y1 - y2)/(x1-x2), 3)
        intercept = np.round((y1 - gradient*x1), 3)
        # 确保返回内置 float，避免类型检查告警
        return float(gradient), float(intercept)

    def _get_data_from_trading_economics_month(self, data_name: str) -> Optional[pd.DataFrame]:
        """提取月度数据的代码，季度数据需要单独写
        主要流程：访问页面，点击5y按钮，点击bar按钮，提取table数字，提取bar长度，反向计算数据"""

        url = self.url + data_name.replace("_", "-")
        t0 = time.perf_counter()
        self.driver.get(url)
        logger.info("TE open page %s (%.3fs)", url, time.perf_counter() - t0)
        # 等到日期区块或图表容器出现，避免固定 sleep
        try:
            WebDriverWait(self.driver, TEDownloader.time_wait).until(
                EC.presence_of_element_located((By.ID, 'chart'))
            )
        except Exception:
            pass
        # Try cache first（请求级缓存）
        cached = self._cache_read(data_name)
        if cached is not None and not cached.empty:
            return cached
        # Try dismissing cookie/terms popups if present（仅首次会做，后续跳过）
        self._dismiss_te_popups(data_name)

        # click "5y" button
        # Try various strategies to click 5Y；若失败则回退为使用当前可见范围的数据
        clicked_5y = self._click_5y(data_name)
        if not clicked_5y:
            logger.warning(f"{data_name} FAILED TO CLICK 5y button, fallback to current visible range")

        # 检查是否已是柱状图；若不是再切换，避免多余步骤
        def _wait_bars(timeout: int = 8) -> List[Any]:
            try:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'svg rect.highcharts-point'))
                )
            except Exception:
                return []

        bars = _wait_bars(timeout=4)
        if not bars:
            try:
                # 支持自适应定位器
                type_locs = self._resolve_locators('chartTypeButton', data_name, defaults=[('xpath', '//*[@id="chart"]/div/div/div[1]/div/div[3]/div/button')])
                clicked = False
                for by, sel in type_locs:
                    try:
                        chart_type_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                            EC.element_to_be_clickable((by, sel))
                        )
                        self.driver.execute_script("arguments[0].click();", chart_type_button)
                        clicked = True
                        break
                    except Exception:
                        continue
                if not clicked:
                    raise Exception("chart type button not found")
                time.sleep(TEDownloader.time_pause)
                try:
                    bar_locs = self._resolve_locators('barButton', data_name, defaults=[('xpath', '//*[@id="chart"]/div/div/div[1]/div/div[3]/div/div/div[1]/button')])
                    clicked_bar = False
                    for by, sel in bar_locs:
                        try:
                            chart_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                                EC.element_to_be_clickable((by, sel))
                            )
                            self.driver.execute_script("arguments[0].click();", chart_button)
                            clicked_bar = True
                            break
                        except Exception:
                            continue
                    if not clicked_bar:
                        raise Exception("bar chart button not found")
                    bars = _wait_bars(timeout=8)
                    if not bars:
                        logger.error(f"{data_name} NO BARS after switching chart type")
                        return None
                except Exception as e:
                    logger.error(f"{data_name} FAILED TO CLICK 'bar chart type' button, {e}")
                    return None
            except Exception as e:
                logger.error(f"{data_name} FAILED TO CLICK 'chart type' button, {e}")
                return None

        # 读取统计面板中的“当前/上期/日期”三要素
        try:
            # 多定位器兜底，面板区域在 #panelData 内常见
            row = None
            row_selectors = [
                (By.CSS_SELECTOR, '#panelData .datatable-row'),
                (By.CSS_SELECTOR, '#panelData table tbody tr'),
                (By.XPATH, '//*[@id="panelData"]//tr[contains(@class, "datatable-row") or position()=1]')
            ]
            for by, sel in row_selectors:
                try:
                    row = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                        EC.presence_of_element_located((by, sel))
                    )
                    break
                except Exception:
                    continue
            if row is None:
                raise Exception("panel row not found")

            tds = row.find_elements(By.TAG_NAME, 'td')
            if len(tds) >= 5:
                current_num = float(tds[1].text.strip())
                previous_num = float(tds[2].text.strip())
                current_data_date = str(tds[4].text.replace(" ", "_"))
            else:
                raise Exception("datatable-row tds < 5")

            # 提取柱状图高度，至少需要两个点用于反推线性关系
            rects = self.driver.find_elements(By.CSS_SELECTOR, 'svg rect.highcharts-point')
            heights: List[float] = []
            for rect in rects:
                try:
                    h = rect.get_attribute('height')
                    if h is not None:
                        heights.append(float(str(h)))
                except Exception:
                    continue
            if len(heights) < 2:
                raise Exception("not enough bars to derive scale (need >=2)")

            # 线性关系：以最后两个柱对应当前/上期数值来求解
            gradient, intercept = self._calc_function(heights[-1], heights[-2], current_num, previous_num)
            data_list: List[float] = []
            for num in heights:
                data_list.append(intercept + gradient * num)

            # 构造与柱子数量等长的月份序列（从最早到最新）
            month_map = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
            }
            month_abbr, year_str = current_data_date.split("_")
            end_date = datetime(int(year_str), month_map[month_abbr], 1)
            months_len = len(heights)
            months_list = [
                (end_date - relativedelta(months=i)).strftime("%b_%Y")
                for i in reversed(range(months_len))
            ]

            df = pd.DataFrame(data={"date": months_list, "value": data_list})
            logger.info("TE extracted %s rows=%d", data_name, len(df))
            self._cache_write(data_name, df)
            return df
        except Exception as e:
            logger.error(f"{data_name} FAILED TO EXTRACT data from html, but successfully get data from website, {e}")
            return None

    def _dismiss_te_popups(self, data_name: str) -> None:
        """Best-effort: close cookie/terms banners or overlays to avoid click intercepts."""
        selectors = [
            (By.XPATH, '//button[contains(@class, "accept")]'),
            (By.XPATH, '//button[contains(., "Accept")]'),
            (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'),  # OneTrust common id
            (By.CSS_SELECTOR, 'button[aria-label="dismiss"], button[aria-label="close"]'),
        ]
        for by, sel in selectors:
            try:
                el = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((by, sel)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                time.sleep(0.15)
                self.driver.execute_script("arguments[0].click();", el)
                time.sleep(0.15)
            except Exception:
                continue

    def _click_5y(self, data_name: str) -> bool:
        """Click the 5Y range button using multiple locators and a retry once."""
        locators = [
            (By.XPATH, '//*[@id="dateSpansDiv"]/a[3]'),
            (By.XPATH, '//div[@id="dateSpansDiv"]//a[contains(., "5y") or contains(., "5Y")]'),
            (By.XPATH, '//a[contains(@href, "5y")]'),
            (By.CSS_SELECTOR, '#dateSpansDiv a:nth-child(3)')
        ]
        for _ in range(2):
            for by, sel in locators:
                try:
                    btn = WebDriverWait(self.driver, TEDownloader.time_wait).until(EC.element_to_be_clickable((by, sel)))
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.1)
                    self.driver.execute_script("arguments[0].click();", btn)
                    time.sleep(TEDownloader.time_pause)
                    return True
                except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException):
                    # Try next locator
                    continue
                except Exception:
                    continue
            # Retry once after dismissing popups again
            self._dismiss_te_popups(data_name)
            time.sleep(0.2)
        return False

    def to_db(self, return_csv: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        # 并发策略：优先使用小规模驱动池，减少频繁创建/销毁开销；每个任务独占一个临时 driver 实例
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return df_dict if return_csv else None

        # 构建驱动池（仅在并发时启用）
        pool: Optional["queue.Queue[webdriver.Chrome]"] = None
        pool_size = 0
        load_dotenv()
        env_te_workers = os.environ.get('TE_WORKERS')
        env_te_pool = os.environ.get('TE_POOL_SIZE')
        resolved_workers = max_workers or (int(env_te_workers) if env_te_workers and env_te_workers.isdigit() else 1)
        if resolved_workers > 1:
            pool_size = max(1, min(int(env_te_pool) if env_te_pool and env_te_pool.isdigit() else resolved_workers, 3))  # 控制池大小，避免过多实例
            pool = queue.Queue(maxsize=pool_size)
            for _ in range(pool_size):
                opts = TEDownloader._build_chrome_options(self._headless)
                drv = webdriver.Chrome(options=opts)
                try:
                    drv.maximize_window()
                except Exception:
                    pass
                try:
                    drv.set_page_load_timeout(25)
                except Exception:
                    pass
                pool.put(drv)

        def run_single(data_name: str) -> Optional[pd.DataFrame]:
            # 单任务可复用主 driver；并发时创建局部 driver
            if (max_workers or 1) > 1:
                assert pool is not None
                drv = pool.get()
                try:
                    original = self.driver
                    self.driver = drv
                    try:
                        return self._get_data_from_trading_economics_month(data_name=data_name)
                    finally:
                        self.driver = original
                finally:
                    pool.put(drv)
            else:
                return self._get_data_from_trading_economics_month(data_name=data_name)

        workers = resolved_workers
        if workers > 1:
            logger.info("TE submitting %d tasks (workers=%d, headless=%s)", len(items), workers, self._headless)
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=workers) as ex:
                fut_map = {ex.submit(run_single, cfg["name"]): tn for tn, cfg in items}
                for fut in as_completed(fut_map):
                    tn = fut_map[fut]
                    try:
                        df = fut.result()
                        if df is None:
                            logger.error("TE FAILED TO EXTRACT %s", tn)
                            continue
                        converter = DatabaseConverter()
                        converter.write_into_db(
                            df=df,
                            data_name=self.json_dict[tn]["name"],
                            start_date=self.start_date,
                            is_time_series=True,
                            is_pct_data=self.json_dict[tn]["needs_pct"]
                        )
                        df_dict[tn] = df
                    except Exception as e:
                        logger.error("TE future for %s raised: %s", tn, e)
        else:
            for tn, cfg in items:
                data_name = cfg["name"]
                df = run_single(data_name)
                if df is None:
                    logger.error(f"FAILED TO EXTRACT {tn}, check PREVIOUS loggings")
                    continue
                converter = DatabaseConverter()
                converter.write_into_db(
                    df=df,
                    data_name=cfg["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=cfg["needs_pct"]
                )
                df_dict[tn] = df

        # 释放驱动池资源
        if pool is not None:
            try:
                while not pool.empty():
                    drv = pool.get_nowait()
                    try:
                        drv.quit()
                    except Exception:
                        pass
            except Exception:
                pass

        if return_csv:
            for name, df in df_dict.items():
                try:
                    data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)
                    os.makedirs(data_folder_path, exist_ok=True)
                    csv_path = os.path.join(data_folder_path, f"{name}.csv")
                    df.to_csv(csv_path, index=True)
                    logging.info(f"{name} saved to {csv_path} Successfully!")
                except Exception as e:
                    logging.error(f"{name} FAILED DOWNLOAD CSV in method 'to_db', since {e}")
                    continue
        return None


class DownloaderFactory:
    '''API/Interface, factory that direct to different data-instance classes'''
    @classmethod
    def _get_api_key(cls, source: str) -> Optional[str]:
        '''获取api key，从env文件获得'''
        load_dotenv()
        api = os.environ.get(source)
        if not api:
            logging.warning("_get_api_key WARNING: API key NOT FOUND in .env file, CONTINUE")
            return ""
        return api

    @classmethod
    def create_downloader(
        cls,
        source: str,
        json_data: Dict[str, Any],   # full json data, not just one item in the dict
        request_year : int,
    ) -> Optional['DataDownloader']:

        api_key = cls._get_api_key(source)
        json_dict_data_index_info = json_data.get(source, None)
        if not isinstance(json_dict_data_index_info, dict):
            logging.error(f"DownloaderFactory: no config found for source '{source}'")
            return None
        # 类型断言，确保后续构造函数类型安全
        cfg = cast(Dict[str, Dict[str, Any]], json_dict_data_index_info)
        downloader_classes = {
            'bea': BEADownloader,
            'yf': YFDownloader,
            'fred': FREDDownloader,
            'bls': BLSDownloader,
            'te': TEDownloader,
            # 'ism': ISMDownloader,
            # 'fw': FedWatchDownloader,
            # 'dfm': DallasFedDownloader,
            # 'nyf': NewYorkFedDownloader,
            # 'cin': InflaNowcastingDownloader,
            # 'em': EminiDownloader,
            # 'fs': ForexSwapDownloader
        }

        if source not in downloader_classes:
            logging.error("INVALID SOURCE in downloader factory :" + source)
            return None

        if source == 'te':
            # 允许通过环境变量控制是否显示浏览器窗口：
            # - TE_HEADLESS=false 则显示窗口；true 则无头
            # - TE_SHOW_BROWSER=true/1 优先强制显示窗口
            # - TE_FORCE_HEADLESS=true/1 优先强制无头
            # 缺省改为 False（显示窗口），便于可视化调试；如需无头，请在环境中设置 TE_HEADLESS=true
            show_browser = os.environ.get('TE_SHOW_BROWSER', '').strip().lower() in ('1', 'true', 'yes')
            force_headless = os.environ.get('TE_FORCE_HEADLESS', '').strip().lower() in ('1', 'true', 'yes')
            headless_env = os.environ.get('TE_HEADLESS', 'false').strip().lower()
            headless = headless_env in ('1', 'true', 'yes')
            if show_browser:
                headless = False
            if force_headless:
                headless = True
            logger.info(
                "TE headless resolved: %s (TE_HEADLESS=%s, TE_SHOW_BROWSER=%s, TE_FORCE_HEADLESS=%s)",
                headless, headless_env, show_browser, force_headless
            )
            return downloader_classes[source](
                json_dict=cfg,
                api_key=api_key,
                request_year=request_year,
                headless=headless
            )
        return downloader_classes[source](
            json_dict=cfg,
            api_key=api_key,
            request_year=request_year
        )