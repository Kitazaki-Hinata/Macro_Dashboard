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
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Tuple
from typing import cast

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
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

        # 1) BEA（索引为 'YYYY' | 'YYYYQn' | 'YYYYMM'）
        try:
            sample = str(df.index[0]) if len(df.index) else ""
            if re.fullmatch(r"\d{4}", sample):
                # 年度：用当年末一天
                df["date"] = [f"{int(y)}-12-31" for y in df.index.astype(str)]
                df = DatabaseConverter._rename_bea_date_col(df)
                return finalize_with_date_first(df.rename_axis(None, axis=1))
            if re.fullmatch(r"\d{4}Q[1-4]", sample):
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
            if "date" in df.columns:
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
                period = df["period"].astype(str)
                # 统一生成 month 为 Series[str]
                if period.str.startswith("M").any():
                    month_series = period.str[1:].astype(int)
                    month_series = month_series.where(month_series != 12, 0) + 1
                    month_series = month_series.astype(str).str.zfill(2)
                elif period.str.startswith("Q").any():
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
                return finalize_with_date_first(df.rename(columns={df.columns[1]: data_name}) if len(df.columns) > 1 else df)
            else:
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

        # 尝试寻找database中是否存在ts表，如果存在，则跳过create
        cursor.execute("SELECT name FROM sqlite_master WHERE type= 'table' AND name  = 'Time_Series'")
        table_exists = cursor.fetchone() is not None  # if table exists, return True

        # 如果没有ts表，则尝试创建一个
        try:
            if not table_exists:
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
                return cursor
            else:
                logging.info("Time_Series table already exists, continue")
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
                    dates_to_add: List[date] = []
                    while current_date > max_date:
                        dates_to_add.append(current_date)
                        current_date -= timedelta(days=1)
                    # 插入数据
                    for d in dates_to_add:
                        cursor.execute("INSERT INTO Time_Series (date) VALUES (?)", (d.strftime('%Y-%m-%d'),))
                    self.conn.commit()
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
    ) -> None:
        '''params df: df that used to write into db
        params data_name: used in db columns and errors
        params start_date, start date of  all data, used when create db sheet
        params is_time_series: judge whether it is time series data, incl. BEA, BLS, YF, TE, FRED
        params is_pct_data: input json data, bool value, "needs_pct"
        '''
        # 串行化整个写入过程，防止 Time_Series 全表替换时的竞态
        with DB_WRITE_LOCK:
            self._create_ts_sheet(start_date = start_date)
            cursor = self.cursor
            try:
                if df.empty:
                    logging.error(f"{data_name} is empty, FAILED INSERT, locate in write_into_db")
                else:
                    if is_time_series:  # check whether Time_Series table exists
                        df_after_modify_time: pd.DataFrame = DatabaseConverter._format_converter(df, data_name, is_pct_data)
                        if df_after_modify_time.empty or 'date' not in df_after_modify_time.columns:
                            logging.error(f"{data_name} reformat produced empty/invalid dataframe, skip writing")
                            return
                        # 标准化和去重
                        df_after_modify_time = df_after_modify_time.copy()
                        df_after_modify_time['date'] = pd.to_datetime(df_after_modify_time['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                        df_after_modify_time = df_after_modify_time.dropna(subset=['date']).drop_duplicates(subset=['date'], keep='last')
                        try:
                            cursor.execute(f"ALTER TABLE Time_Series ADD COLUMN {data_name} DOUBLE")
                            self.conn.commit()
                        except:
                            logging.warning(f"{data_name} col name already exists in Time_Series, continue")

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

                        result_db.to_sql(
                            name="Time_Series",  # 同一张表或新表
                            con=self.conn,
                            if_exists="replace",
                            index=False
                        )

                        self.conn.commit()
                        return
                    else:
                        # 其他数据则直接生成新sheet存入database当中
                        df.to_sql(
                            name=data_name,
                            con=self.conn,
                            if_exists='replace',  # if sheet exist, then replace
                            index=False
                        )
                        self.conn.commit()
                        self.conn.close()
                        return

            except Exception as e:
                logging.error(f"FAILED to write into database, in method write_into_db, since {e}")
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
                try:
                    bea_tbl = beaapi.get_data(
                        self.api_key,
                        datasetname=table_config["category"],
                        TableName=table_config["code"],
                        Frequency=table_config["freq"],
                        Year=self.time_range
                    )
                except beaapi.beaapi_error.BEAAPIResponseError:
                    bea_tbl = beaapi.get_data(
                        self.api_key,
                        datasetname=table_config["category"],
                        TableName=table_config["code"],
                        Frequency=table_config["freq"],
                        Year=self.time_range_lag
                    )
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
                logging.info(f"BEA_{table_name} Successfully extracted!")

                if df_modified.empty:
                    logging.error(f"{table_name} is empty, FAILED INSERT, locate in to_db")
                    return table_name, None
                converter = DatabaseConverter()
                converter.write_into_db(
                    df = df_modified,
                    data_name=table_config["name"],
                    start_date  = str(date(self.request_year, 1, 1)),
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"]
                )
                return table_name, df_modified
            except Exception as e:
                logging.error(f"{table_name} FAILED DOWNLOAD/REFORMAT in BEA worker: {e}")
                return table_name, None

        workers  = max_workers or min(8, (os.cpu_count() or 4) * 2)    # workers是int，确认进程数量
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

    def to_db(self, return_df: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return df_dict if return_df else None

        def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
            try:
                index = table_config["code"]
                data = pd.DataFrame(
                    yf.download(index, start=self.start_date, end=self.end_date, interval="1d")
                )
                try:
                    data.columns = data.columns.droplevel(1)
                except Exception:
                    pass
                if return_df:
                    return table_name, data
                else:
                    converter = DatabaseConverter()
                    converter.write_into_db(
                        df=data,
                        data_name=table_config["name"],
                        start_date=self.start_date,
                        is_time_series=True,
                        is_pct_data=table_config["needs_pct"]
                    )
                    return table_name, None
            except Exception as e:
                logging.error(f"to_db, {table_name} FAILED EXTRACT DATA from Yfinance, {e}")
                return table_name, None

        workers = max_workers or min(12, (os.cpu_count() or 4) * 2)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}
            for fut in as_completed(future_map):
                tn = future_map[fut]
                try:
                    name, df = fut.result()
                    if return_df and df is not None:
                        df_dict[name] = df
                except Exception as e:
                    logging.error(f"YF future for {tn} raised: {e}")

        return df_dict if return_df else None

    def to_csv(self) -> None:
        try:
            df_dict: Dict[str, pd.DataFrame] = self.to_db(return_df=True) or {}
        except:
            logging.error("to_csv, DF_DICT requires DICT but get NONE, probably failed to download data in to_db format")
            return None

        for name, df in df_dict.items():
            try:
                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)  # 因为csv文件夹地址一样所以统一使用BEA类里面定义好的地址
                os.makedirs(data_folder_path, exist_ok= True)
                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                df.to_csv(csv_path, index=True)
                logging.info(f"{name} saved to {csv_path} Successfully!")
            except Exception as e:
                logging.error(f"{ name} FAILED DOWNLOAD CSV in method 'to_csv', since {e}")
                continue


class FREDDownloader(DataDownloader):
    url : str = r"https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year : int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
        self.start_date : str  = str(request_year)+"-01-01"
        self.end_date : str = str(date.today())

    def to_db(self, return_df: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return df_dict if return_df else None

        def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
            try:
                params = {
                    "series_id": table_config["code"],
                    "api_key": self.api_key,
                    "observation_start": self.start_date,
                    "observation_end": self.end_date,
                    "file_type": "json"
                }
                resp = requests.get(FREDDownloader.url, params=params)
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

                if return_df:
                    logging.info(f"{table_name} Successfully extracted!")
                    return table_name, df
                else:
                    converter = DatabaseConverter()
                    converter.write_into_db(
                        df=df,
                        data_name=table_config["name"],
                        start_date=self.start_date,
                        is_time_series=True,
                        is_pct_data=table_config["needs_pct"]
                    )
                    logging.info(f"{table_name} Successfully extracted!")
                    return table_name, None
            except Exception as e:
                logging.error(f"{table_name} FAILED EXTRACT DATA from FRED: {e}")
                return table_name, None

        workers = max_workers or min(12, (os.cpu_count() or 4) * 2)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}
            for fut in as_completed(future_map):
                tn = future_map[fut]
                try:
                    name, df = fut.result()
                    if return_df and df is not None:
                        df_dict[name] = df
                except Exception as e:
                    logging.error(f"FRED future for {tn} raised: {e}")

        return df_dict if return_df else None

    def to_csv(self) -> None:
        try:
            df_dict: Dict[str, pd.DataFrame] = self.to_db(return_df=True) or {}
        except:
            logging.error("to_csv, DF_DICT requires DICT but get NONE, probably failed to download data in to_db format")
            return None

        for name, df in df_dict.items():
            try:
                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)  # 因为csv文件夹地址一样所以统一使用BEA类里面定义好的地址
                os.makedirs(data_folder_path, exist_ok= True)
                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                df.to_csv(csv_path, index=True)
                logging.info(f"{name} saved to {csv_path} Successfully!")
            except Exception as e:
                logging.error(f"{ name} FAILED DOWNLOAD CSV in method 'to_csv', since {e}")
                continue


