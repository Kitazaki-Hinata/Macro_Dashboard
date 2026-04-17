"""NAAIM(全美投资经理人协会)持仓暴露指数下载器。

数据源:https://www.naaim.org/programs/naaim-exposure-index/
该页面每周更新一个 XLSX 链接,包含自 2006 年以来的完整历史序列。
本下载器先抓取页面定位最新 XLSX URL,再下载解析,写入 `NAAIM_Exposure_Index`。
"""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false

from __future__ import annotations

import io
import logging
import os
import re
from datetime import date
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
    http_get_with_retry,
)

logger = logging.getLogger(__name__)

# 匹配 NAAIM 页面上的 XLSX 下载链接(形如 .../USE_Data-since-Inception_YYYY-MM-DD.xlsx)
_XLSX_HREF_RE = re.compile(
    r'href=["\']([^"\']+\.xlsx)["\']',
    re.IGNORECASE,
)


class NAAIMDownloader(DataDownloader):
    """NAAIM Exposure Index 下载器。"""

    page_url: str = "https://www.naaim.org/programs/naaim-exposure-index/"
    _headers: Dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    def __init__(
        self,
        json_dict: Dict[str, Dict[str, Any]],
        api_key: str,
        request_year: int,
    ) -> None:
        # api_key 仅为了兼容工厂接口,此源不需要
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.start_date: str = f"{request_year}-01-01"
        self.end_date: str = str(date.today())

    def _locate_xlsx_url(
        self, cancel_token: Optional[CancellationToken]
    ) -> str:
        """抓取 NAAIM 页面,返回最新一份 xlsx 数据的绝对 URL。"""

        logger.info("NAAIM GET %s", self.page_url)
        resp = http_get_with_retry(
            self.page_url,
            headers=self._headers,
            cancel_token=cancel_token,
        )
        # 兼容 NAAIM 可能托管于 naaim.org 或 www.naaim.org 的情况
        candidates = [m for m in _XLSX_HREF_RE.findall(resp.text) if "naaim" in m.lower()]
        if not candidates:
            raise Exception("NAAIM page does not expose an xlsx link")
        # 选取文件名中日期最新的(字符串排序对 YYYY-MM-DD 有效)
        candidates.sort()
        return candidates[-1]

    def _fetch_dataframe(
        self, cancel_token: Optional[CancellationToken]
    ) -> pd.DataFrame:
        """下载 xlsx 并返回包含 Date + NAAIM Number 的 DataFrame。"""

        url = self._locate_xlsx_url(cancel_token)
        logger.info("NAAIM download xlsx %s", url)
        resp = http_get_with_retry(
            url,
            headers=self._headers,
            cancel_token=cancel_token,
            timeout=60.0,
        )
        buf = io.BytesIO(resp.content)
        df = pd.read_excel(buf)
        if "Date" not in df.columns or "NAAIM Number" not in df.columns:
            raise Exception(
                f"unexpected NAAIM xlsx schema: {list(df.columns)}"
            )
        out = df[["Date", "NAAIM Number"]].copy()
        out.columns = ["date", "value"]
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
        out = out.dropna(subset=["date"]).drop_duplicates(
            subset=["date"], keep="last"
        )
        out["date"] = out["date"].dt.strftime("%Y-%m-%d")
        out = out.sort_values("date").reset_index(drop=True)
        return out

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

        # NAAIM 配置通常只有单项,顺序处理足够(避免并发多次抓取同一页面)
        for table_name, table_config in items:
            _check_cancel()
            try:
                df = self._fetch_dataframe(token)
                df = df[df["date"] >= self.start_date].copy()
                if df.empty:
                    raise Exception("filtered dataframe is empty")

                if table_config.get("needs_pct", False):
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    df["MoM_growth"] = df["value"].pct_change()
                    if table_config.get("needs_cleaning", False):
                        df["MoM_growth"] = df["MoM_growth"].ffill()
                    df = df[["date", "MoM_growth"]]
                else:
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    if table_config.get("needs_cleaning", False):
                        df["value"] = df["value"].ffill()
                    df = df[["date", "value"]]

                converter = DatabaseConverter()
                _check_cancel()
                final_df = converter.write_into_db(
                    df=df,
                    data_name=table_config["name"],
                    start_date=self.start_date,
                    is_time_series=True,
                    is_pct_data=table_config["needs_pct"],
                )
                _check_cancel()
                logger.info(
                    "%s Successfully extracted from NAAIM! rows=%d",
                    table_name,
                    len(df),
                )
                if final_df is not None:
                    df_dict[table_config["name"]] = final_df
            except CancelledError:
                raise
            except Exception as e:
                logger.error("%s FAILED EXTRACT DATA from NAAIM: %s", table_name, e)

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
                    logger.error(
                        "%s FAILED DOWNLOAD CSV in method 'to_db', since %s",
                        name,
                        err,
                    )
                    continue
        return df_dict if return_csv else None
