"""Shared utilities and base classes for data downloaders.

这一模块承载原 `download.py` 中的通用工具：

- HTTP 与 yfinance 的重试封装
- 数据写入 SQLite 的 `DatabaseConverter`
- 下载器抽象基类 `DataDownloader`

后续每个具体来源的下载器在独立文件中实现，只需从本模块导入上述组件。
"""

from __future__ import annotations

import logging
import random
import re
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
import yfinance as yf

# 基础路径（downloaders 目录）与共享 CSV 输出目录
DOWNLOADERS_ROOT = Path(__file__).resolve().parent
CSV_DATA_FOLDER = DOWNLOADERS_ROOT.parent / "csv"

# 全局 DB 写锁，避免并发写入 SQLite 导致数据丢失或锁冲突
DB_WRITE_LOCK = threading.Lock()

# 模块级 logger（与异步日志模块配合使用）
logger = logging.getLogger(__name__)


class CancelledError(RuntimeError):
	"""Raised when a download operation is cancelled by the caller."""


class CancellationToken:
	"""Thread-safe cancellation flag shared across download tasks."""

	def __init__(self) -> None:
		self._event = threading.Event()

	def cancel(self) -> None:
		self._event.set()

	def cancelled(self) -> bool:
		return self._event.is_set()

	def raise_if_cancelled(self) -> None:
		if self._event.is_set():
			raise CancelledError("operation cancelled")


def _sleep_with_cancel(delay: Optional[float], cancel_token: Optional[CancellationToken]) -> None:
	"""Sleep for *delay* seconds while remaining responsive to cancellation."""

	if delay is None:
		return
	remaining = float(delay)
	if remaining <= 0:
		return
	if cancel_token is None:
		time.sleep(remaining)
		return
	deadline = time.monotonic() + remaining
	while True:
		if cancel_token.cancelled():
			raise CancelledError("operation cancelled during backoff")
		remaining = deadline - time.monotonic()
		if remaining <= 0:
			return
		time.sleep(min(0.1, remaining))


def _exponential_backoff_delays(max_attempts: int, base: float = 0.5, factor: float = 2.0, jitter: float = 0.25) -> List[float]:
	"""生成指数退避延时序列（带抖动）。"""

	delays: List[float] = []
	d = base
	for _ in range(max_attempts):
		delays.append(max(0.0, d + random.uniform(-jitter, jitter)))
		d *= factor
	return delays


def http_get_with_retry(url: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: float = 30.0, max_attempts: int = 4, cancel_token: Optional[CancellationToken] = None) -> requests.Response:
	"""带重试的 HTTP GET。"""

	delays = _exponential_backoff_delays(max_attempts)
	last_exc: Optional[Exception] = None
	for i, delay in enumerate(delays, start=1):
		if cancel_token is not None:
			cancel_token.raise_if_cancelled()
		try:
			t0 = time.perf_counter()
			resp = requests.get(url, params=params, headers=headers, timeout=timeout)
			dt = time.perf_counter() - t0
			status = getattr(resp, "status_code", None)
			logger.info("HTTP GET %s attempt=%d status=%s in %.3fs", url, i, status, dt)
			if resp.ok:
				return resp
			if status is not None and 400 <= int(status) < 500 and int(status) in {400, 401, 403, 404, 405, 406, 410, 422}:
				raise Exception(f"non-retriable client error: status={status}")
			last_exc = Exception(f"status={status}")
		except Exception as e:
			last_exc = e
			logger.warning("HTTP GET %s attempt=%d failed: %s", url, i, e)
		if i < max_attempts:
			try:
				_sleep_with_cancel(delay, cancel_token)
			except CancelledError:
				raise
	if cancel_token is not None:
		cancel_token.raise_if_cancelled()
	raise Exception(f"GET {url} failed after {max_attempts} attempts: {last_exc}")


