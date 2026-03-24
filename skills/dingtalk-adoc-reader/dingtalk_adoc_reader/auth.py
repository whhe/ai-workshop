"""
DingTalk QR code login via Playwright.

Flow:
1. Open alidocs.dingtalk.com
2. Click the "登录" (Login) button → opens a new tab to login.dingtalk.com
3. On the login page, capture the QR code image
4. User scans with DingTalk App → login page redirects → extract cookies
"""

import asyncio
import base64
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class LoginStatus(str, Enum):
    """Login session status."""
    PENDING = "pending"
    QR_READY = "qr_ready"
    SCANNED = "scanned"
    SUCCESS = "success"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class LoginSession:
    """Login session data."""
    session_id: str
    status: LoginStatus = LoginStatus.PENDING
    qr_image_base64: Optional[str] = None
    cookie: Optional[str] = None
    error: Optional[str] = None
    _task: Optional[asyncio.Task] = field(default=None, repr=False)


_sessions: Dict[str, LoginSession] = {}

LOGIN_TIMEOUT_SECONDS = 180
QR_POLL_INTERVAL = 2.0


def get_session(session_id: str) -> Optional[LoginSession]:
    """Get login session by ID."""
    return _sessions.get(session_id)


def cleanup_session(session_id: str) -> None:
    """Remove login session and cancel background task."""
    session = _sessions.pop(session_id, None)
    if session and session._task and not session._task.done():
        session._task.cancel()


async def start_qr_login(target_url: str = "https://alidocs.dingtalk.com") -> LoginSession:
    """
    Start a new QR code login session.

    Returns immediately with session_id; the QR code capture and login
    polling run in the background.

    Args:
        target_url: Target URL to open after login.

    Returns:
        LoginSession with session_id for polling.
    """
    session_id = uuid.uuid4().hex[:12]
    session = LoginSession(session_id=session_id)
    _sessions[session_id] = session

    task = asyncio.create_task(_run_login_flow(session, target_url))
    session._task = task
    return session


async def _run_login_flow(session: LoginSession, target_url: str) -> None:
    """Background task: launch browser, trigger login, capture QR, wait."""
    browser = None
    playwright_obj = None
    try:
        from playwright.async_api import async_playwright

        playwright_obj = await async_playwright().start()
        browser = await playwright_obj.chromium.launch(headless=True)
        from .client import USER_AGENT

        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        # Navigate to alidocs homepage
        await page.goto(
            "https://alidocs.dingtalk.com",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await page.wait_for_timeout(3000)

        # Click the "登录" button which opens a new tab
        login_page = await _click_login_button(context, page)
        if not login_page:
            session.status = LoginStatus.FAILED
            session.error = "Cannot find or click the login button"
            return

        login_page_url = login_page.url

        # Baseline cookies to distinguish pre-existing from post-login ones
        initial_cookies = await context.cookies()
        initial_cookie_names = {c["name"] for c in initial_cookies}

        # Capture the QR code from the login page
        qr_b64 = await _capture_qr_code(login_page, session.session_id)
        if not qr_b64:
            debug_img = await login_page.screenshot()
            session.qr_image_base64 = base64.b64encode(debug_img).decode()
            session.status = LoginStatus.FAILED
            session.error = "Cannot find QR code on the login page"
            return

        session.qr_image_base64 = qr_b64
        session.status = LoginStatus.QR_READY

        # Wait for user to scan and complete login
        cookie_str = await _wait_for_login(
            context, login_page, session, login_page_url, initial_cookie_names
        )
        if cookie_str:
            session.cookie = cookie_str
            session.status = LoginStatus.SUCCESS
        elif session.status != LoginStatus.FAILED:
            session.status = LoginStatus.EXPIRED
            session.error = "QR code expired or login timed out"

    except asyncio.CancelledError:
        session.status = LoginStatus.FAILED
        session.error = "Session cancelled"
    except Exception as e:
        session.status = LoginStatus.FAILED
        session.error = str(e)
    finally:
        if browser:
            await browser.close()
        if playwright_obj:
            await playwright_obj.stop()


async def _click_login_button(context, page):
    """Click the login button and return the newly opened login page."""
    try:
        async with context.expect_page(timeout=15000) as new_page_info:
            btn = await page.query_selector("text=登录")
            if not btn:
                btn = await page.query_selector(
                    'a:has-text("登录"), button:has-text("登录")'
                )
            if not btn:
                return None
            await btn.click()

        login_page = await new_page_info.value
        await login_page.wait_for_load_state("domcontentloaded")
        await login_page.wait_for_timeout(3000)
        return login_page
    except Exception:
        return None


async def _capture_qr_code(page, session_id: str) -> Optional[str]:
    """Find and screenshot the QR code on the DingTalk login page."""
    # Strategy 1: DingTalk login page specific selectors
    dt_selectors = [
        "div.module-qrcode-code",
        "div.edu-qrCode-code",
        "div.factor-onlineDevice-code",
        "div.module-qrcode-area",
        "div.edu-qrCode-area",
    ]
    for sel in dt_selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=2000)
            if el:
                box = await el.bounding_box()
                if box and box["width"] > 100 and box["height"] > 100:
                    img_bytes = await el.screenshot()
                    return base64.b64encode(img_bytes).decode()
        except Exception:
            continue

    # Strategy 2: Generic QR code selectors
    generic_selectors = [
        "div[class*='qrcode'] img",
        "div[class*='QRCode'] img",
        "img[class*='qrcode']",
    ]
    for sel in generic_selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=2000)
            if el:
                box = await el.bounding_box()
                if box and box["width"] > 80 and box["height"] > 80:
                    img_bytes = await el.screenshot()
                    return base64.b64encode(img_bytes).decode()
        except Exception:
            continue

    # Strategy 3: Find square images that look like QR codes (150-250px)
    try:
        images = await page.query_selector_all("img")
        for img in images:
            src = await img.get_attribute("src") or ""
            box = await img.bounding_box()
            if not box:
                continue
            w, h = box["width"], box["height"]
            if 140 < w < 260 and 140 < h < 260 and 0.85 < w / h < 1.15:
                if any(skip in src.lower() for skip in ["logo", "icon", "avatar", "banner"]):
                    continue
                img_bytes = await img.screenshot()
                return base64.b64encode(img_bytes).decode()
    except Exception:
        pass

    # Strategy 4: Canvas-based QR code
    try:
        canvases = await page.query_selector_all("canvas")
        for canvas in canvases:
            box = await canvas.bounding_box()
            if box and 100 < box["width"] < 300 and 100 < box["height"] < 300:
                img_bytes = await canvas.screenshot()
                return base64.b64encode(img_bytes).decode()
    except Exception:
        pass

    return None


