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
import pandas as pd
import yfinance as yf
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from selenium import webdriver
from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class DatabaseConverter():
    _MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    end_date: date = date.today()

    def __init__(self, db_file: str = 'data.db'):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)   # 参数是数据库的本地地址，后续可以只用一次cursor
        self.cursor = self.conn.cursor()

    @staticmethod
    def _convert_month_str_to_num(month_str):
        return DatabaseConverter._MONTH_MAP.get(month_str.casefold(), None)

    @staticmethod
    def _rename_bea_date_col(df: pd.DataFrame)-> pd.DataFrame:
        '''modify time index, unify all time index in different dataframe(time series dataframe'''
        try:
            # df.drop("TimePeriod", axis=1, inplace=True)  # remove original date index
            date_col = df.pop("date")  # get date col
            df.insert(0, "date", date_col)  # insert "date col" into first col
            return df
        except Exception as e:
            logging.error(f"{e}, FAILED to write into database")
            df = pd.DataFrame()
            return df

    @staticmethod
    def _format_converter(df: pd.DataFrame, data_name : str, is_pct_data : bool)-> pd.DataFrame:
        try:
            # 将index统一转换为2020-01-01
            match df.index[1]:  # BEA
                case bea_a if re.fullmatch(r"[0-9]{4}", bea_a):
                    # 匹配： BEA_a 2020
                    df.index = df.index + "-12-31"
                    df["date"] = pd.to_datetime(df.index, format="%Y-%m-%d")
                    df = DatabaseConverter._rename_bea_date_col(df)
                    return df

                case bea_q if re.fullmatch(r"[0-9]{4}Q[0-9]{1}", bea_q):
                    # 匹配：BEA_q 2020Q1
                    def convert_q_format(date_str):
                        # 匹配：BEA_q 2020Q1
                        year, quarter = date_str.split("Q")
                        quarter = int(quarter)
                        year = int(year)

                        month = quarter * 3 + 1
                        if month > 12:
                            year += 1
                            month = 1
                        return f"{year}-{month:02d}-01"

                    df["date"] = list(map(convert_q_format, df.index))
                    df = DatabaseConverter._rename_bea_date_col(df)
                    return df

                case bea_m if re.fullmatch(r"[0-9]{4}M[0-9]{2}", bea_m):
                    # 匹配：BEA_m 2020M01
                    def convert_m_format(date_str):
                        # 转换月份格式，如果要是2020M12 -> 2021-01-01
                        year, month = date_str.split("M")
                        month = int(month)
                        year = int(year)

                        if month == 12:
                            new_year = year + 1
                            new_month = 1
                        else:
                            new_year = year
                            new_month = month + 1

                        return f"{new_year}-{new_month:02d}-01"

                    df["date"] = list(map(convert_m_format, df.index))
                    df = DatabaseConverter._rename_bea_date_col(df)
                    return df

                case _:
                    logging.warning("Haven't MATCH DATA in method _format_converter, continue")
                    pass
        except Exception as e:
            logging.warning(f"{e}, not match BEA, continue")
            pass

        try:   # match yfinance
            if df.columns.tolist() == ["Close", "High", "Low", "Open", "Volume"]:
                df["date"] = pd.to_datetime(
                    pd.Series(df.index).astype(str).str.split().str[0],
                    errors="coerce"
                ).dt.strftime("%Y-%m-%d")
                df = df.reset_index(drop=True)
                df.drop(columns=["High", "Low", "Open", "Volume", "Date"], inplace=True)  # implace, 直接替换原来的df
                date_col = df.pop("date")
                df.insert(0, "date", date_col)  # 这里将date放到第一列
                if len(df.columns) > 1:  # rename col with data name
                    second_col = df.columns[1]
                    df = df.rename(columns={second_col: f"{data_name}"})
                else:
                    logging.warning(f"FAILED TO RENAME COLUMN NAME {data_name}, in function write_to_db, continue")
                return df

        except Exception as e:
            logging.warning(f"{e}, not match YFinance, continue")
            pass

        try:
            match df["date"][1]:  # Fred data
                case fred if re.match("[0-9]{4}-[0-9]+-[0-9]+", fred):
                    # 匹配：FRED 2020-01-01
                    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")

                    # 判断列数是否大于1，且区分是不是百分比数据
                    if len(df.columns) > 1 and is_pct_data == False:  # rename col with data name
                        second_col = df.columns[1]
                        df = df.rename(columns={second_col: f"{data_name}"})
                    elif len(df.columns) > 1 and is_pct_data == True:  # rename col, pct data
                        second_col = df.columns[1]
                        df = df.rename(columns={second_col: f"{data_name}"})
                    else:
                        logging.warning(f"FAILED TO RENAME COLUMN NAME {data_name}, in function write_to_db, continue")
                    return df

                case _:
                    logging.warning("Haven't MATCH DATA in method _format_converter, continue")
                    pass
        except Exception as e:
            logging.warning(f"{e}, not match FRED, continue")
            pass

            ################################ 没法下载BLS数据，所以暂时没法match这个数据
            ###################  is_pct_data 区分一个True

        try:
            match df["date"][1]:  # Trading Economics data
                case trading_eco if re.match("[A-Z][a-z]+_[0-9]{4}", trading_eco):
                    df.rename(columns = {"date": "Date"}, inplace=True )
                    df.rename(columns = {"value": f"{data_name}"}, inplace=True)
                    split_data = df["Date"].str.split("_", expand=True).replace()
                    month_str : pd.Series = split_data[0]
                    year : pd.Series = split_data[1].astype(int)  # 转换为整数

                    dec_mask = (month_str == "Dec")  # 布尔掩码
                    year = year.where(~dec_mask, year + 1)  # Dec 年份 +1
                    month = month_str.apply(DatabaseConverter._convert_month_str_to_num)
                    month = month.where(~dec_mask, 1)
                    df["date"] = year.astype(str) + "-" + month.astype(str).str.zfill(2) + "-01"

                    df.drop(columns=["Date"], inplace=True)
                    date_col = df.pop("date")
                    df.insert(0, "date", date_col)
                    return df

                case _:
                    pass
        except Exception as e:
            logging.warning(f"{e}, not match TE, continue")
            pass

    def _create_ts_sheet(self, start_date : str):
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
                max_date = datetime.strptime(max_date_str, '%Y-%m-%d').date()

                # 计算需要添加的日期
                current_date = datetime.now().date()
                if current_date > max_date:
                    dates_to_add = []
                    while current_date > max_date:
                        dates_to_add.append(current_date)
                        current_date -= timedelta(days=1)
                    # 插入数据
                    for date in dates_to_add:
                        cursor.execute("INSERT INTO Time_Series (date) VALUES (?)", (date.strftime('%Y-%m-%d'),))
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
        self._create_ts_sheet(start_date = start_date)
        cursor = self.cursor
        try:
            if df.empty:
                logging.error(f"{data_name} is empty, FAILED INSERT, locate in write_into_db")
            else:
                if is_time_series:  # check whether Time_Series table exists
                    df_after_modify_time : pd.DataFrame = DatabaseConverter._format_converter(df, data_name, is_pct_data)
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
    def to_db(self, return_df = False):
        pass

    @abstractmethod
    def to_csv(self) -> None:
        pass


