"""
Locale provider for MediAssist Pro.
Loads UI strings from JSON locale files under config/locale/.
All UI text must be retrieved via this module — never hardcoded.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


_LOCALE_DIR = Path(__file__).parent / "locale"
_strings: dict[str, Any] = {}
_current_locale: str = "en"


def load_locale(locale: str | None = None) -> None:
    """Load the specified locale file. Falls back to 'en' if not found."""
    global _strings, _current_locale

    locale = locale or os.getenv("MEDIASSIST_LOCALE", "en")
    locale_file = _LOCALE_DIR / f"{locale}.json"

    if not locale_file.exists():
        locale_file = _LOCALE_DIR / "en.json"
        locale = "en"

    with open(locale_file, "r", encoding="utf-8") as fh:
        _strings = json.load(fh)

    _current_locale = locale


def tr(section: str, key: str, **kwargs: Any) -> str:
    """
    Retrieve a translated string.

    Parameters
    ----------
    section : str
        Top-level section in the locale JSON (e.g. 'login', 'dashboard').
    key : str
        Key within the section (e.g. 'title', 'username_label').
    **kwargs
        Format arguments for placeholders like {name}.

    Returns
    -------
    str
        The localized string with placeholders filled in.
    """
    if not _strings:
        load_locale()

    try:
        value = _strings[section][key]
    except KeyError:
        return f"[{section}.{key}]"

    if kwargs:
        try:
            value = value.format(**kwargs)
        except KeyError:
            pass

    return value


def get_section(section: str) -> dict[str, str]:
    """Return all keys for a locale section."""
    if not _strings:
        load_locale()
    return _strings.get(section, {})


def current_locale() -> str:
    """Return the currently loaded locale code."""
    return _current_locale
