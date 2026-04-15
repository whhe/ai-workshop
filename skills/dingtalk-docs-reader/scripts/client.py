"""
DingTalk document client.

Used for getting DingTalk document list, downloading documents and attachments.
"""

from __future__ import annotations

import re
import json
import asyncio
import logging
import httpx
import random
from types import TracebackType
from typing import Any
from urllib.parse import urlparse, urlencode
from bs4 import BeautifulSoup

BASE_URL = "https://alidocs.dingtalk.com"
API_DOCUMENT_DATA = f"{BASE_URL}/api/document/data"
API_DENTRY_LIST = f"{BASE_URL}/box/api/v2/dentry/list"
API_DENTRY_INFO = f"{BASE_URL}/box/api/v2/dentry/info"
API_FILE_DOWNLOAD = f"{BASE_URL}/box/api/v2/file/download"
API_CREATE_EXPORT_JOB = f"{BASE_URL}/api/v2/files/createExportJob"
API_QUERY_EXPORT_STATUS = f"{BASE_URL}/api/v2/files/queryExportStatus"
API_OPERATION_GUARD = f"{BASE_URL}/box/api/v1/dentry/operationGuard"
API_RESOURCES_UPLOAD_INFO = f"{BASE_URL}/core/api/resources/9/upload_info"
BX_VERSION = "2.5.36"
APP_VERSION = "4.98.9"
BIZ_VERSION = "10"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/141.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 30.0
EXPORT_TIMEOUT = 120.0
MAX_RETRIES = 3
RETRY_BACKOFF = 2
PAGE_SIZE = "100"

# Pool connections like typical OpenAPI SDK clients (alibabacloud-style) to avoid
# creating a new TCP/TLS stack per request.
_HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=100)

logger = logging.getLogger(__name__)


def _http_error_detail(exc: httpx.HTTPStatusError) -> str:
    """Best-effort response body snippet for HTTP error messages."""
    try:
        return (exc.response.text or "")[:2000]
    except (AttributeError, TypeError, UnicodeDecodeError):
        return str(exc)


DOWNLOADABLE_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "txt",
    "md",
    "xlsx",
    "pptx",
    "png",
    "jpg",
    "jpeg",
}


class DingTalkAuthError(Exception):
    """DingTalk authentication error, raised when Cookie is invalid or expired."""


COMMON_HEADERS = {
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "user-agent": USER_AGENT,
}


def _extract_cookie_value(cookie: str, name: str) -> str:
    """Extract a named value from a Cookie header string."""
    match = re.search(rf"{re.escape(name)}=([^;]+)", cookie)
    return match.group(1) if match else ""