class BEADownloader(DataDownloader):
    current_year : int = date.today().year
    download_py_file_path : str = os.path.dirname(os.path.abspath(__file__))
    csv_data_folder : str = os.path.join(download_py_file_path, "csv")

    def __init__(self, json_dict: dict, api_key: str, request_year : int):
        self.json_dict : dict = json_dict
        self.api_key : str = api_key
        self.request_year : int = request_year
        self.time_range : str= ",".join(map(str, range(request_year, BEADownloader.current_year + 1)))
        self.time_range_lag : str = self.time_range[:-5]  # 去除最后5个字符，即去除最后一年

    def to_db(self, return_df = False):
        df_dict : dict = {}    # create list for future df storage and output  (return df_list)
        total_items = len(self.json_dict)
        for idx, (table_name, table_config) in enumerate(self.json_dict.items(), 1):
            try:
                bea_tbl = beaapi.get_data(
                    self.api_key,
                    datasetname=table_config["category"],
                    TableName=table_config["code"],
                    Frequency=table_config["freq"],
                    Year=self.time_range
                )
            except beaapi.beaapi_error.BEAAPIResponseError:
                try:  # 如果在本年1-3月，未公布本年的数据，则跳转到这里，下载上一年到目标年份的数据
                    bea_tbl = beaapi.get_data(
                        self.api_key,
                        datasetname=table_config["category"],
                        TableName=table_config["code"],
                        Frequency=table_config["freq"],
                        Year=self.time_range_lag
                    )
                except Exception as e:
                    logging.error(f"{table_name} FAILED DOWNLOAD from API, since {e}")
                    continue
            except Exception as e:
                logging.error(f"{table_name} FAILED DOWNLOAD from API, since {e}")
                continue

            try:
                df : pd.DataFrame = pd.DataFrame(bea_tbl)
                df_filtered : pd.DataFrame = df[df["LineDescription"].isin([df["LineDescription"][1], ""])]   # 提取首列数据/isin后面使用list和""的原因是不允许输入str
                df_modified : pd.DataFrame= df_filtered.pivot(index="TimePeriod", columns="LineDescription", values="DataValue") # 重新排序
                df_modified.columns = [f"{table_config['name']}"]   # rename
                df_modified.index.name = "TimePeriod"
                logging.info(f"BEA_{table_name} Successfully extracted!")
                if return_df is True and isinstance(df_modified, pd.DataFrame):  # used for to_csv method
                    df_dict[table_name] = df_modified
                    if idx == total_items:
                        break
                    continue
                elif return_df is False:
                    if df_modified.empty:
                        logging.error(f"{table_name} is empty, FAILED INSERT, locate in to_db")
                        continue
                    converter = DatabaseConverter()
                    converter.write_into_db(
                        df = df_modified,
                        data_name=table_config["name"],
                        start_date  = str(date(self.request_year, 1, 1)),
                        is_time_series=True,
                        is_pct_data=table_config["needs_pct"]
                    )
                    continue
            except Exception as e:
                logging.error(f"{table_name} FAILED REFORMAT to dataframe in method 'to_db', since {e}")
                continue
        if return_df is True:
            return df_dict
        else:
            return None

    def to_csv(self) -> None:
        try:
            df_dict : dict = self.to_db(return_df=True)
        except:
            logging.error("to_csv, DF_DICT requires DICT but get NONE, probably failed to download data in to_db format")
            return None

        for name, df in df_dict.items():
            try:
                data_folder_path = os.path.join(BEADownloader.csv_data_folder, name)
                os.makedirs(data_folder_path, exist_ok= True)
                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                df.to_csv(csv_path, index=True)
                logging.info(f"{name} saved to {csv_path} Successfully!")
            except Exception as e:
                logging.error(f"{ name} FAILED DOWNLOAD CSV in method 'to_csv', since {e}")
                continue


