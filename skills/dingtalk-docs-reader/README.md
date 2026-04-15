# dingtalk-docs-reader

An Agent Skill for reading DingTalk (钉钉) documents via cookie-based auth — no enterprise app or admin approval needed.

## Features

- **Knowledge base traversal** — list spaces, walk directory trees
- **Text extraction** — extract text from native `adoc` documents
- **PDF export** — export `adoc` documents to PDF
- **File download** — download attachments (pdf, docx, xlsx, pptx, txt, md, png, jpg, jpeg)
- **Link resolution** — follow `dlink` / `hlink` shortcut nodes to their targets

> **Not supported:** table documents (asheet).

## How It Works

Instead of the official DingTalk SDK (which requires an enterprise app and org admin approval), this skill calls internal web APIs using a browser cookie. This makes it usable for personal access and custom DingTalk deployments (AliDing, AntDing, etc.) where the SDK does not support document reads.

## Install

```bash
npx skills add whhe/ai-workshop --skill dingtalk-docs-reader
```

## Prerequisites

Python dependencies (install into your project's venv):

```bash
pip install httpx beautifulsoup4
```

## Authentication

1. Open <https://alidocs.dingtalk.com> in your browser (logged in)
2. DevTools → Network tab → find any request to `alidocs.dingtalk.com`
3. Copy the full `Cookie` header value

The cookie must contain `XSRF-TOKEN`. When it expires, repeat the steps above.

## Quick Start

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from client import DingTalkClient

async def main():
    cookie = "your-cookie-string"
    async with DingTalkClient(cookie) as client:
        space_id = client.extract_space_id_from_url(
            "https://alidocs.dingtalk.com/i/spaces/ABC123"
        )
        root_uuid = await client.get_root_dentry_uuid(space_id)
        children = await client.get_dentry_children(root_uuid)
        for child in children:
            print(f"{child['name']} ({child.get('extension', 'folder')})")
```

## License

[MIT](../../LICENSE)
