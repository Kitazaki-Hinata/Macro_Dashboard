"""multpl.com 数据源下载器。

覆盖 S&P 500 估值类月度指标，例如 PE Ratio、Shiller PE、股息率等。
数据来自 https://www.multpl.com/ 公开表格页面，使用 HTTP + BeautifulSoup 解析，
无需 selenium。每个指标对应一个 URL 子路径，通过 `code` 字段配置。
"""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false

from __future__ import annotations

import logging
import os
import re
from datetime import date
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from downloaders.common import (
    CSV_DATA_FOLDER,
    CancelledError,
    CancellationToken,
    DatabaseConverter,
    DataDownloader,
    http_get_with_retry,
)

logger = logging.getLogger(__name__)

# multpl 页面表格常见的“estimate”等备注标记，解析数值前需剔除
_MULTPL_ANNOTATION_RE = re.compile(r"\s*(estimate|est\.?|\*+)\s*$", re.IGNORECASE)


class MultplDownloader(DataDownloader):
    """multpl.com 月度估值指标下载器。"""

    base_url: str = "https://www.multpl.com"
    # 使用常见桌面浏览器 UA，避免个别页面对默认 requests UA 返回 403
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
        # api_key 形参保留以兼容 DownloaderFactory 接口，此源无需密钥
        self.json_dict: Dict[str, Dict[str, Any]] = json_dict
        self.start_date: str = f"{request_year}-01-01"
        self.end_date: str = str(date.today())

    @staticmethod
    def _parse_value(raw: str) -> Optional[float]:
        """将 multpl 表格单元格的字符串解析为浮点数。

        - 去除末尾的 "estimate" / "*" 之类注释；
        - 去除千位分隔符与百分号；
        - 解析失败返回 None。
        """

        if raw is None:
            return None
        text = _MULTPL_ANNOTATION_RE.sub("", str(raw).strip())
        text = text.replace(",", "").replace("%", "").strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _fetch_table(
        self,
        code: str,
        cancel_token: Optional[CancellationToken],
    ) -> pd.DataFrame:
        """拉取指定指标的月度历史表格并返回 (date, value) 两列 DataFrame。"""

        url = f"{self.base_url}/{code}/table/by-month"
        logger.info("multpl GET %s", url)
        resp = http_get_with_retry(
            url,
            headers=self._headers,
            cancel_token=cancel_token,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", id="datatable") or soup.find("table")
        if table is None:
            raise Exception(f"multpl page for {code} has no table")

        rows_out: list[Tuple[str, Optional[float]]] = []
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            date_text = cells[0].get_text(strip=True)
            value_text = cells[1].get_text(" ", strip=True)
            # 跳过表头（首列非日期）
            try:
                parsed_date = pd.to_datetime(date_text, errors="coerce")
            except Exception:
                parsed_date = pd.NaT
            if pd.isna(parsed_date):
                continue
            rows_out.append(
                (parsed_date.strftime("%Y-%m-%d"), self._parse_value(value_text))
            )

        if not rows_out:
            raise Exception(f"multpl page for {code} parsed 0 rows")

        df = pd.DataFrame(rows_out, columns=["date", "value"])
        df = df.dropna(subset=["value"])
        # multpl 表格按倒序排列，统一升序更便于后续 pct_change / ffill
        df = df.sort_values("date").reset_index(drop=True)
        return df

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

        def worker(
            table_name: str, table_config: Dict[str, Any]
        ) -> Tuple[str, Optional[pd.DataFrame]]:
            _check_cancel()
            try:
                df = self._fetch_table(table_config["code"], token)

                # 按请求起始年份过滤（DatabaseConverter 内部也会裁剪，这里先减少量）
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
                    "%s Successfully extracted from multpl! rows=%d",
                    table_name,
                    len(df),
                )
                return table_name, final_df
            except CancelledError:
                raise
            except Exception as e:
                logger.error("%s FAILED EXTRACT DATA from multpl: %s", table_name, e)
                return table_name, None

        env_workers = os.environ.get("MULTPL_WORKERS")
        workers = max_workers or (
            int(env_workers)
            if env_workers and env_workers.isdigit()
            else min(6, max(2, len(items)))
        )
        logger.info("multpl submitting %d tasks (workers=%d)", len(items), workers)
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
                        logger.info("multpl task %s cancelled", tn)
                        raise
                    except Exception as e:
                        logger.error("multpl future for %s raised: %s", tn, e)
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
                    logger.info("%s saved to %s Successfully!", name, csv_path)
                except Exception as err:
                    logger.error(
                        "%s FAILED DOWNLOAD CSV in method 'to_db', since %s",
                        name,
                        err,
                    )
                    continue
        return df_dict if return_csv else None