def _has_new_auth_cookies(cookies: list, initial_names: set) -> bool:
    """Check if new auth cookies appeared after login."""
    current_names = {c["name"] for c in cookies}
    new_names = current_names - initial_names
    # After DingTalk login, cookies like atoken, nick, etc. are added
    auth_indicators = {"atoken", "atknv2", "nick", "ssotoken", "uid"}
    has_auth_cookie = bool(new_names & auth_indicators)
    many_new = len(new_names) >= 5
    return has_auth_cookie or many_new


async def _wait_for_login(
    context,
    login_page,
    session: LoginSession,
    login_page_url: str,
    initial_cookie_names: set,
) -> Optional[str]:
    """Poll until login succeeds."""
    elapsed = 0.0
    while elapsed < LOGIN_TIMEOUT_SECONDS:
        await asyncio.sleep(QR_POLL_INTERVAL)
        elapsed += QR_POLL_INTERVAL

        try:
            cookies = await context.cookies()
            new_auth = _has_new_auth_cookies(cookies, initial_cookie_names)

            # Check if login page URL changed (redirect after login)
            login_closed = login_page.is_closed()
            url_changed = login_closed or login_page.url != login_page_url

            # Primary signal: URL changed + new auth cookies
            if url_changed and new_auth:
                await asyncio.sleep(2)
                cookies = await context.cookies()
                parts = [f"{c['name']}={c['value']}" for c in cookies]
                return "; ".join(parts)

            # Secondary: new auth cookies even without URL change
            if new_auth and not url_changed:
                await asyncio.sleep(3)
                cookies = await context.cookies()
                if _has_new_auth_cookies(cookies, initial_cookie_names):
                    parts = [f"{c['name']}={c['value']}" for c in cookies]
                    return "; ".join(parts)

            # Check if the original page navigated to alidocs content
            if not login_closed:
                for p in context.pages:
                    if p == login_page:
                        continue
                    p_url = p.url
                    if "alidocs.dingtalk.com/i/" in p_url:
                        await asyncio.sleep(2)
                        cookies = await context.cookies()
                        parts = [f"{c['name']}={c['value']}" for c in cookies]
                        return "; ".join(parts)

        except Exception:
            continue

    return None