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
                        logger.error("FRED future for %s raised: %s", tn, e)
            finally:
                if token is not None and token.cancelled():
                    for fut in future_map:
                        fut.cancel()

        # -------- 衍生指标:M1 与 M2 剪刀差 (M1 YoY - M2 YoY) --------
        # 当 FRED 配置中包含 M1_Total 与 M2_Total 且均成功获取时,
        # 计算周度 YoY 同比增速之差并写入 Time_Series。
        try:
            self._emit_m1m2_spread(df_dict)
        except Exception as e:
            logger.error("M1M2 spread computation failed: %s", e)

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

    def _emit_m1m2_spread(self, df_dict: Dict[str, pd.DataFrame]) -> None:
        """基于已下载的 M1_Total / M2_Total,衍生出 M1M2 剪刀差并落库。

        剪刀差定义:M1 同比增速 − M2 同比增速。
        - 正值:M1 增速快于 M2,流动性趋于活跃;
        - 负值:M2 增速快于 M1,流动性趋于定期化。

        数据频率为周度(WM1NS / WM2NS),YoY 采用 52 周滞后。
        输出表列名:`M1_M2_Spread_YoY`。
        """

        m1 = df_dict.get("M1_Total")
        m2 = df_dict.get("M2_Total")
        if m1 is None or m2 is None:
            logger.info(
                "skip M1M2 spread: m1=%s m2=%s",
                "ok" if m1 is not None else "missing",
                "ok" if m2 is not None else "missing",
            )
            return

        # write_into_db 返回的两列为 ["date", "<data_name>"]
        def _series(df: pd.DataFrame, name: str) -> pd.Series:
            col = name if name in df.columns else [c for c in df.columns if c != "date"][0]
            s = pd.Series(df[col].to_numpy(), index=pd.to_datetime(df["date"]))
            return s.dropna().astype(float)

        s_m1 = _series(m1, "M1_Total")
        s_m2 = _series(m2, "M2_Total")
        # 以周度频率重采样(WM1NS/WM2NS 本身为周频,reindex 到公共日期并向前填充),
        # 再用 52 周滞后计算 YoY。
        common_idx = s_m1.index.union(s_m2.index)
        s_m1 = s_m1.reindex(common_idx).ffill()
        s_m2 = s_m2.reindex(common_idx).ffill()

        # 抽样到周频(每周取一次观测),避免日度 ffill 产生虚假 52 期偏移
        s_m1_w = s_m1.resample("W").last().dropna()
        s_m2_w = s_m2.resample("W").last().dropna()

        yoy_m1 = s_m1_w.pct_change(periods=52)
        yoy_m2 = s_m2_w.pct_change(periods=52)
        spread = (yoy_m1 - yoy_m2).dropna()
        if spread.empty:
            logger.info("skip M1M2 spread: not enough history for 52-week YoY")
            return

        out = pd.DataFrame(
            {
                "date": spread.index.strftime("%Y-%m-%d"),
                "value": spread.astype(float).to_numpy(),
            }
        )
        converter = DatabaseConverter()
        final_df = converter.write_into_db(
            df=out,
            data_name="M1_M2_Spread_YoY",
            start_date=self.start_date,
            is_time_series=True,
            is_pct_data=False,
        )
        if final_df is not None:
            df_dict["M1_M2_Spread_YoY"] = final_df
            logger.info(
                "M1M2 spread derived successfully, rows=%d, last=%s -> %.4f",
                len(out),
                out["date"].iloc[-1],
                float(out["value"].iloc[-1]),
            )
