"""
DingTalk document client.

Used for getting DingTalk document list, downloading documents and attachments.
"""

import re
import json
import asyncio
import httpx
import random
from typing import List, Dict, Any, Optional
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

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/141.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_BACKOFF = 2

# Pool connections like typical OpenAPI SDK clients (alibabacloud-style) to avoid
# creating a new TCP/TLS stack per request.
_HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=100)

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


def _extract_xsrf_token(cookie: str) -> str:
    """Extract XSRF-TOKEN from Cookie string."""
    match = re.search(r"XSRF-TOKEN=([^;]+)", cookie)
    return match.group(1) if match else ""


def _extract_doc_atoken(cookie: str) -> str:
    """Extract doc_atoken from Cookie (required for editor / export APIs)."""
    match = re.search(r"doc_atoken=([^;]+)", cookie)
    return match.group(1) if match else ""


def _extract_portal_corp_id(cookie: str) -> str:
    """Extract portal_corp_id from Cookie."""
    match = re.search(r"portal_corp_id=([^;]+)", cookie)
    return match.group(1) if match else ""


class DingTalkClient:
    """DingTalk document client."""

    def __init__(self, cookie: str):
        """
        Initialize DingTalk client.

        Args:
            cookie: Full cookie string from authenticated browser session.
        """
        self.cookie = cookie
        self.xsrf_token = _extract_xsrf_token(cookie)
        self._doc_atoken = _extract_doc_atoken(cookie)
        self._portal_corp_id = _extract_portal_corp_id(cookie)
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        """Lazy shared AsyncClient for connection reuse across alidocs and follow-up HTTP calls."""
        if self._http is None:
            self._http = httpx.AsyncClient(
                verify=False,
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

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def _get_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            **COMMON_HEADERS,
            "cookie": self.cookie,
        }
        extra_keys_lower = set()
        if extra_headers:
            extra_keys_lower = {k.lower() for k in extra_headers}
        if self.xsrf_token and "x-xsrf-token" not in extra_keys_lower:
            headers["X-XSRF-TOKEN"] = self.xsrf_token
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @staticmethod
    def _strip_accept_encoding(headers: Dict[str, str]) -> Dict[str, str]:
        """Remove Accept-Encoding header for certain APIs."""
        return {k: v for k, v in headers.items() if k.lower() != "accept-encoding"}

    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: float = DEFAULT_TIMEOUT,
        strip_accept_encoding: bool = False,
    ) -> httpx.Response:
        """HTTP request with retry."""
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
            except Exception:
                if attempt == MAX_RETRIES:
                    raise
                wait = RETRY_BACKOFF ** attempt
                await asyncio.sleep(wait)

        raise RuntimeError("Unreachable")

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

    async def get_dentry_children(self, dentry_uuid: str) -> List[Dict[str, Any]]:
        """
        Get children list of a directory or space (supports pagination).

        Args:
            dentry_uuid: Directory or space root UUID.

        Returns:
            List of child entries.
        """
        all_children = []
        params = {"dentryUuid": dentry_uuid, "pageSize": "100"}

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
                "pageSize": "100",
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

    async def get_dentry_info(self, dentry_uuid: str) -> Dict[str, Any]:
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

        headers = self._get_headers({
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        })

        client = await self._get_http()
        response = await client.get(
            url,
            headers=headers,
            params={"rnd": random.random()},
            follow_redirects=True,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
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
        except json.JSONDecodeError:
            raise ValueError("Cannot parse page JSON data")

        if "spaceRootDentry" in mainsite_content:
            data = mainsite_content["spaceRootDentry"].get("data", {})
            dentry_uuid = data.get("dentryUuid")
            if dentry_uuid:
                return dentry_uuid

        # Try alternative path
        props = mainsite_content.get("props", {}).get("pageProps", {})
        space_root = props.get("spaceRootDentry", {}).get("data", {})
        if space_root.get("dentryUuid"):
            return space_root["dentryUuid"]

        raise ValueError("Cannot find root dentry UUID")

    async def get_document_data(self, node_id: str, dentry_key: Optional[str] = None) -> Dict[str, Any]:
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

    async def download_file(self, node_id: str) -> bytes:
        """
        Download file content for downloadable types (pdf, docx, etc.).

        Args:
            node_id: Document node ID.

        Returns:
            File content as bytes.
        """
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

        client = await self._get_http()
        file_response = await client.get(pre_sign_urls[0], timeout=DEFAULT_TIMEOUT)
        file_response.raise_for_status()
        return file_response.content

    async def export_to_pdf(
        self,
        node_id: str,
        filename: Optional[str] = None,
        poll_interval: float = 2.0,
        max_wait: float = 120.0,
    ) -> bytes:
        """
        Export native adoc document to PDF.

        Args:
            node_id: Document node ID.
            filename: Output filename (optional).
            poll_interval: Polling interval for export status.
            max_wait: Maximum wait time for export completion.

        Returns:
            PDF content as bytes.
        """
        # Step 1: Get document info
        info = await self.get_dentry_info(node_id)
        data = info.get("data", {})
        dentry_key = data.get("dentryKey")
        doc_key = data.get("docKey")
        space_id = data.get("spaceId")
        doc_name = filename or data.get("name", "document").replace(".adoc", "")

        # Step 2: Get document data
        doc_data = await self.get_document_data(node_id, dentry_key)
        doc_content = doc_data.get("data", {})
        checkpoint = doc_content.get("documentContent", {}).get("checkpoint", {})
        access_token = doc_content.get("accessToken", "")
        base_version = checkpoint.get("baseVersion", 0)
        user_nick = doc_content.get("userInfo", {}).get("user", {}).get("nick", "")

        # Step 3: Prepare export options
        export_options = {
            "openToken": {
                "docOpenToken": access_token,
                "corpId": self._portal_corp_id,
                "docKey": doc_key,
            },
            "isNew": True,
            "customConfig": {
                "content": "ONLYCONTENT",
                "mode": "PORTRAIT",
                "watermark": "CLOSE",
                "nick": user_nick,
                "corpName": "",
                "link": "",
                "enableTableAutofitWidth": False,
            },
            "fileName": doc_name,
            "showDocTitle": True,
            "ctxVersion": base_version,
            "printStyle": {"backgroundColor": "var(--we_bg_default_color, rgba(255, 255, 255, 1))"},
            "version": 1,
            "appVersion": "4.98.9",
            "exportType": "pdf",
            "corpId": self._portal_corp_id,
            "lang": "zh-CN",
        }

        # Step 4: Operation guard (DOWNLOAD preamble)
        guard_headers = self._get_headers({
            "a-token": self._doc_atoken,
            "corp-id": self._portal_corp_id,
            "bx-v": "2.5.36",
        })
        await self._request(
            "POST",
            API_OPERATION_GUARD,
            json_data={"operation": "DOWNLOAD", "dentryUuid": node_id},
            headers=guard_headers,
        )

        # Step 5: Get upload URL
        upload_body = json.dumps({
            "asl": checkpoint.get("content", ""),
            "optionsString": json.dumps(export_options, separators=(",", ":")),
        }, separators=(",", ":"))

        upload_headers = self._get_headers({
            "a-token": self._doc_atoken,
            "a-doc-key": doc_key,
            "a-host-doc-key": "",
        })

        upload_info = await self._request(
            "POST",
            API_RESOURCES_UPLOAD_INFO,
            json_data={"size": len(upload_body.encode("utf-8"))},
            headers=upload_headers,
            strip_accept_encoding=True,
        )
        upload_url = upload_info.json().get("data", {}).get("uploadUrl")

        # Step 6: Upload to OSS
        client = await self._get_http()
        put_response = await client.put(upload_url, content=upload_body, timeout=DEFAULT_TIMEOUT)
        put_response.raise_for_status()

        # Step 7: Create export job
        export_headers = self._get_headers({
            "a-token": self._doc_atoken,
            "a-doc-key": doc_key,
            "a-dentry-key": dentry_key,
        })

        export_response = await self._request(
            "POST",
            API_CREATE_EXPORT_JOB,
            json_data={
                "dentryUuid": node_id,
                "workspaceId": space_id,
                "docKey": doc_key,
                "dentryKey": dentry_key,
                "exportType": "pdf",
            },
            headers=export_headers,
            strip_accept_encoding=True,
        )
        export_result = export_response.json()

        if not export_result.get("isSuccess"):
            raise ValueError(f"Export job creation failed: {export_result.get('message')}")

        job_data = export_result.get("data", {})
        job_id = job_data.get("jobId")
        download_url = job_data.get("url")

        # Step 8: Poll for completion
        if not job_data.get("done"):
            elapsed = 0.0
            while elapsed < max_wait:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                status_response = await self._request(
                    "GET",
                    API_QUERY_EXPORT_STATUS,
                    params={"jobId": job_id},
                    headers=export_headers,
                )
                status_result = status_response.json()
                status_data = status_result.get("data", {})

                if status_data.get("done"):
                    download_url = status_data.get("url") or download_url
                    break

        if not download_url:
            raise ValueError("No download URL from export job")

        client = await self._get_http()
        pdf_response = await client.get(download_url, timeout=DEFAULT_TIMEOUT)
        pdf_response.raise_for_status()
        return pdf_response.content