"""
DingTalk document transformer - extracts text from alidocs format.
"""

from __future__ import annotations

import re
import warnings
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


def extract_text_from_alidocs(
    obj: Any, depth: int = 0, *, max_depth: int = MAX_RECURSION_DEPTH
) -> list[str]:
    """
    Recursively extract text from alidocs checkpoint (application/x-alidocs-package).

    Args:
        obj: Parsed JSON object from checkpoint content.
        depth: Starting recursion depth, retained for existing callers.
        max_depth: Maximum included depth, relative to the document root.

    Returns:
        List of extracted text strings.

    Warns:
        RuntimeWarning: One or more subtrees were skipped at the depth limit.

    Raises:
        ValueError: max_depth is negative.
    """
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    texts: list[str] = []
    truncated = False

    def walk(node: Any, current_depth: int) -> None:
        nonlocal truncated
        if current_depth > max_depth:
            truncated = True
            return
        if isinstance(node, dict):
            # Skip explicit text fields during the generic walk to avoid duplicates.
            text_keys: set[str] = set()
            for key in ("text", "t"):
                val = node.get(key)
                if isinstance(val, str):
                    stripped = val.strip()
                    if stripped:
                        texts.append(stripped)
                        text_keys.add(key)
            for key, value in node.items():
                if key not in text_keys:
                    walk(value, current_depth + 1)
        elif isinstance(node, list):
            for value in node:
                walk(value, current_depth + 1)
        elif isinstance(node, str):
            text = node.strip()
            if len(text) > 2 and not _is_noise(text):
                texts.append(text)

    walk(obj, depth)
    if truncated:
        warnings.warn(
            f"Text extraction truncated at max_depth={max_depth}; "
            "increase max_depth to include deeper content.",
            RuntimeWarning,
            stacklevel=2,
        )
    return texts
