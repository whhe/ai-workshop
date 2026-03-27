---
name: dingtalk-adoc-reader
description: >-
  Read DingTalk native documents (adoc) via internal web APIs.
  Cookie-based auth (browser session) — no Open Platform app or admin approval needed.
  Supports: QR login automation, knowledge-base traversal, document text extraction,
  file download, and PDF export.
dependencies:
  - httpx >= 0.24.0 (async HTTP client)
  - beautifulsoup4 >= 4.12.0 (HTML parsing)
  - playwright >= 1.40.0 (QR login automation, optional)
capabilities:
  - QR code login via Playwright for cookie authentication
  - List documents in knowledge base recursively
  - Download files (pdf, docx, xlsx, pptx, txt, md, images)
  - Export native adoc documents to PDF
  - Extract text content from native alidocs format
limitations:
  - Uses reverse-engineered internal APIs — no official stability guarantees
  - Cookie-based auth expires periodically; re-login required
  - Custom/branded DingTalk builds (Alibaba, Ant internal) may differ
  - Table documents not supported
  - Rate limiting may apply
---

# DingTalk Document (adoc) API Guide

Portal: <https://alidocs.dingtalk.com>

Programmatic access to DingTalk native documents. No stable public OpenAPI exists for the read paths the web app uses for native docs. This skill mirrors the browser with **cookie-based** session auth and internal endpoints reverse-engineered from the web frontend.

## Official SDK vs This Skill

Alibaba ships Open Platform SDKs (`alibabacloud-dingtalk`, `dingtalk-sdk`) for **server APIs**: app credentials, `access_token`, messaging, org/contacts, calendar, etc. Those SDKs **do not** cover `alidocs.dingtalk.com` native-document reads — auth is app-based (not browser-cookie-based) and the adoc/knowledge-base endpoints are not exposed as stable public OpenAPIs.

**When to use this skill** (cookie-based):

- Individual developer or ad-hoc automation — no enterprise app registration or admin approval needed
- Custom/branded DingTalk deployments where open APIs for documents may not exist
- Read-only access that mirrors "what the user can open in the browser"

**When to use the official SDK** (app-based):

- You have a provisioned enterprise app with approved scopes
- You need published, stable APIs (messaging, contacts, calendar, attendance, etc.)

The `DingTalkClient` keeps a shared `httpx.AsyncClient` with connection pooling. Always use the async context manager or call `aclose()` explicitly:

```python
async with DingTalkClient(cookie) as client:
    ...
```

## Authentication

Every request requires:

- `Cookie` header — full cookie string from an authenticated browser session
- `X-XSRF-TOKEN` header — extracted from the `XSRF-TOKEN` value in the cookie

### Method 1: QR Code Login (Automated)

Uses Playwright to automate the browser login flow:

1. Launch headless Chromium → navigate to `https://alidocs.dingtalk.com`
2. Click login button → new tab opens to `login.dingtalk.com`
3. Capture QR code image → user scans with DingTalk app
4. Detect login completion (URL redirect + new auth cookies)
5. Extract full cookie string from browser context

Key cookies after login: `atoken`, `atknv2`, `nick`, `ssotoken`, `uid`, `XSRF-TOKEN`, `doc_atoken`.

### Method 2: Manual Cookie Extraction

1. Open `https://alidocs.dingtalk.com` in browser (logged in)
2. DevTools → Network tab → find any request to `alidocs.dingtalk.com`
3. Copy the full `Cookie` header value

### Auth Failure Detection

- HTTP 301/302 redirect to `login.dingtalk.com`
- Response URL containing `oauth2/auth`
- Missing auth cookies (`atoken`, `ssotoken`)

## URL Structure

```
Knowledge Base: https://alidocs.dingtalk.com/i/spaces/{space_id}
Document:       https://alidocs.dingtalk.com/i/nodes/{node_id}
```

Use the client methods to extract IDs:

```python
client.extract_space_id_from_url("https://alidocs.dingtalk.com/i/spaces/ABC123")
# → "ABC123"

client.extract_node_id_from_url("https://alidocs.dingtalk.com/i/nodes/xyz789")
# → "xyz789"
```

## API Reference

### Common Headers

```python
HEADERS = {
    "Cookie": "<cookie-string>",
    "X-XSRF-TOKEN": "<extracted-from-cookie>",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
```

All requests disable redirect following (`follow_redirects=False`) to detect auth failures.

### 1. List Directory Children

