---
name: dingtalk-docs-reader
description: "Read DingTalk documents (adoc, dlink/hlink, downloadable attachments) via cookie-based auth — no enterprise app or admin approval needed. Supports knowledge-base traversal, text extraction, file download, and PDF export. Table documents (asheet) not supported. Use when accessing DingTalk/alidocs with a browser cookie instead of the official SDK."
---

IRON LAW: Every API call requires a valid browser Cookie with X-XSRF-TOKEN. Auth failures return 301/302 redirects, not 401 — always check for redirects before parsing response JSON.

# DingTalk Document API Guide

Portal: <https://alidocs.dingtalk.com>

Programmatic read access to DingTalk native documents via **cookie-based** session auth and internal endpoints reverse-engineered from the web frontend. No stable public OpenAPI covers these paths.

## Workflow

1. ⛔ BLOCKING **Authenticate** → obtain cookie via manual extraction from browser → verify: `XSRF-TOKEN` present in cookie string
2. ⚠️ REQUIRED **Create client** → `async with DingTalkClient(cookie) as client` → verify: no `DingTalkAuthError` on first call
3. ⚠️ REQUIRED **Navigate** → extract space/node ID from URL → list children or get node info → verify: API returns `isSuccess: true`
4. ⚠️ REQUIRED **Read/Download** → branch by extension:
   - `adoc` → `get_document_data()` + `extract_text_from_alidocs()` for text; (conditional) `export_to_pdf()` if PDF output is needed
   - (conditional) `dlink`/`hlink` → `resolve_external_link()` first, then treat target as regular node
   - other → `download_file()` (validates extension against `DOWNLOADABLE_EXTENSIONS`)
5. (conditional) **Cleanup** → client auto-closes via `async with`; manual `aclose()` if not using context manager

## Official SDK vs This Skill

- **Official DingTalk**: the SDK requires creating an enterprise app, which depends on org admin permissions. This skill only needs a browser cookie — no approval needed.
- **Custom DingTalk deployments** (AliDing, AntDing, etc.): the SDK does not support document reads. This skill calls web APIs directly, unaffected by this limitation.

## Authentication

Every request requires:

- `Cookie` header — full cookie string from an authenticated browser session
- `X-XSRF-TOKEN` header — extracted from the `XSRF-TOKEN` value in the cookie

Auth failure signals: HTTP 301/302 redirect to `login.dingtalk.com`, response URL containing `oauth2/auth`, or missing `atoken`/`ssotoken` cookies.

### Manual Cookie Extraction

1. Open `https://alidocs.dingtalk.com` in browser (logged in)
2. DevTools → Network tab → find any request to `alidocs.dingtalk.com`
3. Copy the full `Cookie` header value

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
        "name": "Doc Title",
        "dentryType": "file",
        "extension": "adoc",
        "dentryKey": "key123",
        "docKey": "doc456"
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

### External Links (`dlink` / `hlink`)

These are shortcut nodes whose target URL lives in `hyperlinkInfo.url` (returned by `get_dentry_info`). Use `resolve_external_link(node_info)` to handle them:

- **alidocs URL** → returns the target `node_id`; treat as a regular node for subsequent operations.
- **Non-alidocs URL** → returns `None` and logs the skipped URL; caller should skip the node.
- **`hyperlinkInfo` missing** → returns `None` with an info log; caller should skip.

Identification: check `extension` field (`dlink` / `hlink`) or `name` suffix (`.dlink` / `.link`).

```python
info = await client.get_dentry_info(child["dentryUuid"])
ext = child.get("extension", "")
name = child.get("name", "")
is_link = ext in ("dlink", "hlink") or name.endswith((".dlink", ".link"))

if is_link:
    target_node_id = client.resolve_external_link(info)
    if target_node_id is not None:
        # alidocs link — treat target_node_id as a regular node
        ...
    else:
        # external or unresolvable link — already logged, skip
        continue
```

Unsupported: table documents.

## Text Extraction from Alidocs

Native adoc documents use `application/x-alidocs-package` format. Extract text by recursively walking the JSON tree:

