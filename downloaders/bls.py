"""BLS (Bureau of Labor Statistics) downloader implementation."""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false

from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv

import debug.mock_api as mock_api
from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
    http_post_with_retry,
)

logger = logging.getLogger(__name__)


class BLSDownloader(DataDownloader):
    """美国劳工统计局（BLS）下载器。"""

    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers: Tuple[str, str] = ("Content-type", "application/json")

    def __init__(
        self, json_dict: Dict[str, Dict[str, Any]], api_key: str, request_year: int
    ):
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.api_key: str = api_key
        self.start_year: int = request_year
        self.start_date: str = f"{request_year}-01-01"

    def to_db(
        self,
        return_csv: bool = False,
        max_workers: Optional[int] = None,
        cancel_token: Optional[CancellationToken] = None,
    ) -> Optional[Dict[str, pd.DataFrame]]:
        df_dict: Dict[str, pd.DataFrame] = {}
        bls_debug = os.environ.get("BLS_DEBUG", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        if bls_debug:
            if cancel_token is not None and cancel_token.cancelled():
                raise CancelledError("operation cancelled before BLS debug write")
            converter = DatabaseConverter()
            converter.write_into_db(
                df=mock_api.return_bls_data(),
                data_name="Trial",
                start_date=self.start_date,
                is_time_series=True,
                is_pct_data=False,
            )
            return df_dict if return_csv else None

        items = list(self.json_dict.items())
        if not items:
            return df_dict if return_csv else None

        token = cancel_token

        def _check_cancel() -> None:
            if token is not None:
                token.raise_if_cancelled()

        def worker(
            table_name: str, table_config: Dict[str, Any]
        ) -> Tuple[str, Optional[pd.DataFrame]]:
            _check_cancel()
            try:
                logger.info(
                    "BLS POST %s series_id=%s years=%s..%s",
                    BLSDownloader.url,
                    table_config.get("code"),
                    self.start_year,
                    date.today().year,
                )
                params = json.dumps(
                    {
                        "seriesid": [table_config["code"]],
                        "startyear": self.start_year,
                        "endyear": date.today().year,
                        "registrationKey": self.api_key,
                    }
                )
                load_dotenv()
                bls_timeout_env = os.environ.get("BLS_POST_TIMEOUT")
                bls_timeout = float(bls_timeout_env) if bls_timeout_env else 60.0
                context = http_post_with_retry(
                    BLSDownloader.url,
                    data=params,
                    headers=dict([BLSDownloader.headers]),
                    timeout=bls_timeout,
                    max_attempts=4,
                    delay_seconds=5.0,
                    cancel_token=token,
                )
                json_data = json.loads(context.text)
                logger.info("%s Successfully download data", table_name)
            except CancelledError:
                raise
            except Exception as e:
                logger.error(
                    "%s FAILED EXTRACT DATA from BLS, probably due to API or network issues: %s",
                    table_name,
                    e,
                )
                return table_name, None

            try:
                df = pd.DataFrame(json_data["Results"]["series"][0]["data"]).drop(
                    columns=["periodName", "latest", "footnotes"]
                )
            except Exception:
                try:
                    df = pd.DataFrame(json_data)
                    logger.warning(
                        "%s FAILED REFORMAT: DROP USELESS COLUMNS, continue", table_name
                    )
                except Exception as err:
                    logger.error(
                        "%s FAILED REFORMAT data from BLS, errors in df managing, %s",
                        table_name,
                        err,
                    )
                    return table_name, None

            if table_config["needs_pct"] is True:
                try:
                    df["value"] = pd.to_numeric(df["value"])
                    df["MoM_growth"] = (
                        (df["value"] - df["value"].shift(1))
                        / (df["value"].shift(1))
                        * -1
                    ).shift(-1)
                    df = df.drop(df.columns[-2], axis=1)
                except Exception as err:
                    logger.error(
                        "%s FAILED REFORMAT PERCENTAGE, probably due to df error, %s",
                        table_name,
                        err,
                    )
                    return table_name, None

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

        load_dotenv()
        env_workers = os.environ.get("BLS_WORKERS")
        workers = max_workers or (
            int(env_workers) if env_workers and env_workers.isdigit() else 4
        )
        logger.info("BLS submitting %d tasks (workers=%d)", len(items), workers)
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
                        logger.info("BLS task %s cancelled", tn)
                        raise
                    except Exception as e:
                        logging.error("BLS future for %s raised: %s", tn, e)
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
                    logging.error(
                        "%s FAILED DOWNLOAD CSV in method 'to_db', since %s", name, err
                    )
                    continue
        return df_dict if return_csv else None
