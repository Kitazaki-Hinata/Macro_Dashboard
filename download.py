import os
import logging
import beaapi
import pandas as pd
import yfinance as yf
from datetime import  date
from dotenv import load_dotenv
from abc import ABC, abstractmethod


def write_into_db(df):
    '''input df into database'''
    try:
        pass
    except Exception as e:
        logging.error(f"{e}, FAILED to write into database")
        return None

class DataDownloader(ABC):
    @abstractmethod
    def to_db(self):
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
                logging.info(f"BEA_{table_name} Successfully extracted!")
                if return_df is True and isinstance(df_modified, pd.DataFrame):  # used for to_csv method
                    df_dict[table_name] = df_modified
                    if idx == total_items:
                        break
                    continue
                elif return_df is False:
                    write_into_db(df_modified)
                    continue
            except Exception as e:
                logging.error(f"{table_name} FAILED REFORMAT to dataframe in method 'to_db', since {e}")
                continue
        if return_df is True:
            return df_dict
        else:
            return  None

    def to_csv(self) -> None:
        df_dict : dict = self.to_db(return_df=True)
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
        df_dict : dict = {}  # create list for future df storage and output  (return df_list)
        for table_name, table_config in self.json_dict.items():
            try:
                index = table_config["code"]
                data = yf.download(index, start=self.start_date, end=self.end_date, interval="1d")
                data.columns = data.columns.droplevel(1)
                if return_df is True and isinstance(data, pd.DataFrame):  # used for to_csv method
                    df_dict[table_name] = data
                    continue
                elif return_df is False:
                    write_into_db(data)
                    continue
            except Exception as e:
                logging.error(f"to_db, {table_name} FAILED EXTRACT DATA from Yfinance")
                continue
        if return_df is True:
            return df_dict
        else:
            return None


    def to_csv(self) -> None:
        df_dict : dict = self.to_db(return_df=True)
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
            # 'fred': FREDDownloader,
            # 'bls': BLSDownloader,
            # 'te': TEDownloader,
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