class DingTalkClient:
    """DingTalk document client."""

    def __init__(self, cookie: str, *, verify_ssl: bool = True):
        """
        Initialize DingTalk client.

        Args:
            cookie: Full cookie string from authenticated browser session.
            verify_ssl: Verify TLS certificates. Disable only for known-safe
                        internal networks; a warning is logged when False.
        """
        self.cookie = cookie
        self.xsrf_token = _extract_cookie_value(cookie, "XSRF-TOKEN")
        self._doc_atoken = _extract_cookie_value(cookie, "doc_atoken")
        self._portal_corp_id = _extract_cookie_value(cookie, "portal_corp_id")
        self._verify_ssl = verify_ssl
        self._http: httpx.AsyncClient | None = None
        if not verify_ssl:
            logger.warning("SSL verification is disabled — vulnerable to MITM attacks")

    async def _get_http(self) -> httpx.AsyncClient:
        """Lazy shared AsyncClient for connection reuse across alidocs and follow-up HTTP calls."""
        if self._http is None:
            self._http = httpx.AsyncClient(
                verify=self._verify_ssl,
                timeout=httpx.Timeout(DEFAULT_TIMEOUT),
                limits=_HTTP_LIMITS,
            )
        return self._http

    async def aclose(self) -> None:
        """Close the underlying HTTP client. Safe to call multiple times."""
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    async def __aenter__(self) -> "DingTalkClient":
        await self._get_http()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    def _get_headers(self, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            **COMMON_HEADERS,
            "cookie": self.cookie,
            "X-XSRF-TOKEN": self.xsrf_token or "",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @staticmethod
    def _strip_accept_encoding(headers: dict[str, str]) -> dict[str, str]:
        """Remove Accept-Encoding header for certain APIs."""
        return {k: v for k, v in headers.items() if k.lower() != "accept-encoding"}

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        strip_accept_encoding: bool = False,
    ) -> httpx.Response:
        """Send an HTTP request with retry on 429 and transient network errors (up to MAX_RETRIES).

        Auth redirects (301/302 to login.dingtalk.com) raise DingTalkAuthError immediately.
        Other HTTP 4xx/5xx propagate without retry.
        """
        merged_headers = self._get_headers(headers)
        if strip_accept_encoding:
            merged_headers = self._strip_accept_encoding(merged_headers)

        client = await self._get_http()
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    headers=merged_headers,
                    follow_redirects=False,
                    timeout=timeout,
                )

                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location", "")
                    if "login.dingtalk.com" in location or "oauth2" in location:
                        raise DingTalkAuthError(
                            "Cookie has expired or is invalid, "
                            "please re-login to DingTalk and get a new Cookie"
                        )
                    response = await client.get(
                        location, headers=merged_headers, follow_redirects=True, timeout=timeout
                    )

                if response.status_code == 429:
                    wait = RETRY_BACKOFF ** attempt
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()
                return response

            except (DingTalkAuthError, httpx.HTTPStatusError):
                raise
            except httpx.RequestError:
                if attempt == MAX_RETRIES:
                    raise
                wait = RETRY_BACKOFF ** attempt
                await asyncio.sleep(wait)

        # All attempts returned 429; raise the final 429 as HTTPStatusError
        response.raise_for_status()
        return response

    def extract_node_id_from_url(self, url_or_node_id: str) -> str:
        """
        Extract node_id from complete URL.

        Args:
            url_or_node_id: DingTalk document URL or node_id.

        Returns:
            Extracted node_id.
        """
        if url_or_node_id.startswith("http"):
            match = re.search(r"/i/nodes/([^?/]+)", url_or_node_id)
            if match:
                return match.group(1)
            raise ValueError(f"Cannot extract node_id from URL: {url_or_node_id}")
        return url_or_node_id

    def extract_space_id_from_url(self, space_url: str) -> str:
        """
        Extract space_id from knowledge base URL.

        Args:
            space_url: DingTalk knowledge base URL.

        Returns:
            Extracted space_id.
        """
        if space_url.startswith("http"):
            match = re.search(r"/i?/spaces/([^?/]+)", space_url)
            if match:
                return match.group(1)
            raise ValueError(f"Cannot extract space_id from URL: {space_url}")
        return space_url

    def resolve_external_link(self, node_info: dict[str, Any]) -> str | None:
        """
        Resolve a dlink/hlink node to its target node_id.

        Inspects the ``hyperlinkInfo.url`` field returned by ``get_dentry_info``.
        If the target URL points to alidocs.dingtalk.com, extracts and returns
        the target node_id so the caller can treat it as a regular node.
        Returns None for non-alidocs URLs (external sites, other platforms).

        Args:
            node_info: Response dict from ``get_dentry_info``.

        Returns:
            Target node_id if the link is an alidocs URL, None otherwise.
        """
        data = node_info.get("data", node_info)
        if not isinstance(data, dict):
            return None
        ext = (data.get("extension") or "").lower()
        if ext not in ("dlink", "hlink"):
            return None
        hyperlink = data.get("hyperlinkInfo")
        if not isinstance(hyperlink, dict):
            logger.info(
                "hyperlinkInfo not available for %s node %s (title=%s), skipping",
                ext,
                data.get("dentryUuid"),
                data.get("name"),
            )
            return None
        target_url = hyperlink.get("url") or ""
        if not target_url.startswith(BASE_URL):
            logger.info(
                "Skipping external link: %s (title=%s)",
                target_url,
                data.get("name"),
            )
            return None
        match = re.search(r"/i/nodes/([^?/]+)", target_url)
        if match:
            return match.group(1)
        logger.info(
            "Cannot extract node_id from alidocs link: %s (title=%s)",
            target_url,
            data.get("name"),
        )
        return None

    async def get_dentry_children(self, dentry_uuid: str) -> list[dict[str, Any]]:
        """
        Get children list of a directory or space (supports pagination).

        Args:
            dentry_uuid: Directory or space root UUID.

        Returns:
            List of child entries.
        """
        all_children = []
        params = {"dentryUuid": dentry_uuid, "pageSize": PAGE_SIZE}

        response = await self._request("GET", API_DENTRY_LIST, params=params)
        result = response.json()

        if not (result.get("isSuccess") and "data" in result):
            return []

        data = result["data"]
        all_children.extend(data.get("children", []))

        has_more = data.get("hasMore", False)
        load_more_id = data.get("loadMoreId")

        while has_more and load_more_id:
            more_params = {
                "dentryUuid": dentry_uuid,
                "pageSize": PAGE_SIZE,
                "loadMoreId": load_more_id,
            }
            more_response = await self._request(
                "GET", API_DENTRY_LIST, params=more_params
            )
            more_result = more_response.json()
            more_data = more_result.get("data", {})
            all_children.extend(more_data.get("children", []))
            has_more = more_data.get("hasMore", False)
            load_more_id = more_data.get("loadMoreId")

        return all_children

    async def get_dentry_info(self, dentry_uuid: str) -> dict[str, Any]:
        """
        Get detailed info of a single node.

        Args:
            dentry_uuid: Node UUID.

        Returns:
            Node info dict.
        """
        response = await self._request(
            "GET", API_DENTRY_INFO, params={"dentryUuid": dentry_uuid}
        )
        return response.json()

    async def get_root_dentry_uuid(self, space_id: str) -> str:
        """
        Get root dentry UUID of a space.

        Args:
            space_id: Space ID.

        Returns:
            Root dentry UUID.
        """
        url = f"{BASE_URL}/i/spaces/{space_id}"

        response = await self._request(
            "GET",
            url,
            params={"rnd": str(random.random())},
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            },
        )
        html = response.text

        if "login.dingtalk.com" in html or "oauth2/auth" in html:
            raise DingTalkAuthError(
                "Cookie has expired or is invalid, "
                "please re-login to DingTalk and get a new Cookie"
            )

        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", {"id": "mainsite_server_content"})

        if not script or not script.string:
            raise ValueError("Cannot find page data")

        try:
            mainsite_content = json.loads(script.string.strip())
        except json.JSONDecodeError as e:
            raise ValueError("Cannot parse page JSON data") from e

        if "spaceRootDentry" in mainsite_content:
            data = mainsite_content["spaceRootDentry"].get("data", {})
            dentry_uuid = data.get("dentryUuid")
            if dentry_uuid:
                return dentry_uuid

        props = mainsite_content.get("props", {}).get("pageProps", {})
        space_root = props.get("spaceRootDentry", {}).get("data", {})
        if space_root.get("dentryUuid"):
            return space_root["dentryUuid"]

        raise ValueError("Cannot find root dentry UUID")

    async def get_document_data(self, node_id: str, dentry_key: str | None = None) -> dict[str, Any]:
        """
        Get document content data for native adoc documents.

        Args:
            node_id: Document node ID.
            dentry_key: Document dentry key (optional, will fetch if not provided).

        Returns:
            Document data including checkpoint content and access token.
        """
        if not dentry_key:
            info = await self.get_dentry_info(node_id)
            dentry_key = info.get("data", {}).get("dentryKey")

        headers = self._get_headers({
            "A-DENTRY-KEY": dentry_key,
            "Referer": f"{BASE_URL}/i/nodes/{node_id}",
        })

        response = await self._request(
            "POST",
            API_DOCUMENT_DATA,
            json_data={"fetchBody": True},
            headers=headers,
            strip_accept_encoding=True,
        )
        return response.json()

    async def _download_bytes(self, url: str, timeout: float = EXPORT_TIMEOUT) -> bytes:
        """Download binary content from *url* with transient-error retry."""
        client = await self._get_http()
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = await client.get(url, follow_redirects=True, timeout=timeout)
                resp.raise_for_status()
                return resp.content
            except httpx.HTTPStatusError:
                raise
            except httpx.RequestError:
                if attempt == MAX_RETRIES:
                    raise
                await asyncio.sleep(RETRY_BACKOFF ** attempt)
        raise RuntimeError("unreachable: all retry paths exit via return or raise")

    async def download_file(self, node_id: str, extension: str | None = None) -> bytes:
        """
        Download file content for downloadable types (pdf, docx, etc.).

        Args:
            node_id: Document node ID.
            extension: Known file extension. When provided, skips the extra
                       ``get_dentry_info`` call used for validation.

        Returns:
            File content as bytes.

        Raises:
            ValueError: If the node extension is not in DOWNLOADABLE_EXTENSIONS.
        """
        if extension is None:
            info = await self.get_dentry_info(node_id)
            extension = info.get("data", {}).get("extension", "")
        if extension and extension not in DOWNLOADABLE_EXTENSIONS:
            raise ValueError(
                f"Extension '{extension}' is not downloadable. "
                f"Supported: {', '.join(sorted(DOWNLOADABLE_EXTENSIONS))}"
            )

        response = await self._request(
            "GET", API_FILE_DOWNLOAD, params={"dentryUuid": node_id}
        )
        result = response.json()

        if not result.get("isSuccess"):
            raise ValueError(f"Failed to get download URL: {result.get('message')}")

        pre_sign_urls = (
            result.get("data", {})
            .get("ossUrlPreSignatureInfo", {})
            .get("preSignUrls", [])
        )

        if not pre_sign_urls:
            raise ValueError("No download URL available")

        return await self._download_bytes(pre_sign_urls[0])

    def _export_referer(self, doc_key: str, dentry_key: str, workspace_id: str) -> str:
        """Referer for editor note/preview export chain (matches browser DevTools)."""
        q = {
            "dt_editor_toolbar": "true",
            "biz_ver": BIZ_VERSION,
            "docId": doc_key,
            "docType": "doc",
            "dontjump": "true",
            "utm_scene": "team_space",
            "platform": "pc",
            "mainsiteOrigin": "mainsite",
            "showCommentPanel": "false",
            "from": "dingnote",
            "dd_user_keyboard": "false",
            "dd_full_screen": "true",
            "workspaceId": workspace_id,
            "docKey": doc_key,
            "dentryKey": dentry_key,
            "utm_source": "portal",
            "utm_medium": "portal_space_file_tree",
            "channelId": "wiki-doc-iframe",
            "disableGuide": "false",
            "scene": "cloudSpace",
        }
        return f"{BASE_URL}/note/preview?{urlencode(q)}"

    @staticmethod
    def _export_referer_nodes(node_id: str) -> str:
        """Alternate Referer when note/preview export is rejected (e.g. 52600007)."""
        return f"{BASE_URL}/i/nodes/{node_id}"

    def _require_doc_atoken(self) -> None:
        if not self._doc_atoken:
            raise DingTalkAuthError(
                "Cookie missing doc_atoken; PDF export requires an authenticated alidocs session"
            )

    def _base_export_headers(self, referer: str) -> dict[str, str]:
        """Common headers shared by all export-chain endpoints."""
        self._require_doc_atoken()
        return {
            "accept": "application/json, text/plain, */*",
            "origin": BASE_URL,
            "referer": referer,
            "bx-v": BX_VERSION,
            "a-token": self._doc_atoken,
        }

    def _operation_guard_headers(
        self,
        doc_key: str,
        dentry_key: str,
        workspace_id: str,
    ) -> dict[str, str]:
        ref = self._export_referer(doc_key, dentry_key, workspace_id)
        h = self._base_export_headers(ref)
        if self._portal_corp_id:
            h["corp-id"] = self._portal_corp_id
        return h

    def _upload_info_headers(
        self,
        doc_key: str,
        dentry_key: str,
        workspace_id: str,
    ) -> dict[str, str]:
        ref = self._export_referer(doc_key, dentry_key, workspace_id)
        h = self._base_export_headers(ref)
        h["a-doc-key"] = doc_key
        h["a-host-doc-key"] = ""
        return h

    def _export_doc_headers(
        self,
        dentry_key: str,
        doc_key: str,
        workspace_id: str,
        referer: str | None = None,
    ) -> dict[str, str]:
        ref = referer if referer is not None else self._export_referer(
            doc_key, dentry_key, workspace_id
        )
        h = self._base_export_headers(ref)
        h["a-doc-key"] = doc_key
        h["a-dentry-key"] = dentry_key
        return h

    def _pdf_export_options_string(
        self,
        doc_key: str,
        doc_open_token: str,
        nick: str,
        title: str,
        ctx_version: int,
    ) -> str:
        opts: dict[str, Any] = {
            "openToken": {
                "docOpenToken": doc_open_token,
                "corpId": self._portal_corp_id or "",
                "docKey": doc_key,
            },
            "isNew": True,
            "customConfig": {
                "content": "ONLYCONTENT",
                "mode": "PORTRAIT",
                "watermark": "CLOSE",
                "nick": nick,
                "corpName": "",
                "link": "",
                "enableTableAutofitWidth": False,
            },
            "fileName": title,
            "showDocTitle": True,
            "ctxVersion": ctx_version,
            "printStyle": {
                "backgroundColor": "var(--we_bg_default_color, rgba(255, 255, 255, 1))",
            },
            "version": 1,
            "appVersion": APP_VERSION,
            "exportType": "pdf",
            "corpId": self._portal_corp_id or "",
            "lang": "zh-CN",
        }
        return json.dumps(opts, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _strip_adoc_extension(name: str) -> str:
        """Remove a trailing .adoc suffix (case-insensitive)."""
        s = name.strip()
        if s.lower().endswith(".adoc"):
            return s[: -len(".adoc")]
        return s

    @staticmethod
    def _checkpoint_ctx_version(checkpoint: dict[str, Any]) -> int:
        v = checkpoint.get("baseVersion", 0)
        if v is None:
            return 0
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _parse_upload_info_response(
        payload: dict[str, Any],
    ) -> tuple[str, str, dict[str, str]]:
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            raise ValueError("upload_info: unexpected response shape")
        storage_path = (
            data.get("storagePath")
            or data.get("storage_path")
            or data.get("path")
            or data.get("objectKey")
            or ""
        )
        put_url = (
            data.get("uploadUrl")
            or data.get("upload_url")
            or data.get("putUrl")
            or data.get("externalUrl")
            or ""
        )
        put_headers: dict[str, str] = {}
        sig = data.get("headerSignatureInfo") or data.get("headerSignature") or {}
        if isinstance(sig, dict):
            if not put_url:
                urls = sig.get("resourceUrls") or sig.get("resource_urls") or []
                if isinstance(urls, list) and urls:
                    put_url = urls[0]
            ph = sig.get("headers")
            if isinstance(ph, dict):
                put_headers = ph
        if not put_url:
            raise ValueError(f"upload_info: could not resolve upload URL: {payload}")
        return str(storage_path), put_url, put_headers

    @staticmethod
    def _storage_path_from_put_url(put_url: str) -> str:
        path = urlparse(put_url).path.lstrip("/")
        if path.startswith("tmp_cp/"):
            return path
        idx = path.find("tmp_cp/")
        if idx >= 0:
            return path[idx:]
        raise ValueError(f"Cannot extract storagePath from upload URL: {put_url[:120]}")

    async def _operation_guard_download(
        self,
        node_id: str,
        doc_key: str,
        dentry_key: str,
        workspace_id: str,
    ) -> None:
        h = self._operation_guard_headers(doc_key, dentry_key, workspace_id)
        body = {
            "operationType": "DOWNLOAD",
            "resourceType": 0,
            "resourceIdList": [node_id],
        }
        resp = await self._request(
            "POST",
            API_OPERATION_GUARD,
            json_data=body,
            headers={**h, "content-type": "application/json"},
            timeout=60.0,
            strip_accept_encoding=True,
        )
        result = resp.json()
        if result.get("isSuccess") is False:
            raise ValueError(f"operationGuard failed: {result}")

    async def _upload_checkpoint_to_oss_and_storage_path(
        self,
        doc_key: str,
        dentry_key: str,
        workspace_id: str,
        oss_put_bytes: bytes,
    ) -> str:
        body = {
            "size": len(oss_put_bytes),
            "resourceName": doc_key,
            "contentType": "",
        }
        h = self._upload_info_headers(doc_key, dentry_key, workspace_id)
        resp = await self._request(
            "POST",
            API_RESOURCES_UPLOAD_INFO,
            json_data=body,
            headers={**h, "content-type": "application/json"},
            timeout=EXPORT_TIMEOUT,
            strip_accept_encoding=True,
        )
        result = resp.json()
        if result.get("isSuccess") is False:
            raise ValueError(f"upload_info failed: {result}")
        sp, put_url, put_headers = self._parse_upload_info_response(result)
        req_headers = dict(put_headers) if put_headers else {}
        client = await self._get_http()
        r = await client.put(put_url, content=oss_put_bytes, headers=req_headers, timeout=EXPORT_TIMEOUT)
        r.raise_for_status()
        if not sp:
            sp = self._storage_path_from_put_url(put_url)
        return sp

    @staticmethod
    def _is_retryable_create_export_error(exc: Exception) -> bool:
        if isinstance(exc, httpx.HTTPStatusError):
            code = exc.response.status_code
            if code == 400:
                return True
            if 500 <= code < 600:
                return True
            return False
        err_s = str(exc)
        if "52600007" in err_s:
            return True
        return False

    async def _create_pdf_export_job_once(
        self,
        dentry_key: str,
        doc_key: str,
        workspace_id: str,
        body: dict[str, Any],
        referer: str | None,
    ) -> dict[str, Any]:
        h = self._export_doc_headers(dentry_key, doc_key, workspace_id, referer=referer)
        response = await self._request(
            "POST",
            API_CREATE_EXPORT_JOB,
            json_data=body,
            headers={
                **h,
                "content-type": "application/json",
                "source_doc_app": "doc",
                "utm_medium": "portal_space_file_tree",
                "utm_source": "portal",
            },
            timeout=EXPORT_TIMEOUT,
            strip_accept_encoding=False,
        )
        result = response.json()
        if not result.get("isSuccess"):
            code = result.get("code") or result.get("errorCode")
            msg = result.get("message", result)
            raise ValueError(f"createExportJob failed: {msg} (code={code})")
        data = result.get("data") or {}
        job_id = data.get("jobId")
        if not job_id:
            raise ValueError(f"createExportJob missing jobId: {result}")
        return {
            "jobId": job_id,
            "url": data.get("url") or "",
            "done": bool(data.get("done")),
        }

    async def _create_pdf_export_job(
        self,
        dentry_key: str,
        doc_key: str,
        storage_path: str,
        workspace_id: str,
        node_id: str,
    ) -> dict[str, Any]:
        strategies: list[tuple[dict[str, Any], str | None]] = [
            ({"scene": "normal", "storagePath": storage_path}, None),
            (
                {"scene": "normal", "storagePath": storage_path},
                self._export_referer_nodes(node_id),
            ),
        ]
        for i, (body, ref) in enumerate(strategies):
            try:
                return await self._create_pdf_export_job_once(
                    dentry_key, doc_key, workspace_id, body, ref
                )
            except (ValueError, httpx.HTTPStatusError) as e:
                if i < len(strategies) - 1 and self._is_retryable_create_export_error(e):
                    logger.warning(
                        "createExportJob attempt %s/%s failed, retrying with alternate referer: %s",
                        i + 1,
                        len(strategies),
                        e,
                    )
                    continue
                raise

    async def _poll_pdf_export_job(
        self,
        job_id: str,
        doc_key: str,
        dentry_key: str,
        workspace_id: str,
        poll_interval: float,
        max_wait: float,
    ) -> str | None:
        params = {"jobId": job_id}
        h = self._export_doc_headers(dentry_key, doc_key, workspace_id)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + max_wait
        while loop.time() < deadline:
            await asyncio.sleep(poll_interval)
            try:
                response = await self._request(
                    "GET",
                    API_QUERY_EXPORT_STATUS,
                    params=params,
                    headers=h,
                    timeout=60.0,
                    strip_accept_encoding=False,
                )
            except httpx.HTTPStatusError as e:
                detail = _http_error_detail(e)
                raise ValueError(
                    f"queryExportStatus HTTP {e.response.status_code}: {detail or e}"
                ) from e
            payload = response.json()
            data = payload.get("data") or {}
            if data.get("done"):
                url = data.get("url")
                return str(url) if url else None
        raise TimeoutError(f"PDF export polling timed out after {max_wait}s")

    async def export_to_pdf(
        self,
        node_id: str,
        filename: str | None = None,
        poll_interval: float = 2.0,
        max_wait: float = 120.0,
    ) -> bytes:
        """
        Export native adoc document to PDF.

        Mirrors the browser: operationGuard (DOWNLOAD) -> upload_info + OSS PUT
        {{asl, optionsString}} -> createExportJob(scene=normal, storagePath) -> poll -> download.
        The createExportJob body must use storagePath from upload_info, not dentryUuid/workspaceId.

        Args:
            node_id: Document node ID.
            filename: Output filename (optional).
            poll_interval: Polling interval for export status.
            max_wait: Maximum wait time for export completion.

        Returns:
            PDF content as bytes.
        """
        info = await self.get_dentry_info(node_id)
        data = info.get("data", info)
        if not isinstance(data, dict):
            data = {}
        dentry_key = data.get("dentryKey")
        doc_key = data.get("docKey")
        workspace_id = str(data.get("spaceId") or data.get("workspaceId") or "")

        if not dentry_key or not doc_key:
            raise ValueError("Cannot resolve dentryKey/docKey for PDF export")
        if not workspace_id:
            raise ValueError("Cannot resolve spaceId for PDF export")

        doc_data = await self.get_document_data(node_id, dentry_key)
        doc_content = doc_data.get("data", {})
        checkpoint = doc_content.get("documentContent", {}).get("checkpoint", {})
        content_str = checkpoint.get("content")
        if not isinstance(content_str, str):
            raise ValueError("checkpoint.content must be a string for PDF export")
        access_token = doc_content.get("accessToken") or self._doc_atoken
        ctx_version = self._checkpoint_ctx_version(checkpoint)
        user_nick = doc_content.get("userInfo", {}).get("user", {}).get("nick", "")

        raw_title = filename or data.get("name", "document")
        title = self._strip_adoc_extension(raw_title)

        options_string = self._pdf_export_options_string(
            doc_key=doc_key,
            doc_open_token=access_token,
            nick=user_nick,
            title=title,
            ctx_version=ctx_version,
        )
        oss_put_bytes = json.dumps(
            {"asl": content_str, "optionsString": options_string},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        await self._operation_guard_download(node_id, doc_key, dentry_key, workspace_id)
        storage_path = await self._upload_checkpoint_to_oss_and_storage_path(
            doc_key, dentry_key, workspace_id, oss_put_bytes
        )
        job = await self._create_pdf_export_job(
            dentry_key=dentry_key,
            doc_key=doc_key,
            storage_path=storage_path,
            workspace_id=workspace_id,
            node_id=node_id,
        )
        download_url = job.get("url")
        if not job.get("done"):
            polled_url = await self._poll_pdf_export_job(
                job_id=job["jobId"],
                doc_key=doc_key,
                dentry_key=dentry_key,
                workspace_id=workspace_id,
                poll_interval=poll_interval,
                max_wait=max_wait,
            )
            download_url = polled_url or download_url
        if not download_url:
            raise ValueError(f"createExportJob did not return a download URL: {job}")

        return await self._download_bytes(download_url)
