"""
DingTalk document transformer - extracts text from alidocs format.
"""

from typing import Any, List


def _is_noise(s: str) -> bool:
    """Skip UUIDs, type names, style values, bullets, IDs."""
    s = s.strip()
    if len(s) < 3:
        return True
    if (
        s.startswith("00000000-")
        or s.startswith("application/")
        or s.startswith("rgb(")
        or s.startswith("dingdoc")
    ):
        return True
    if s.startswith("rgba(") or (s.startswith("#") and len(s) <= 9):
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
    ):
        return True
    # Skip alphanumeric IDs (e.g. mib1ppo8vr24wi3wnx)
    if s == "100%" or (len(s) <= 25 and s.isalnum() and s.islower()):
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