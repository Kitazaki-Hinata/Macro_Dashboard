from __future__ import annotations

from pathlib import Path
from typing import Iterable

import i18n

_LOCALE_DIR = Path(__file__).resolve().parent / "locales"
_AVAILABLE_LOCALES: tuple[str, ...] = ("zh", "en")
_DEFAULT_LOCALE = "zh"


def _ensure_locale_path() -> None:
    _LOCALE_DIR.mkdir(parents=True, exist_ok=True)


def configure() -> None:
    _ensure_locale_path()
    current_locale = i18n.get("locale")
    i18n.load_path.clear()
    i18n.load_path.append(str(_LOCALE_DIR))
    i18n.set("fallback", _DEFAULT_LOCALE)
    i18n.set("available_locales", list(_AVAILABLE_LOCALES))
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("file_format", "yml")
    i18n.set("enable_memoization", True)
    i18n.set("use_locale_dirs", False)
    if not isinstance(current_locale, str) or current_locale not in _AVAILABLE_LOCALES:
        current_locale = _DEFAULT_LOCALE
    i18n.set("locale", current_locale)


def set_locale(locale: str) -> str:
    if locale not in _AVAILABLE_LOCALES:
        locale = _DEFAULT_LOCALE
    configure()
    i18n.set("locale", locale)
    return locale


def get_locale() -> str:
    configure()
    return i18n.get("locale") or _DEFAULT_LOCALE


def available_locales() -> Iterable[str]:
    return list(_AVAILABLE_LOCALES)


def translate(key: str, **kwargs) -> str:
    configure()
    return i18n.t(key, **kwargs)


def format_language_name(locale: str) -> str:
    names = {"zh": "中文", "en": "English"}
    return names.get(locale, locale)


# Ensure configuration is applied as soon as the module is imported.
configure()
