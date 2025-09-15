"""Centralized async logging configuration using QueueHandler/QueueListener.
Provides start_logging(process_tag) and stop_logging().
- Per-level daily-rotating file handlers (UTF-8, backup 14 days)
- Optional process_tag to differentiate GUI/worker etc.
- Console output at INFO+ level
"""
from __future__ import annotations

import logging
import os
import queue
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from typing import Optional, List, Dict

_listener: Optional[QueueListener] = None
_queue: Optional[queue.Queue] = None
_configured: bool = False


class LevelFilter(logging.Filter):
    """Allow only a specific level to pass."""
    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        return record.levelno == self.level


def _make_timed_handler(filename: str, level: int, when: str = "midnight", backupCount: int = 14) -> TimedRotatingFileHandler:
    handler = TimedRotatingFileHandler(
        filename,
        when=when,
        interval=1,
        backupCount=backupCount,
        encoding="utf-8",
        delay=True,
    )
    handler.setLevel(logging.DEBUG)  # accept all, filtered by LevelFilter
    handler.addFilter(LevelFilter(level))
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s [%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    return handler


def start_logging(process_tag: str = "", lib_levels: Optional[Dict[str, int]] = None) -> None:
    """Initialize async logging with a QueueListener.

    Args:
        process_tag: Optional tag appended to filenames, e.g. "gui", "worker".
    """
    global _listener, _queue, _configured

    if _configured:
        return

    os.makedirs("logs", exist_ok=True)

    # Build handlers that will be used by the QueueListener
    suffix = f"_{process_tag}" if process_tag else ""
    handlers: List[logging.Handler] = [
        _make_timed_handler(f"logs/debug{suffix}.log", logging.DEBUG),
        _make_timed_handler(f"logs/info{suffix}.log", logging.INFO),
        _make_timed_handler(f"logs/warning{suffix}.log", logging.WARNING),
        _make_timed_handler(f"logs/error{suffix}.log", logging.ERROR),
    ]

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%H:%M:%S"))
    handlers.append(console)

    # Create a queue and listener
    _queue = queue.Queue(-1)  # type: ignore[assignment]
    _listener = QueueListener(_queue, *handlers, respect_handler_level=True)

    # Configure root logger to use QueueHandler
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    for h in list(root.handlers):
        try:
            root.removeHandler(h)
            h.close()
        except Exception:
            pass

    root.addHandler(QueueHandler(_queue))

    _listener.start()
    _configured = True

    # Configure common third-party libraries log levels to reduce noise.
    default_lib_levels: Dict[str, int] = {
        "urllib3": logging.WARNING,
        "requests": logging.WARNING,
        "selenium": logging.INFO,
        "yfinance": logging.INFO,
        "matplotlib": logging.WARNING,
        "pyqtgraph": logging.INFO,
    }
    for name, level in (lib_levels or default_lib_levels).items():
        try:
            logging.getLogger(name).setLevel(level)
        except Exception:
            pass


def stop_logging() -> None:
    global _listener, _configured
    if _listener is not None:
        try:
            _listener.stop()
        finally:
            _listener = None
            _configured = False