class YFDownloader(DataDownloader):
    def __init__(self, json_dict: dict, api_key, request_year : int):
        self.json_dict : dict = json_dict
        self.start_date : str  = str(request_year)+"-01-01"
        self.end_date : str = str(date.today())

    def to_db(self, return_df = False):
        '''NOTE : data is pd.dataframe'''
        df_dict : dict = {}  # create list for future df storage and output  (return df_list)
        for table_name, table_config in self.json_dict.items():
            try:
                index = table_config["code"]
                data : pd.DataFrame = yf.download(index, start=self.start_date, end=self.end_date, interval="1d")
                data.columns = data.columns.droplevel(1)
                if return_df is True and isinstance(data, pd.DataFrame):  # used for to_csv method
                    df_dict[table_name] = data
                    continue
                elif return_df is False:
                    converter = DatabaseConverter()
                    converter.write_into_db(
                        df=data,
                        data_name=table_config["name"],
                        start_date=self.start_date,
                        is_time_series=True,
                        is_pct_data=table_config["needs_pct"]
                    )
                    continue
            except Exception as e:
                logging.error(f"to_db, {table_name} FAILED EXTRACT DATA from Yfinance, {e}")
                continue
        if return_df is True:
            return df_dict
        else:
            return None

    def to_csv(self) -> None:
        try:
            df_dict : dict = self.to_db(return_df=True)
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

    def __init__(self, json_dict: dict, api_key, request_year : int):
        self.json_dict : dict = json_dict
        self.api_key : str = api_key
        self.start_date : str  = str(request_year)+"-01-01"
        self.end_date : str = str(date.today())

    def to_db(self, return_df = False):
        df_dict : dict = {}
        for table_name, table_config in self.json_dict.items():
            try:
                params = {
                    "series_id": table_config["code"],
                    "api_key": self.api_key,
                    "observation_start": self.start_date,
                    "observation_end": self.end_date,
                    "file_type": "json"
                }
                data  = requests.get(FREDDownloader.url, params=params).json()
                df = pd.DataFrame(data["observations"])
                try:
                    df : pd.DataFrame = df.iloc[:, -2:]
                except:
                    logging.warning(f"{table_name} HAVEN'T REMOVE 2 realtime columns, but continue to operate")
                    pass

                if table_config["needs_pct"] is True:  # identify params in json and reformat based on bool value
                    df["value"] = pd.to_numeric(df["value"])
                    df["MoM_growth"] = df["value"].pct_change().dropna()
                    df = df.drop(df.columns[-2], axis=1)
                if table_config["needs_cleaning"] is True:
                    df["value"] = df["value"].replace(".", np.nan)
                    df["value"] = np.where(
                        df["value"].isna(),
                        df['value'].shift(1),
                        df['value']
                    )
                    df["value"] = df["value"].ffill().dropna()

                if return_df is True and isinstance(df, pd.DataFrame):
                    df_dict[table_name] = df
                    logging.info(f"{table_name} Successfully extracted!")
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
                    logging.info(f"{table_name} Successfully extracted!")
                    continue
            except Exception as e:
                logging.error(f"{table_name} FAILED EXTRACT DATA from FRED"
                              f"Probably due to extraction failure or df reformat failure.")
                continue

        if return_df is True:
            return df_dict
        else:
            return None

    def to_csv(self):
        try:
            df_dict: dict = self.to_db(return_df=True)
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
    headers: tuple = ('Content-type', 'application/json')

    def __init__(self, json_dict: dict, api_key : str, request_year : int):
        self.json_dict : dict = json_dict
        self.api_key : str = api_key
        self.start_year : int  = request_year
        self.start_date : str  = str(request_year)+"-01-01"

    def to_db(self, return_df = False):
        df_dict : dict = {}
        for table_name, table_config in self.json_dict.items():
            try:
                params = json.dumps(
                    {
                        "seriesid": table_config["code"],
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
                logging.error(f"{table_name} FAILED EXTRACT DATA from BLS"
                              f"Probably due to API extraction problems, {e}")
                continue

            # reformat data
            try:
                df = pd.DataFrame(json_data["Results"]["series"][0]["data"]).drop(
                    columns=["periodName", "latest", "footnotes"])
            except:
                try:
                    df = pd.DataFrame(json_data)
                    logging.warning(f"{table_name} FAILED REFORMAT: DROP USELESS COLUMNS, continue")
                except Exception as e:
                    logging.error(f"{table_name} FAILED REFORMAT data from BLS, errors in df managing, {e}")
                    continue

            if table_config["needs_pct"] is True:
                try:
                    df["value"] = pd.to_numeric(df["value"])
                    df["MoM_growth"] = ((df["value"] - df["value"].shift(1)) / (df["value"].shift(1)) * -1).shift(-1)
                    df = df.drop(df.columns[-2], axis=1)
                except Exception as e:
                    logging.error(f"{table_name} FAILED REFORMAT PERCENTAGE, probably due to df error, {e}")
                    continue

            if return_df is True and isinstance(df, pd.DataFrame):
                df_dict[table_name] = df
                logging.info(f"{table_name} Successfully extracted!")
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
                logging.info(f"{table_name} Successfully extracted!")
                continue

        if return_df is True:
            return df_dict
        else:
            return None

    def to_csv(self) -> None:
        try:
            df_dict: dict = self.to_db(return_df=True)
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

    def __init__(self, json_dict: dict, api_key : str, request_year : int):
        self.json_dict : dict = json_dict
        self.start_year : int  = request_year
        self.start_date: str = str(request_year) + "-01-01"
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)

    def _calc_function(self, x1: float, x2:float, y1:float, y2:float):
        """解二元一次方程，用于计算数据 used for data calculation"""
        gradient = np.round((y1 - y2)/(x1-x2), 3)
        intercept = np.round((y1 - gradient*x1), 3)
        return gradient, intercept

    def _get_data_from_trading_economics_month(self, data_name: str):
        """提取月度数据的代码，季度数据需要单独写
        主要流程：访问页面，点击5y按钮，点击bar按钮，提取table数字，提取bar长度，反向计算数据"""

        data_name: str = data_name
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
            if row:
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
            heights = [float(rect.get("height")) for rect in rects if rect.get("height") is not None]  # value of height

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
            month_abbr, year = current_data_date.split("_")
            month : int = month_map[month_abbr]
            year : int = int(year)
            end_date = datetime(year, month, 1)
            months_list = [
                (end_date - relativedelta(months=i)).strftime("%b_%Y")
                for i in reversed(range(61))  # 包含Mar_2020 ~ Mar_2025
            ]
            df = pd.DataFrame(data={"date": months_list, "value": data_list})
            return df
        except Exception as e:
            logging.error(f"{data_name} FAILED TO EXTRACT data from html, but successfully get data from website, {e}")
            return None

    def to_db(self, return_df = False):
        df_dict: dict = {}
        for table_name, table_config in self.json_dict.items():
            data_name = table_config["name"]
            df = self._get_data_from_trading_economics_month(data_name = data_name)
            if df is None:
                logging.error(f"FAILED TO EXTRACT {table_name}, check PREVIOUS loggings")
                continue
            if return_df is True and isinstance(df, pd.DataFrame):
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
            df_dict: dict = self.to_db(return_df=True)
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
    def _get_api_key(cls, source: str) -> str or None:
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
            json_data: dict,   # full json data, not just one item in the dict
            request_year : int,
    ) -> 'DataDownloader' or None:

        api_key = cls._get_api_key(source)
        json_dict_data_index_info = json_data.get(source, None)
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
            json_dict=json_dict_data_index_info,
            api_key=api_key,
            request_year=request_year
        )