class BLSDownloader(DataDownloader):
    url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers: Tuple[str, str] = ('Content-type', 'application/json')

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key : str, request_year : int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
        self.start_year: int  = request_year
        self.start_date : str  = str(request_year)+"-01-01"

    def to_db(self, return_df : bool = False, debug : bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
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
                return df_dict if return_df else None

            def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
                try:
                    params = json.dumps(
                        {
                            "seriesid": [table_config["code"]],
                            "startyear": self.start_year,
                            "endyear": date.today().year,
                            "registrationKey": self.api_key
                            }
                        )
                    context = requests.post(
                        BLSDownloader.url,
                        data=params,
                        headers=dict([BLSDownloader.headers])
                    )
                    json_data = json.loads(context.text)
                    logging.info(f"{table_name} Successfully download data")
                except Exception as e:
                    logging.error(f"{table_name} FAILED EXTRACT DATA from BLSProbably due to API extraction problems, {e}")
                    return table_name, None

                try:
                    df = pd.DataFrame(json_data["Results"]["series"][0]["data"]).drop(
                        columns=["periodName", "latest", "footnotes"])
                except Exception:
                    try:
                        df = pd.DataFrame(json_data)
                        logging.warning(f"{table_name} FAILED REFORMAT: DROP USELESS COLUMNS, continue")
                    except Exception as e:
                        logging.error(f"{table_name} FAILED REFORMAT data from BLS, errors in df managing, {e}")
                        return table_name, None

                if table_config["needs_pct"] is True:
                    try:
                        df["value"] = pd.to_numeric(df["value"])
                        df["MoM_growth"] = ((df["value"] - df["value"].shift(1)) / (df["value"].shift(1)) * -1).shift(-1)
                        df = df.drop(df.columns[-2], axis=1)
                    except Exception as e:
                        logging.error(f"{table_name} FAILED REFORMAT PERCENTAGE, probably due to df error, {e}")
                        return table_name, None

                if return_df:
                    logging.info(f"{table_name} Successfully extracted!")
                    return table_name, df
                else:
                    converter = DatabaseConverter()
                    converter.write_into_db(
                        df=df,
                        data_name=table_config["name"],
                        start_date=self.start_date,
                        is_time_series=True,
                        is_pct_data=table_config["needs_pct"]
                    )
                    logging.info(f"{table_name} Successfully extracted!")
                    return table_name, None

            workers = max_workers or min(8, (os.cpu_count() or 4) * 2)
            with ThreadPoolExecutor(max_workers=workers) as ex:
                future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}
                for fut in as_completed(future_map):
                    tn = future_map[fut]
                    try:
                        name, df = fut.result()
                        if return_df and df is not None:
                            df_dict[name] = df
                    except Exception as e:
                        logging.error(f"BLS future for {tn} raised: {e}")

        if return_df is True:
            return df_dict
        else:
            return None

    def to_csv(self) -> None:
        try:
            df_dict: Dict[str, pd.DataFrame] = self.to_db(return_df=True) or {}
        except:
            logging.error("to_csv, DF_DICT requires DICT but get NONE, probably failed to download data in to_db format")
            return None

        for name, df in df_dict.items():
            try:
                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)  # 因为csv文件夹地址一样所以统一使用BEA类里面定义好的地址
                os.makedirs(data_folder_path, exist_ok=True)
                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                df.to_csv(csv_path, index=True)
                logging.info(f"{name} saved to {csv_path} Successfully!")
            except Exception as e:
                logging.error(f"{name} FAILED DOWNLOAD CSV in method 'to_csv', since {e}")
                continue


