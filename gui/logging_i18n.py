from __future__ import annotations

import logging
from typing import Any, Mapping

from .i18n_support import translate

_LOG_PREFIX = "logs.messages."


def _full_key(key: str) -> str:
    if key.startswith("logs."):
        return key
    return f"{_LOG_PREFIX}{key}"


def _safe_translate(key: str, params: Mapping[str, Any] | None = None) -> str:
    try:
        return translate(key, **(params or {}))
    except Exception:
        return f"{key} | {params}" if params else key


def _log(level: int, key: str, params: Mapping[str, Any] | None = None, **log_kwargs: Any) -> None:
    message = _safe_translate(_full_key(key), params)
    logging.log(level, message, **log_kwargs)


def log_debug(key: str, params: Mapping[str, Any] | None = None, **log_kwargs: Any) -> None:
    _log(logging.DEBUG, key, params, **log_kwargs)


def log_info(key: str, params: Mapping[str, Any] | None = None, **log_kwargs: Any) -> None:
    _log(logging.INFO, key, params, **log_kwargs)


def log_warning(key: str, params: Mapping[str, Any] | None = None, **log_kwargs: Any) -> None:
    _log(logging.WARNING, key, params, **log_kwargs)


def log_error(key: str, params: Mapping[str, Any] | None = None, **log_kwargs: Any) -> None:
    _log(logging.ERROR, key, params, **log_kwargs)


def log_critical(key: str, params: Mapping[str, Any] | None = None, **log_kwargs: Any) -> None:
    _log(logging.CRITICAL, key, params, **log_kwargs)