```python
from transformer import extract_text_from_alidocs

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
| `DingTalkAuthError` | Cookie expired/invalid | Re-extract cookie from browser |
| HTTP 429 | Rate limited | Auto-retried with exponential backoff |
| HTTP 404 | Document not found | Check node_id validity |
| Export timeout | Large document | Increase `max_wait` parameter |

### Retry Boundary

The client has **three layers** of retry, with different responsibilities:

| Layer | Scope | Built-in? | What it does |
|-------|-------|-----------|-------------|
| `_request` (transport) | All API calls | Yes | Retries on HTTP 429 and transient network errors (`httpx.RequestError`, 3 attempts, exponential backoff). HTTP 4xx/5xx (other than 429) and auth errors propagate immediately. |
| `_download_bytes` | Binary file downloads | Yes | Retries on transient network errors (3 attempts, exponential backoff). Used by `download_file` and `export_to_pdf` for the final download step. |
| `createExportJob` Referer fallback | PDF export step 6 only | Yes | If the server rejects the `note/preview` Referer (e.g. error 52600007, HTTP 400/5xx), retries once with an alternate Referer (`/i/nodes/{id}`). This is a **DingTalk-specific protocol workaround**, not a generic retry. |

**Callers are responsible for** any additional retry/back-off policies (e.g. retrying a full `export_to_pdf` call on transient failures, circuit-breaking across multiple documents, etc.). The client does not wrap these higher-level strategies.

## Usage Examples

Add the skill's `scripts/` directory to `sys.path` once before importing:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
```

### List Knowledge Base Documents

```python
from client import DingTalkClient

# verify_ssl defaults to True; pass verify_ssl=False only for known-safe internal networks
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
from client import DingTalkClient

async with DingTalkClient(cookie) as client:
    node_id = "xyz789"
    info = await client.get_dentry_info(node_id)
    ext = info["data"].get("extension", "")
    name = info["data"]["name"]
    # For dlink/hlink nodes, resolve via client.resolve_external_link(info) first

    if ext == "adoc":
        content = await client.export_to_pdf(node_id)
        with open(f"{name}.pdf", "wb") as f:
            f.write(content)
    else:
        # Pass extension to skip redundant get_dentry_info inside download_file
        content = await client.download_file(node_id, extension=ext)
        with open(name, "wb") as f:
            f.write(content)
```

### Extract Text from adoc

```python
import json
from client import DingTalkClient
from transformer import extract_text_from_alidocs

async with DingTalkClient(cookie) as client:
    doc_data = await client.get_document_data(node_id)
    checkpoint = doc_data["data"]["documentContent"]["checkpoint"]
    alidocs_json = json.loads(checkpoint["content"])

    texts = extract_text_from_alidocs(alidocs_json)
    print("\n".join(texts))
```

## Anti-Patterns

- Do NOT call any API without a Cookie containing `XSRF-TOKEN` — the server returns 301/302 (not 401), and the model may misinterpret the redirect as a valid response.
- Do NOT use `download_file()` for `adoc` documents — they have no binary file; use `export_to_pdf()` or `get_document_data()` + `extract_text_from_alidocs()`.
- Do NOT skip `resolve_external_link()` for `dlink`/`hlink` nodes — downloading them directly yields metadata, not the target content.
- Do NOT parse HTTP 301/302 responses as JSON — always check for auth-redirect first.
- Do NOT pass `dentryUuid` or `workspaceId` in the `createExportJob` body — use `storagePath` from `upload_info` only; the legacy fields cause server errors.

## File Reference

Source code lives in `scripts/` — invoke via `import`, do not load into context unless debugging. Ensure the skill's `scripts/` directory is on `sys.path` before importing (see Usage Examples).

| File | When to load |
|------|-------------|
| `scripts/client.py` | Debugging API failures or extending the client with new endpoints |
| `scripts/transformer.py` | Debugging text extraction quality or adding new content-type support |

## Pre-Delivery Checklist

- [ ] Cookie string contains `XSRF-TOKEN` (otherwise all API calls fail silently)
- [ ] `DingTalkAuthError` is caught and surfaced to user with re-login instructions
- [ ] `dlink`/`hlink` nodes resolved via `resolve_external_link` before download attempts
- [ ] `download_file` only called for supported extensions (enforced internally; `ValueError` on mismatch)
- [ ] `export_to_pdf` timeout (`max_wait`) is set high enough for large documents (default 120s)
