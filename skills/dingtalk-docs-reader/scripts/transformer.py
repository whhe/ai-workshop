"""
DingTalk document transformer - extracts text from alidocs format.
"""

from __future__ import annotations

import re
from typing import Any

_RE_UUID_STANDARD = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
_RE_HEX_ID = re.compile(r"^[0-9a-f]{20,}$", re.I)
_RE_PERCENT = re.compile(r"^\d+%$")

MAX_RECURSION_DEPTH = 25


def _is_noise(s: str) -> bool:
    """Skip UUIDs, type names, style values, bullets, IDs, and numeric strings."""
    s = s.strip()
    if len(s) < 3:
        return True
    if _RE_UUID_STANDARD.match(s) or _RE_HEX_ID.match(s):
        return True
    if s.startswith(("application/", "dingdoc")):
        return True
    if s.startswith(("rgb(", "rgba(")) or (s.startswith("#") and len(s) <= 9):
        return True
    if s in (
        "paragraph",
        "span",
        "root",
        "leaf",
        "text",
        "top",
        "solid",
        "table",
        "single",
        "hetu",
    ):
        return True
    if _RE_PERCENT.match(s):
        return True
    if s.isdigit():
        return True
    # Skip short lowercase alphanumeric strings (likely internal IDs)
    if len(s) <= 25 and s.isalnum() and s.islower():
        return True
    if len(s) == 1 and s in "●•◦▪▫\u2022\u2023\u25e6":
        return True
    return False


def extract_text_from_alidocs(obj: Any, depth: int = 0) -> list[str]:
    """
    Recursively extract text from alidocs checkpoint (application/x-alidocs-package).

    Args:
        obj: Parsed JSON object from checkpoint content.
        depth: Current recursion depth.

    Returns:
        List of extracted text strings.
    """
    if depth > MAX_RECURSION_DEPTH:
        return []
    texts: list[str] = []
    if isinstance(obj, dict):
        # Keys whose values are already captured as explicit text fields;
        # skip them during the generic obj.values() walk to avoid duplicates.
        text_keys = set()
        for key in ("text", "t"):
            val = obj.get(key)
            if isinstance(val, str):
                stripped = val.strip()
                if stripped:
                    texts.append(stripped)
                    text_keys.add(key)
        for k, v in obj.items():
            if k not in text_keys:
                texts.extend(extract_text_from_alidocs(v, depth + 1))
    elif isinstance(obj, list):
        for v in obj:
            texts.extend(extract_text_from_alidocs(v, depth + 1))
    elif isinstance(obj, str):
        s = obj.strip()
        if len(s) > 2 and not _is_noise(s):
            texts.append(s)
    return texts