def http_post_with_retry(url: str, *, data: Any = None, json_data: Any = None, headers: Optional[Dict[str, str]] = None, timeout: float = 30.0, max_attempts: int = 4, delay_seconds: Optional[float] = None, cancel_token: Optional[CancellationToken] = None) -> requests.Response:
	"""带重试的 HTTP POST（支持固定间隔或指数退避）。"""

	delays = [delay_seconds] * max_attempts if delay_seconds is not None else _exponential_backoff_delays(max_attempts)
	last_exc: Optional[Exception] = None
	for i, delay in enumerate(delays, start=1):
		if cancel_token is not None:
			cancel_token.raise_if_cancelled()
		try:
			t0 = time.perf_counter()
			resp = requests.post(url, data=data, json=json_data, headers=headers, timeout=timeout)
			dt = time.perf_counter() - t0
			status = getattr(resp, "status_code", None)
			logger.info("HTTP POST %s attempt=%d status=%s in %.3fs", url, i, status, dt)
			if resp.ok:
				return resp
			if status is not None and 400 <= int(status) < 500 and int(status) in {400, 401, 403, 404, 405, 406, 410, 422}:
				raise Exception(f"non-retriable client error: status={status}")
			last_exc = Exception(f"status={status}")
		except Exception as e:
			last_exc = e
			logger.warning("HTTP POST %s attempt=%d failed: %s", url, i, e)
		if i < max_attempts:
			try:
				logger.info("Retrying POST in %.1fs (attempt %d/%d)", float(delay), i + 1, max_attempts)
				_sleep_with_cancel(delay, cancel_token)
			except CancelledError:
				raise
			except Exception:
				pass
	if cancel_token is not None:
		cancel_token.raise_if_cancelled()
	raise Exception(f"POST {url} failed after {max_attempts} attempts: {last_exc}")


def yf_download_with_retry(symbol: str, *, start: str, end: str, interval: str = "1d", max_attempts: int = 5, cancel_token: Optional[CancellationToken] = None) -> pd.DataFrame:
	"""yfinance.download 包装器（带指数退避与限流容错）。"""

	delays = _exponential_backoff_delays(max_attempts=max_attempts, base=1.0, factor=2.0, jitter=0.5)
	last_err: Optional[Exception] = None

	for i, dly in enumerate(delays, start=1):
		if cancel_token is not None:
			cancel_token.raise_if_cancelled()
		try:
			t0 = time.perf_counter()
			df = pd.DataFrame(
				yf.download(
					symbol,
					start=start,
					end=end,
					interval=interval,
					auto_adjust=False,
					progress=False,
					threads=False,
				)
			)
			dt = time.perf_counter() - t0
			logger.info("YF GET %s attempt=%d rows=%d in %.3fs", symbol, i, len(df), dt)
			if not df.empty:
				return df
			last_err = Exception("empty dataframe")
		except Exception as e:
			last_err = e
			logger.warning("YF GET %s attempt=%d failed: %s", symbol, i, getattr(e, "message", str(e)))
		if i < max_attempts:
			try:
				_sleep_with_cancel(dly, cancel_token)
			except CancelledError:
				raise
	raise Exception(f"yfinance download failed for {symbol} after {max_attempts} attempts: {last_err}")