```
GET https://alidocs.dingtalk.com/box/api/v2/dentry/list?dentryUuid={uuid}&pageSize=100
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dentryUuid` | string | Directory or space root UUID |
| `pageSize` | int | Items per page (max 100) |
| `loadMoreId` | string | Pagination token from previous response |

Response:

```json
{
  "isSuccess": true,
  "data": {
    "children": [
      {
        "dentryUuid": "abc123",
        "name": "Document Title",
        "dentryType": "file",
        "extension": "adoc",
        "dentryKey": "key123",
        "docKey": "doc456",
        "hasChildren": false,
        "createdTime": "2025-01-01T00:00:00Z",
        "updatedTime": "2025-03-18T00:00:00Z"
      }
    ],
    "hasMore": false,
    "loadMoreId": null
  }
}
```

### 2. Get Node Info

```
GET https://alidocs.dingtalk.com/box/api/v2/dentry/info?dentryUuid={uuid}
```

Returns node details including `driveSpaceId` and `driveDentryId` for Drive file downloads.

### 3. Get Document Content (Native adoc)

```
POST https://alidocs.dingtalk.com/api/document/data
Content-Type: application/json
A-DENTRY-KEY: {dentry_key}
Referer: https://alidocs.dingtalk.com/i/nodes/{node_id}

{"fetchBody": true}
```

Response:

```json
{
  "data": {
    "accessToken": "token123",
    "documentContent": {
      "checkpoint": {
        "content": "{...alidocs-json...}",
        "baseVersion": 493
      }
    },
    "userInfo": {"user": {"nick": "username"}}
  }
}
```

The `content` field contains the alidocs checkpoint format (nested JSON). Use `accessToken` for PDF export.

### 4. Download File (Presigned URL)

Supported types: pdf, doc, docx, xlsx, pptx, txt, md, png, jpg, jpeg.

```
GET https://alidocs.dingtalk.com/box/api/v2/file/download?dentryUuid={uuid}
```

Response:

```json
{
  "isSuccess": true,
  "data": {
    "ossUrlPreSignatureInfo": {
      "preSignUrls": ["https://oss-url..."]
    }
  }
}
```

Download from the first URL in `preSignUrls`.

### 5. PDF Export for Native Docs

Multi-step export flow for adoc documents (matches browser HAR; identity is in headers, not only JSON):

```
1. GET  /box/api/v2/dentry/info        → spaceId, dentryKey, docKey
2. POST /api/document/data             → checkpoint, accessToken, baseVersion
3. POST /box/api/v1/dentry/operationGuard → body: operationType DOWNLOAD, resourceType 0, resourceIdList [nodeId]
4. POST /core/api/resources/9/upload_info → size, resourceName (docKey), contentType ""; parse storagePath + uploadUrl
5. PUT  uploadUrl                       → upload {"asl","optionsString"} (UTF-8 bytes; size in step 4 must match)
6. POST /api/v2/files/createExportJob   → JSON: {"scene":"normal","storagePath":"<from step 4>"} only; headers a-token, a-doc-key, a-dentry-key, referer (note/preview), optional utm_* / source_doc_app
7. GET  /api/v2/files/queryExportStatus → poll until done
8. GET  download URL                    → PDF bytes
```

If step 6 fails with certain errors (e.g. 52600007, 5xx), the client retries with an alternate `referer` (`/i/nodes/{id}`). Sending `dentryUuid`/`workspaceId` in the createExportJob body (legacy) causes server errors.

Export options format:

```json
{
  "openToken": {
    "docOpenToken": "<accessToken>",
    "corpId": "<portal_corp_id>",
    "docKey": "<doc_key>"
  },
  "isNew": true,
  "customConfig": {
    "content": "ONLYCONTENT",
    "mode": "PORTRAIT",
    "watermark": "CLOSE",
    "nick": "<user_nick>"
  },
  "fileName": "<document_title>",
  "showDocTitle": true,
  "ctxVersion": "<baseVersion>",
  "exportType": "pdf",
  "lang": "zh-CN"
}
```

## Supported Document Types

| Extension | Type | Method |
|-----------|------|--------|
| `adoc` | Native alidoc | PDF export; text extraction fallback |
| `pdf` | PDF | Binary download |
| `doc`, `docx` | Word | Binary download |
| `xlsx` | Excel | Binary download |
| `pptx` | PowerPoint | Binary download |
| `txt`, `md` | Plain text | Binary download |
| `png`, `jpg`, `jpeg` | Image | Binary download |
| `folder` | Directory | List children (not downloadable) |

