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
        # 通过线程池并行下载多个 yfinance 标的（IO 密集型，GIL 在网络等待期间释放），
        # 与 FRED/BLS/BEA 下载器保持一致的并发模式。
        # 工作线程数可由环境变量 YF_WORKERS 覆盖；默认偏小以避免触发 Yahoo 限流。
        env_workers = os.environ.get("YF_WORKERS")
        workers = max_workers or (
            int(env_workers) if env_workers and env_workers.isdigit() else min(8, (os.cpu_count() or 4) * 2)
        )
        logger.info("YF submitting %d tasks (workers=%d)", len(items), workers)
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
                        logger.info("YF task %s cancelled", tn)
                        raise
                    except Exception as e:
                        logger.error("YF task for %s raised: %s", tn, e)
            except CancelledError:
                # 取消时立即停止派发剩余任务，避免无谓的网络请求
                for f in future_map:
                    f.cancel()
                raise

        if return_csv and df_dict:
            _check_cancel()
            for name, df in df_dict.items():
                try:
                    data_folder_path = os.path.join(os.fspath(CSV_DATA_FOLDER), name)
                    os.makedirs(data_folder_path, exist_ok=True)
                    csv_path = os.path.join(data_folder_path, f"{name}.csv")
                    df.to_csv(csv_path, index=True)
                    logger.info("%s saved to %s Successfully!", name, csv_path)
                except Exception as err:
                    logger.error("%s FAILED DOWNLOAD CSV in method 'to_db', since %s", name, err)
                    continue
        return df_dict if return_csv else None