class DatabaseConverter:
	"""将不同来源的 DataFrame 规范化并写入 SQLite。"""

	_MONTH_MAP = {
		"jan": 1, "feb": 2, "mar": 3, "apr": 4,
		"may": 5, "jun": 6, "jul": 7, "aug": 8,
		"sep": 9, "oct": 10, "nov": 11, "dec": 12
	}
	end_date: date = date.today()

	def __init__(self, db_file: str = "data.db") -> None:
		self.db_file: str = db_file
		self.conn: sqlite3.Connection = sqlite3.connect(db_file)
		self.cursor: sqlite3.Cursor = self.conn.cursor()

	@staticmethod
	def _convert_month_str_to_num(month_str: str) -> Optional[int]:
		return DatabaseConverter._MONTH_MAP.get(str(month_str).casefold(), None)

	@staticmethod
	def _rename_bea_date_col(df: pd.DataFrame) -> pd.DataFrame:
		try:
			date_col = df.pop("date")  # type: ignore
			df.insert(0, "date", date_col)  # type: ignore
			return df
		except Exception as e:
			logging.error(f"{e}, FAILED to write into database")
			df = pd.DataFrame()
			return df

	@staticmethod
	def _format_converter(df: Optional[pd.DataFrame], data_name: str, is_pct_data: bool) -> pd.DataFrame:
		if df is None or df.empty:
			return pd.DataFrame()
		df = df.copy()

		def finalize_with_date_first(df_in: pd.DataFrame) -> pd.DataFrame:
			if "date" not in df_in.columns:
				return df_in
			dates = pd.to_datetime(df_in["date"], errors="coerce")
			df_in = df_in.assign(date=dates.dt.strftime("%Y-%m-%d"))
			df_in = df_in.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
			if data_name in df_in.columns:
				cols = ["date"] + [c for c in df_in.columns if c != "date"]
				df_in = df_in.reindex(columns=cols)
			return df_in

		logger.debug("_format_converter start: data=%s empty=%s columns=%s index_name=%s shape=%s", data_name, df.empty, list(df.columns), getattr(df.index, "name", None), tuple(df.shape))
		try:
			sample = str(df.index[0]) if len(df.index) else ""
			if re.fullmatch(r"\d{4}", sample):
				logger.debug("_format_converter matched BEA annual for %s (sample=%s)", data_name, sample)
				df["date"] = [f"{int(y)}-12-31" for y in df.index.astype(str)]
				df = DatabaseConverter._rename_bea_date_col(df)
				return finalize_with_date_first(df.rename_axis(None, axis=1))
			if re.fullmatch(r"\d{4}Q[1-4]", sample):
				logger.debug("_format_converter matched BEA quarterly for %s (sample=%s)", data_name, sample)

				def q_to_date(s: str) -> str:
					y, q = s.split("Q")
					y = int(y)
					q = int(q)
					m = q * 3 + 1
					if m > 12:
						y += 1
						m = 1
					return f"{y}-{m:02d}-01"

				df["date"] = [q_to_date(str(s)) for s in df.index]
				df = DatabaseConverter._rename_bea_date_col(df)
				return finalize_with_date_first(df)
			if re.fullmatch(r"\d{4}M\d{2}", sample):
				logger.debug("_format_converter matched BEA monthly for %s (sample=%s)", data_name, sample)

				def m_to_date(s: str) -> str:
					y, m = s.split("M")
					y = int(y)
					m = int(m)
					if m == 12:
						y += 1
						m = 1
					else:
						m += 1
					return f"{y}-{m:02d}-01"

				df["date"] = [m_to_date(str(s)) for s in df.index]
				df = DatabaseConverter._rename_bea_date_col(df)
				return finalize_with_date_first(df)
		except Exception as e:
			logging.warning(f"BEA match failed in _format_converter: {e}")

		try:
			ohlcv = {"Open", "High", "Low", "Close", "Volume"}
			if set(df.columns) >= ohlcv:
				logger.debug("_format_converter matched YF OHLCV for %s", data_name)
				dates = pd.to_datetime(df.index, errors="coerce").strftime("%Y-%m-%d")
				df = df.assign(date=dates)
				out = pd.DataFrame({
					"date": df["date"],
					data_name: df["Close"]
				})
				return finalize_with_date_first(out)
		except Exception as e:
			logging.warning(f"yfinance match failed in _format_converter: {e}")

		try:
			if "date" in df.columns and str(df["date"].iloc[1])[4] == "-":
				logger.debug("_format_converter matched FRED style for %s", data_name)
				value_cols = [c for c in df.columns if c != "date"]
				if value_cols:
					col = value_cols[0]
					out = df[["date", col]].copy()
					out = out.rename(columns={col: data_name})
					return finalize_with_date_first(out)
		except Exception as e:
			logging.warning(f"FRED match failed in _format_converter: {e}")

		try:
			cols = list(df.columns)
			if cols == ["year", "period", "value"] or cols == ["year", "period", "MoM_growth"]:
				logger.debug("_format_converter matched BLS style for %s", data_name)
				period = df["period"].astype(str)
				if period.str.startswith("M").any():
					month_series = period.str[1:].astype(int)
					month_series = month_series.where(month_series != 12, 0) + 1
					month_series = month_series.astype(str).str.zfill(2)
				elif period.str.startswith("Q").any():
					logger.debug("_format_converter BLS quarterly period detected for %s", data_name)

					def q_to_month(s: str) -> int:
						try:
							q = int(s[1:])
							return {1: 4, 2: 7, 3: 10, 4: 1}.get(q, 1)
						except Exception:
							return 1

					month_series = period.apply(q_to_month).astype(str).str.zfill(2)
				else:
					month_series = pd.Series(["01"] * len(df), index=df.index)

				year_num = pd.to_numeric(df["year"], errors="coerce")
				year_num = year_num.where(month_series != "01", year_num + 1)
				month_num = pd.to_numeric(month_series, errors="coerce")
				dt = pd.to_datetime(pd.DataFrame({"year": year_num, "month": month_num, "day": 1}), errors="coerce")
				df["date"] = dt.dt.strftime("%Y-%m-%d")
				val_col = "value" if "value" in df.columns else "MoM_growth"
				out = df[["date", val_col]].copy().rename(columns={val_col: data_name})
				return finalize_with_date_first(out)
		except Exception as e:
			logging.warning(f"BLS match failed in _format_converter: {e}")

		try:
			if "date" in df.columns and df["date"].astype(str).str.contains(r"^[A-Za-z]{3}_[0-9]{4}$").any():
				logger.debug("_format_converter matched TE style for %s", data_name)
				df = df.rename(columns={"value": data_name, "date": "Date"})
				split_data = df["Date"].astype(str).str.split("_", expand=True)
				month_str = split_data[0]
				year = pd.to_numeric(split_data[1], errors="coerce")
				dec_mask = (month_str == "Dec")
				year = year.where(~dec_mask, year + 1)
				month = month_str.apply(DatabaseConverter._convert_month_str_to_num)
				month = month.where(~dec_mask, 1)
				month_num = pd.to_numeric(month, errors="coerce")
				dt = pd.to_datetime(pd.DataFrame({"year": year, "month": month_num, "day": 1}), errors="coerce")
				df["date"] = dt.dt.strftime("%Y-%m-%d")
				df = df.drop(columns=["Date"], errors="ignore")
				date_col = df.pop("date")
				df.insert(0, "date", date_col)
				return finalize_with_date_first(df)
		except Exception as e:
			logging.warning(f"TE match failed in _format_converter: {e}")

		try:
			if "date" in df.columns:
				logger.debug("_format_converter fallback by date column for %s", data_name)
				return finalize_with_date_first(df.rename(columns={df.columns[1]: data_name}) if len(df.columns) > 1 else df)
			else:
				logger.debug("_format_converter fallback by index->date for %s", data_name)
				dates = pd.to_datetime(pd.Series(df.index).astype(str), errors="coerce").dt.strftime("%Y-%m-%d")
				out = pd.DataFrame({"date": dates})
				if df.shape[1] >= 1:
					out[data_name] = list(df.iloc[:, 0])
				return finalize_with_date_first(out)
		except Exception as e:
			logging.warning(f"fallback in _format_converter failed: {e}")
			return df

	def _create_ts_sheet(self, start_date: str) -> sqlite3.Cursor:
		cursor = self.cursor
		logger.debug("ensure Time_Series table exists (start_date=%s)", start_date)
		cursor.execute("SELECT name FROM sqlite_master WHERE type= 'table' AND name  = 'Time_Series'")
		table_exists = cursor.fetchone() is not None

		try:
			if not table_exists:
				t0 = time.perf_counter()
				cursor.execute("CREATE TABLE IF NOT EXISTS Time_Series(date DATE PRIMARY KEY)")
				current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
				while current_date <= DatabaseConverter.end_date:
					cursor.execute(
						"INSERT OR IGNORE INTO Time_Series (date) VALUES (?)",
						(current_date.strftime("%Y-%m-%d"),)
					)
					current_date += timedelta(days=1)
				self.conn.commit()
				logger.info("Time_Series table created and initialized (%.3fs)", time.perf_counter() - t0)
				return cursor
			else:
				logger.info("Time_Series table already exists, continue")
				cursor.execute("SELECT MIN(date), MAX(date) FROM Time_Series")
				row = cursor.fetchone()
				min_date_str, max_date_str = (row if row else (None, None))
				start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
				if not max_date_str:
					max_date = start_date_obj
				else:
					max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
				if not min_date_str:
					min_date = start_date_obj
				else:
					min_date = datetime.strptime(min_date_str, "%Y-%m-%d").date()

				if start_date_obj < min_date:
					t0_back = time.perf_counter()
					dates_to_prepend: List[date] = []
					d = min_date - timedelta(days=1)
					while d >= start_date_obj:
						dates_to_prepend.append(d)
						d -= timedelta(days=1)
					for d in reversed(dates_to_prepend):
						cursor.execute("INSERT OR IGNORE INTO Time_Series (date) VALUES (?)", (d.strftime("%Y-%m-%d"),))
					self.conn.commit()
					logger.info("Time_Series table prepended %d earlier date rows (%.3fs)", len(dates_to_prepend), time.perf_counter() - t0_back)

				current_date = datetime.now().date()
				if current_date > max_date:
					t0_fwd = time.perf_counter()
					dates_to_add: List[date] = []
					while current_date > max_date:
						dates_to_add.append(current_date)
						current_date -= timedelta(days=1)
					for d in dates_to_add:
						cursor.execute("INSERT OR IGNORE INTO Time_Series (date) VALUES (?)", (d.strftime("%Y-%m-%d"),))
					self.conn.commit()
					logger.info("Time_Series table appended %d future date rows (%.3fs)", len(dates_to_add), time.perf_counter() - t0_fwd)
				return cursor

		except sqlite3.Error as e:
			logging.error(f"FAILED to create Time_Series table, since {e}")
			return cursor

	def _ensure_ts_primary_key(self) -> None:
		cursor = self.cursor
		try:
			cursor.execute("PRAGMA table_info('Time_Series')")
			cols_info = cursor.fetchall()
			if not cols_info:
				return
			has_pk = any(row[1] == "date" and row[5] == 1 for row in cols_info)
			if has_pk:
				return
			logger.warning("Time_Series missing PRIMARY KEY on 'date' – rebuilding to restore constraint")
			existing_cols: List[str] = [row[1] for row in cols_info]
			if "date" not in existing_cols:
				logger.error("Time_Series table unexpectedly lacks 'date' column, skip pk repair")
				return
			col_type_map: Dict[str, str] = {row[1]: (row[2] or "REAL") for row in cols_info}
			create_cols_def: List[str] = ["date TEXT PRIMARY KEY"]
			data_cols: List[str] = [c for c in existing_cols if c != "date"]
			for c in data_cols:
				t = col_type_map.get(c, "REAL")
				if not re.fullmatch(r"[A-Za-z0-9_]+", t):
					t = "REAL"
				create_cols_def.append(f"{c} {t}")
			create_sql = f"CREATE TABLE Time_Series_new ({', '.join(create_cols_def)})"
			cursor.execute(create_sql)
			select_cols = ', '.join(existing_cols)
			insert_cols = ', '.join(existing_cols)
			cursor.execute(
				f"INSERT OR REPLACE INTO Time_Series_new ({insert_cols}) "
				f"SELECT {select_cols} FROM Time_Series t WHERE date IS NOT NULL GROUP BY date"
			)
			cursor.execute("ALTER TABLE Time_Series RENAME TO Time_Series_backup")
			cursor.execute("ALTER TABLE Time_Series_new RENAME TO Time_Series")
			cursor.execute("DROP TABLE IF EXISTS Time_Series_backup")
			self.conn.commit()
			logger.info("Time_Series primary key restored; columns=%s", ['date'] + data_cols)
		except Exception as e:
			logger.error("Failed to ensure PRIMARY KEY on Time_Series: %s", e)
			self.conn.rollback()

	def write_into_db(
		self,
		df: pd.DataFrame,
		data_name: str,
		start_date: str,
		is_time_series: bool = False,
		is_pct_data: bool = False,
		overwrite_existing: bool = True,
		only_fill_null: bool = False
	):
		with DB_WRITE_LOCK:
			t_all = time.perf_counter()
			self._create_ts_sheet(start_date=start_date)
			self._ensure_ts_primary_key()
			cursor = self.cursor
			try:
				logger.info("write_into_db start: data=%s, is_time_series=%s, shape=%s", data_name, is_time_series, tuple(df.shape))
				if df.empty:
					logger.error(f"{data_name} is empty, FAILED INSERT, locate in write_into_db")
				else:
					if is_time_series:
						t0 = time.perf_counter()
						df_fmt: pd.DataFrame = DatabaseConverter._format_converter(df, data_name, is_pct_data)
						logger.debug("%s after format: columns=%s, shape=%s", data_name, list(df_fmt.columns), tuple(df_fmt.shape))
						if df_fmt.empty or "date" not in df_fmt.columns:
							logger.error("%s reformat produced empty/invalid dataframe, skip writing", data_name)
							return
						df_fmt = df_fmt.copy()
						df_fmt["date"] = pd.to_datetime(df_fmt["date"], errors="coerce")
						df_fmt = df_fmt.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
						df_fmt["date"] = df_fmt["date"].dt.strftime("%Y-%m-%d")

						all_dates = pd.date_range(start=start_date, end=date.today(), freq="D")
						df_full = pd.DataFrame({"date": [d.strftime("%Y-%m-%d") for d in all_dates]})
						df_full = df_full.merge(df_fmt, on="date", how="left")
						if df_full[data_name].notna().any():
							mask = df_full[data_name].notna().to_numpy(dtype=bool, copy=False)
							first_valid_pos = int(np.flatnonzero(mask)[0])
							if pd.isna(df_full.iloc[0][data_name]):
								first_valid_value = df_full.iloc[first_valid_pos][data_name]
								df_full.loc[df_full.index[:first_valid_pos + 1], data_name] = first_valid_value
						df_full[data_name] = df_full[data_name].ffill()

						if not re.fullmatch(r"[A-Za-z0-9_]+", data_name):
							logger.error("Invalid column name '%s', abort writing", data_name)
							return
						try:
							cursor.execute(f"ALTER TABLE Time_Series ADD COLUMN {data_name} REAL")
							logger.debug("added column '%s' to Time_Series", data_name)
						except sqlite3.Error:
							pass

						existing_map: Dict[str, Optional[float]] = {}
						if (not overwrite_existing) or only_fill_null:
							try:
								cursor.execute(f"SELECT date, {data_name} FROM Time_Series")
								for d, val in cursor.fetchall():
									existing_map[str(d)] = val
							except sqlite3.Error:
								pass

						update_rows: List[Tuple[float, str]] = []
						for date_str, v in df_full[["date", data_name]].itertuples(index=False, name=None):
							if pd.isna(v):
								continue
							ds = str(date_str)
							if only_fill_null:
								if ds in existing_map and existing_map[ds] is not None:
									continue
							elif not overwrite_existing:
								if ds in existing_map and existing_map[ds] is not None:
									continue
							update_rows.append((float(v), ds))
						t_sql = time.perf_counter()
						if update_rows:
							cursor.executemany(
								f"UPDATE Time_Series SET {data_name}=? WHERE date=?",
								update_rows
							)
						self.conn.commit()
						logger.info(
							"write_into_db(Time_Series/%s)[incremental mode=%s fill_null=%s]: updated %d rows (format %.3fs + update %.3fs, total %.3fs)",
							data_name,
							'overwrite' if overwrite_existing else 'no_overwrite',
							only_fill_null,
							len(update_rows),
							(time.perf_counter() - t0),
							(time.perf_counter() - t_sql),
							(time.perf_counter() - t0)
						)
						rtn_df = df_full[["date", data_name]].copy()
						logger.debug("%s returns 2 cols shape=%s", data_name, tuple(rtn_df.shape))
						logger.info("write_into_db finished: data=%s (%.3fs)", data_name, time.perf_counter() - t_all)
						return rtn_df
					else:
						cols = list(df.columns)
						has_date = "date" in cols
						cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (data_name,))
						exists = cursor.fetchone() is not None
						if not exists:
							df.to_sql(data_name, self.conn, if_exists='fail', index=False)
							self.conn.commit()
							logger.info("write_into_db(sheet=%s): created table rows=%d", data_name, len(df))
						else:
							if has_date:
								cursor.execute(f"PRAGMA table_info('{data_name}')")
								info = cursor.fetchall()
								has_pk = any(r[1] == 'date' and r[5] == 1 for r in info)
								if not has_pk:
									tmp_cols = [r[1] for r in info]
									cursor.execute(f"ALTER TABLE {data_name} RENAME TO {data_name}_backup")
									col_defs = ["date TEXT PRIMARY KEY"] + [f"{c} REAL" for c in tmp_cols if c != 'date']
									cursor.execute(f"CREATE TABLE {data_name} ({', '.join(col_defs)})")
									cols_sel = ','.join(tmp_cols)
									cursor.execute(f"INSERT OR REPLACE INTO {data_name} ({cols_sel}) SELECT {cols_sel} FROM {data_name}_backup")
									cursor.execute(f"DROP TABLE {data_name}_backup")
									self.conn.commit()
								if df['date'].dtype != object:
									try:
										df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
									except Exception:
										pass
								insert_cols = ','.join(cols)
								placeholders = ','.join(['?'] * len(cols))
								rows = [tuple(x if (not (isinstance(x, float) and np.isnan(x))) else None for x in r) for r in df.itertuples(index=False, name=None)]
								cursor.executemany(
									f"INSERT OR REPLACE INTO {data_name} ({insert_cols}) VALUES ({placeholders})",
									rows
								)
								self.conn.commit()
								logger.info("write_into_db(sheet=%s): upserted %d rows", data_name, len(rows))
							else:
								df.to_sql(data_name, self.conn, if_exists='append', index=False)
								self.conn.commit()
								logger.warning("write_into_db(sheet=%s): appended %d rows (no date pk)", data_name, len(df))
						logger.info("write_into_db finished: data=%s (%.3fs)", data_name, time.perf_counter() - t_all)
						self.conn.close()
						return df

			except Exception as e:
				logger.error(f"FAILED to write into database, in method write_into_db, since {e}")
				print(f"error {e}")
				return


class DataDownloader(ABC):
	"""下载器抽象基类。"""

	@abstractmethod
	def to_db(self, return_csv: bool = False, max_workers: Optional[int] = None, cancel_token: Optional["CancellationToken"] = None) -> Optional[Dict[str, pd.DataFrame]]:
		raise NotImplementedError