class TEDownloader(DataDownloader):
    url : str = "https://tradingeconomics.com/united-states/"
    time_pause : float = random.uniform(1, 1.3)  # wait, prevent be identified as a bot
    time_wait : int = 10  # wait for a response

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key : str, request_year : int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.start_year: int  = request_year
        self.start_date: str = str(request_year) + "-01-01"
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)

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
        self.driver.get(url)
        time.sleep(TEDownloader.time_pause)

        # consent button click
        try:
            cookie_consent_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[1]/p'))
            )
            cookie_consent_button.click()
            # self.driver.execute_script("arguments[0].click();", cookie_consent_button)
            time.sleep(TEDownloader.time_pause)
        except:
            logging.warning(f"{data_name} FAILED TO CLICK consent button, continue")
            pass

        # click "5y" button
        try:
            five_year_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dateSpansDiv"]/a[3]'))
            )
            self.driver.execute_script("arguments[0].click();", five_year_button)
            time.sleep(TEDownloader.time_pause)
        except Exception as e:
            logging.error(f"{data_name} FAILED TO CLICK 5y button, {e}")
            return None

        # click bar chart
        try:
            chart_type_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="chart"]/div/div/div[1]/div/div[3]/div/button'))
            )
            self.driver.execute_script("arguments[0].click();", chart_type_button)
            time.sleep(TEDownloader.time_pause)
            try:
                chart_button = WebDriverWait(self.driver, TEDownloader.time_wait).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="chart"]/div/div/div[1]/div/div[3]/div/div/div[1]/button'))
                )
                self.driver.execute_script("arguments[0].click();", chart_button)
                time.sleep(TEDownloader.time_wait)
            except Exception as e:
                logging.error(f"{data_name} FAILED TO CLICK 'bar chart type' button, {e}")
                return None
        except Exception as e:
            logging.error(f"{data_name} FAILED TO CLICK 'chart type' button, {e}")
            return None

        # extract table data
        try:
            original_html = self.driver.page_source
            soup = BeautifulSoup(original_html, "lxml")
            row = soup.find("tr", class_="datatable-row")
            if isinstance(row, Tag):
                tds = row.find_all("td")
                if len(tds) >= 2:
                    current_num = float(tds[1].text.strip())    # list num，列表中的current数字
                    previous_num = float(tds[2].text.strip())    # list num，上一期数据
                    current_data_date = str(tds[4].text.replace(" ", "_"))  # 最新数据的日期
                else:
                    raise Exception(f"{data_name}, tds tag's length haven't reach 2, during html convert stage")
            else:
                raise Exception(f"{data_name}, HAVEN'T FOUND ROWS during html convert stage")

            # extract bar height value for actual data
            rects = soup.find_all("rect", class_="highcharts-point")
            # extract bar height value for actual data
            heights: List[float] = []
            for rect in rects:
                if isinstance(rect, Tag):
                    h = rect.get("height")
                    if h is not None:
                        try:
                            heights.append(float(str(h)))
                        except Exception:
                            continue

            # 利用两个数据计算数据与bar高度的线性关系，y是结果，x是高度
            gradient, intercept = self._calc_function(heights[-1], heights[-2], current_num, previous_num,)
            data_list = []   # store final data value
            for num in heights:
                final_data = intercept + gradient * num
                data_list.append(final_data)

            # construct a DATE mapping
            month_map = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
            }
            month_abbr, year_str = current_data_date.split("_")
            month_int: int = month_map[month_abbr]
            year_int: int = int(year_str)
            end_date = datetime(year_int, month_int, 1)
            months_list = [
                (end_date - relativedelta(months=i)).strftime("%b_%Y")
                for i in reversed(range(61))  # 包含Mar_2020 ~ Mar_2025
            ]
            df = pd.DataFrame(data={"date": months_list, "value": data_list})
            return df
        except Exception as e:
            logging.error(f"{data_name} FAILED TO EXTRACT data from html, but successfully get data from website, {e}")
            return None

    def to_db(self, return_df: bool = False, max_workers: Optional[int] = None) -> Optional[Dict[str, pd.DataFrame]]:
        # 说明: 由于 Selenium WebDriver 复用同一 self.driver，不适合多线程并行。
        # 如需并行，需要为每个任务创建独立 driver，成本较高，这里保持顺序执行。
        df_dict: Dict[str, pd.DataFrame] = {}
        for table_name, table_config in self.json_dict.items():
            data_name = table_config["name"]
            df = self._get_data_from_trading_economics_month(data_name = data_name)
            if df is None:
                logging.error(f"FAILED TO EXTRACT {table_name}, check PREVIOUS loggings")
                continue
            if return_df is True:
                df_dict[table_name] = df
                logging.info(f"{data_name} SUCCESSFULLY EXTRACT data from website TE")
                continue
            elif return_df is False:
                converter = DatabaseConverter()
                converter.write_into_db(
                    df=df,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"]
                )
                continue

        if return_df is True:
            return df_dict
        else:
            return None

    def to_csv(self) -> None:
        try:
            df_dict: Dict[str, pd.DataFrame] = self.to_db(return_df=True) or {}
        except:
            logging.error("to_csv, DF_DICT requires DICT but get NONE, probably failed to download data in to_db format")
            return None

        for name, df in df_dict.items():
            try:
                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)  # 因为csv文件夹地址一样所以统一使用BEA类里面定义好的地址
                os.makedirs(data_folder_path, exist_ok=True)
                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                df.to_csv(csv_path, index=True)
                logging.info(f"{name} saved to {csv_path} Successfully!")
            except Exception as e:
                logging.error(f"{name} FAILED DOWNLOAD CSV in method 'to_csv', since {e}")
                continue


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

        return downloader_classes[source](
            json_dict=cfg,
            api_key=api_key,
            request_year=request_year
        )

