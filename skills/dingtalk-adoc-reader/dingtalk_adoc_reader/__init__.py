"""DingTalk adoc document access package."""

from .auth import start_qr_login, get_session, cleanup_session, LoginStatus, LoginSession
from .client import DingTalkClient, DingTalkAuthError, USER_AGENT
from .transformer import extract_text_from_alidocs

__all__ = [
    "DingTalkClient",
    "DingTalkAuthError",
    "USER_AGENT",
    "start_qr_login",
    "get_session",
    "cleanup_session",
    "LoginStatus",
    "LoginSession",
    "extract_text_from_alidocs",
]