Unsupported: `dlink`, `hlink` (shortcuts), table documents.

## Text Extraction from Alidocs

Native adoc documents use `application/x-alidocs-package` format. Extract text by recursively walking the JSON tree:

```python
from dingtalk_adoc_reader.transformer import extract_text_from_alidocs

texts = extract_text_from_alidocs(alidocs_json)
```

The extractor:

1. Walks the nested JSON recursively (depth-limited to 25)
2. Collects values from `"text"` and `"t"` keys
3. Filters noise (UUIDs, CSS values, type names, short IDs, bullet chars)
4. Also captures bare strings in nested structures

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `DingTalkAuthError` | Cookie expired/invalid | Re-login via QR code |
| HTTP 429 | Rate limited | Auto-retried with exponential backoff |
| HTTP 404 | Document not found | Check node_id validity |
| Export timeout | Large document | Increase `max_wait` parameter |

### Retry Boundary

The client has **two layers** of retry, with different responsibilities:

| Layer | Scope | Built-in? | What it does |
|-------|-------|-----------|-------------|
| `_request` (transport) | All HTTP calls | Yes | Retries on HTTP 429 and transient network errors (3 attempts, exponential backoff). HTTP 4xx/5xx (other than 429) and auth errors propagate immediately. |
| `createExportJob` Referer fallback | PDF export step 6 only | Yes | If the server rejects the `note/preview` Referer (e.g. error 52600007, HTTP 400/5xx), retries once with an alternate Referer (`/i/nodes/{id}`). This is a **DingTalk-specific protocol workaround**, not a generic retry. |

**Callers are responsible for** any additional retry/back-off policies (e.g. retrying a full `export_to_pdf` call on transient failures, circuit-breaking across multiple documents, etc.). The client does not wrap these higher-level strategies.

## Usage Examples

### QR Code Login

```python
import asyncio
from dingtalk_adoc_reader.auth import start_qr_login, get_session, LoginStatus

async def login():
    session = await start_qr_login()

    while session.status == LoginStatus.PENDING:
        await asyncio.sleep(1)
        session = get_session(session.session_id)

    if session.status != LoginStatus.QR_READY:
        raise RuntimeError(f"Login failed: {session.error}")

    # session.qr_image_base64 contains the QR code image (base64-encoded PNG)
    print("Scan the QR code with DingTalk app")

    while session.status == LoginStatus.QR_READY:
        await asyncio.sleep(2)
        session = get_session(session.session_id)

    if session.status == LoginStatus.SUCCESS:
        return session.cookie
    raise RuntimeError(f"Login failed: {session.error}")

cookie = asyncio.run(login())
```

### List Knowledge Base Documents

```python
from dingtalk_adoc_reader.client import DingTalkClient

async with DingTalkClient(cookie) as client:
    space_id = client.extract_space_id_from_url(
        "https://alidocs.dingtalk.com/i/spaces/ABC123"
    )
    root_uuid = await client.get_root_dentry_uuid(space_id)

    async def walk(dentry_uuid, path=""):
        children = await client.get_dentry_children(dentry_uuid)
        for child in children:
            child_path = f"{path}/{child['name']}"
            ext = child.get("extension", "unknown")
            if child.get("dentryType") == "folder":
                await walk(child["dentryUuid"], child_path)
            else:
                print(f"{child_path} ({ext})")

    await walk(root_uuid)
```

### Download Document

```python
from dingtalk_adoc_reader.client import DingTalkClient

async with DingTalkClient(cookie) as client:
    node_id = "xyz789"
    info = await client.get_dentry_info(node_id)
    data = info["data"]
    ext = data["extension"]
    name = data["name"]

    if ext == "adoc":
        content = await client.export_to_pdf(node_id)
        with open(f"{name}.pdf", "wb") as f:
            f.write(content)
    else:
        content = await client.download_file(node_id)
        with open(name, "wb") as f:
            f.write(content)
```

### Extract Text from adoc

```python
import json
from dingtalk_adoc_reader.client import DingTalkClient
from dingtalk_adoc_reader.transformer import extract_text_from_alidocs

async with DingTalkClient(cookie) as client:
    doc_data = await client.get_document_data(node_id)
    checkpoint = doc_data["data"]["documentContent"]["checkpoint"]
    alidocs_json = json.loads(checkpoint["content"])

    texts = extract_text_from_alidocs(alidocs_json)
    print("\n".join(texts))
```
