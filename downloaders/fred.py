"""FRED (Federal Reserve Economic Data) downloader implementation."""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false

from __future__ import annotations

import logging
import os
from datetime import date
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
    http_get_with_retry,
)

logger = logging.getLogger(__name__)


class FREDDownloader(DataDownloader):
    """圣路易斯联储（FRED）下载器。"""

    url: str = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
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
                params = {
                    "series_id": table_config["code"],
                    "api_key": self.api_key,
                    "observation_start": self.start_date,
                    "observation_end": self.end_date,
                    "file_type": "json",
                }
                log_params = {k: v for k, v in params.items() if k != "api_key"}
                logger.info("FRED GET %s params=%s", FREDDownloader.url, log_params)
                resp = http_get_with_retry(FREDDownloader.url, params=params, cancel_token=token)
                data = resp.json()
                df = pd.DataFrame(data.get("observations", []))
                if df.empty:
                    raise Exception("empty observations")
                keep_cols = [c for c in df.columns if c in ("date", "value")]
                df = df[keep_cols].copy()

                if table_config.get("needs_pct", False):   # 查找needs_pct，如果不存在返回false
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    df["MoM_growth"] = df["value"].pct_change()
                    if table_config.get("needs_cleaning", False):
                        df["MoM_growth"] = df["MoM_growth"].ffill()
                    df = df[["date", "MoM_growth"]]
                else:
                    df["value"] = df["value"].replace(".", np.nan)
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    if table_config.get("needs_cleaning", False):
                        df["value"] = df["value"].ffill()
                    df = df[["date", "value"]]

                converter = DatabaseConverter()
                _check_cancel()
                final_result_df = converter.write_into_db(
                    df=df,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"],
                )
                _check_cancel()
                logger.info("%s Successfully extracted! rows=%d", table_name, len(df))
                return table_name, final_result_df
            except CancelledError:
                raise
            except Exception as e:
                logger.error("%s FAILED EXTRACT DATA from FRED: %s", table_name, e)
                return table_name, None

        load_dotenv()
        env_workers = os.environ.get("FRED_WORKERS")
        workers = max_workers or (
            int(env_workers) if env_workers and env_workers.isdigit() else min(12, (os.cpu_count() or 4) * 2)
        )
        logger.info("FRED submitting %d tasks (workers=%d)", len(items), workers)
        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_map = {ex.submit(worker, tn, cfg): tn for tn, cfg in items}
            try:
                for fut in as_completed(future_map):
                    _check_cancel()
                    tn = future_map[fut]
                    try:
                        name, df = fut.result()
                        if df is not None:
                            df_dict[name] = df
                    except CancelledError:
                        logger.info("FRED task %s cancelled", tn)
                        raise
                    except Exception as e:
                        logging.error("FRED future for %s raised: %s", tn, e)
            finally:
                if token is not None and token.cancelled():
                    for fut in future_map:
                        fut.cancel()

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
