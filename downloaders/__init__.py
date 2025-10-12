"""Downloader package exposing per-source implementations and a factory helper."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional, Type, cast

from dotenv import load_dotenv

from .bea import BEADownloader
from .bls import BLSDownloader
from .common import DataDownloader
from .fred import FREDDownloader
from .te import TEDownloader
from .yf import YFDownloader
from .ism import ISMDownloader
from .fw import CMEfedWatchDownloader

__all__ = [
    "DownloaderFactory",
    "DataDownloader",
    "BEADownloader",
    "BLSDownloader",
    "FREDDownloader",
    "TEDownloader",
    "YFDownloader",
    "ISMDownloader",
    "CMEfedWatchDownloader"
]

DownloaderType = Type[DataDownloader]
_DOWNLOADERS: Dict[str, DownloaderType] = {
    "bea": BEADownloader,
    "yf": YFDownloader,
    "fred": FREDDownloader,
    "bls": BLSDownloader,
    "te": TEDownloader,
    "ism": ISMDownloader,
    "fw": CMEfedWatchDownloader
}


class DownloaderFactory:
    """Factory for creating concrete downloader instances by source name."""
    @staticmethod
    def _get_api_key(source: str) -> str:
        load_dotenv()
        key = os.environ.get(source)
        if not key:
            logging.warning("API key for %s not found in environment", source)
            return ""
        return key

    @classmethod
    def create_downloader(
        cls,
        source: str,
        json_data: Dict[str, Any],
        request_year: int,
    ) -> Optional[DataDownloader]:
        source_key = source.lower()
        downloader_cls = _DOWNLOADERS.get(source_key)
        if downloader_cls is None:
            logging.error("Unsupported data source requested: %s", source)
            return None

        config = json_data.get(source_key)
        if not isinstance(config, dict):
            logging.error("DownloaderFactory: missing configuration for source '%s'", source)
            return None

        api_key = cls._get_api_key(source_key)
        cfg = cast(Dict[str, Dict[str, Any]], config)
        try:
            return downloader_cls(cfg, api_key, request_year)  # type: ignore[call-arg]
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to create downloader for %s: %s", source, exc)
            return None

    @classmethod
    def available_sources(cls) -> Dict[str, DownloaderType]:
        """Return a mapping of the sources supported by the factory."""

        return dict(_DOWNLOADERS)
