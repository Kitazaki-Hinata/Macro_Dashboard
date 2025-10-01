"""BEA (Bureau of Economic Analysis) downloader implementation."""

from __future__ import annotations

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Any, Dict, Optional, Tuple

import beaapi
import pandas as pd

from downloaders.common import CSV_DATA_FOLDER, DatabaseConverter, DataDownloader

logger = logging.getLogger(__name__)


class BEADownloader(DataDownloader):
    """美国经济分析局（BEA）下载器。"""

    current_year: int = date.today().year
    csv_data_folder: str = os.fspath(CSV_DATA_FOLDER)

    def __init__(
        self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
        self.request_year: int = request_year
        self.time_range: str = ",".join(
            map(str, range(request_year, BEADownloader.current_year + 1))
        )
        self.time_range_lag: str = self.time_range[:-5]

    def to_db(
        self, return_csv: bool = False, max_workers: Optional[int] = None
    ) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        items = list(self.json_dict.items())
        if not items:
            return None

        def worker(
            table_name: str, table_config: Dict[str, Any]
        ) -> Tuple[str, Optional[pd.DataFrame]]:
            try:
                logger.info(
                    "BEA start: table=%s code=%s freq=%s years=%s",
                    table_name,
                    table_config.get("code"),
                    table_config.get("freq"),
                    self.time_range,
                )
                try:
                    t0 = time.perf_counter()
                    bea_tbl = beaapi.get_data(
                        self.api_key,
                        datasetname=table_config["category"],
                        TableName=table_config["code"],
                        Frequency=table_config["freq"],
                        Year=self.time_range,
                    )
                    logger.info(
                        "BEA fetched primary range for %s (%.3fs)",
                        table_name,
                        time.perf_counter() - t0,
                    )
                except beaapi.beaapi_error.BEAAPIResponseError:
                    t0 = time.perf_counter()
                    bea_tbl = beaapi.get_data(
                        self.api_key,
                        datasetname=table_config["category"],
                        TableName=table_config["code"],
                        Frequency=table_config["freq"],
                        Year=self.time_range_lag,
                    )
                    logger.warning(
                        "BEA fallback years used for %s (%.3fs)",
                        table_name,
                        time.perf_counter() - t0,
                    )
                df: pd.DataFrame = pd.DataFrame(bea_tbl)
                try:
                    ld_series = df["LineDescription"].fillna("")
                    pick = (
                        ld_series.iloc[1]
                        if len(ld_series) > 1
                        else (ld_series.iloc[0] if len(ld_series) else "")
                    )
                except Exception:
                    pick = ""
                df_filtered: pd.DataFrame = df[
                    df["LineDescription"].isin([pick, ""])
                ].copy()

                def _last_or_none(s: pd.Series) -> Any:
                    return s.iloc[-1] if len(s) else None

                df_modified: pd.DataFrame = pd.pivot_table(
                    df_filtered,
                    index="TimePeriod",
                    columns="LineDescription",
                    values="DataValue",
                    aggfunc=_last_or_none,
                )
                df_modified.columns = [f"{table_config['name']}"]
                df_modified.index.name = "TimePeriod"
                logger.info(
                    "BEA_%s Successfully extracted! rows=%d",
                    table_name,
                    len(df_modified),
                )

                if df_modified.empty:
                    logging.error(
                        "%s is empty, FAILED INSERT, locate in to_db", table_name
                    )
                    return table_name, None
                converter = DatabaseConverter()
                final_result_df = converter.write_into_db(
                    df=df_modified,
                    data_name=table_config["name"],
                    start_date=str(date(self.request_year, 1, 1)),
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"],
                )
                return table_name, final_result_df
            except Exception as e:
                logger.error(
                    "%s FAILED DOWNLOAD/REFORMAT in BEA worker: %s", table_name, e
                )
                return table_name, None

        workers_env = os.environ.get("BEA_WORKERS")
        workers = max_workers or (
            int(workers_env)
            if workers_env and workers_env.isdigit()
            else min(8, (os.cpu_count() or 4) * 2)
        )
        logger.info("BEA submitting %d tasks (workers=%d)", len(items), workers)
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
                                data_folder_path = os.path.join(
                                    BEADownloader.csv_data_folder, name
                                )
                                os.makedirs(data_folder_path, exist_ok=True)
                                csv_path = os.path.join(data_folder_path, f"{name}.csv")
                                df.to_csv(csv_path, index=True)
                                logging.info(
                                    "%s saved to %s Successfully!", name, csv_path
                                )
                            except Exception as err:
                                logging.error(
                                    "%s FAILED DOWNLOAD CSV in method 'to_csv', since %s",
                                    name,
                                    err,
                                )
                                continue
                except Exception as e:
                    logging.error("BEA future for %s raised: %s", tn, e)
        return df_dict if return_csv else None
