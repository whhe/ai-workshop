"""
DingTalk document transformer - extracts text from alidocs format.
"""

import re
from typing import Any, List

_RE_UUID_STANDARD = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
_RE_HEX_ID = re.compile(r"^[0-9a-f]{20,}$", re.I)
_RE_PERCENT = re.compile(r"^\d+%$")


def _is_noise(s: str) -> bool:
    """Skip UUIDs, type names, style values, bullets, IDs, and numeric strings."""
    s = s.strip()
    if len(s) < 3:
        return True
    if _RE_UUID_STANDARD.match(s) or _RE_HEX_ID.match(s):
        return True
    if s.startswith("application/") or s.startswith("dingdoc"):
        return True
    if s.startswith("rgb(") or s.startswith("rgba(") or (s.startswith("#") and len(s) <= 9):
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


def extract_text_from_alidocs(obj: Any, depth: int = 0) -> List[str]:
    """
    Recursively extract text from alidocs checkpoint (application/x-alidocs-package).

    Args:
        obj: Parsed JSON object from checkpoint content.
        depth: Current recursion depth.

    Returns:
        List of extracted text strings.
    """
    if depth > 25:
        return []
    texts = []
    if isinstance(obj, dict):
        if "text" in obj and isinstance(obj["text"], str) and obj["text"].strip():
            texts.append(obj["text"].strip())
        if "t" in obj and isinstance(obj["t"], str) and obj["t"].strip():
            texts.append(obj["t"].strip())
        for v in obj.values():
            texts.extend(extract_text_from_alidocs(v, depth + 1))
    elif isinstance(obj, list):
        for v in obj:
            texts.extend(extract_text_from_alidocs(v, depth + 1))
    elif isinstance(obj, str) and obj.strip() and not _is_noise(obj.strip()):
        # Direct string in nested structure
        if len(obj.strip()) > 2:
            texts.append(obj.strip())
    return texts