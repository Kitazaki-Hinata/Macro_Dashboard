"""Yahoo Finance downloader implementation."""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false

from __future__ import annotations

import logging
import os
from datetime import date
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv

from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
    yf_download_with_retry,
)

logger = logging.getLogger(__name__)


class YFDownloader(DataDownloader):
    """Yahoo Finance 下载器。"""

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key: Optional[str], request_year: int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.start_date: str = f"{request_year}-01-01"
        self.end_date: str = str(date.today())

    def to_db(
        self,
        return_csv: bool = False,
        max_workers: Optional[int] = None,
        cancel_token: Optional[CancellationToken] = None,
    ) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return df_dict if return_csv else None

        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        def worker(table_name: str, table_config: Dict[str, Any]) -> Tuple[str, Optional[pd.DataFrame]]:
            _check_cancel()
            try:
                index = table_config["code"]
                logger.info(
                    "YF start: table=%s symbol=%s range=%s..%s",
                    table_name,
                    index,
                    self.start_date,
                    self.end_date,
                )
                data = yf_download_with_retry(
                    index,
                    start=self.start_date,
                    end=self.end_date,
                    interval="1d",
                    cancel_token=token,
                )
                try:
                    data.columns = data.columns.droplevel(1)
                except Exception:
                    pass
                if data.empty:
                    logger.warning("YF %s returned empty dataframe, skip DB write", table_name)
                    return table_name, None
                converter = DatabaseConverter()
                _check_cancel()
                final_result_df = converter.write_into_db(
                    df=data,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"],
                )
                _check_cancel()
                return table_name, final_result_df
            except CancelledError:
                raise
            except Exception as e:
                logger.error("to_db, %s FAILED EXTRACT DATA from Yfinance, %s", table_name, e)
                return table_name, None

        load_dotenv()
        logger.info("YF submitting %d tasks (sequential execution)", len(items))
        for tn, cfg in items:
            _check_cancel()
            try:
                name, df = worker(tn, cfg)
                if df is not None:
                    df_dict[name] = df
            except CancelledError:
                raise
            except Exception as e:
                logging.error("YF task for %s raised: %s", tn, e)

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
                    logging.error("%s FAILED DOWNLOAD CSV in method 'to_db', since %s", name, err)
                    continue
        return df_dict if return_csv else None
