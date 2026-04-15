# AI Workshop

A personal collection of AI-related mini-projects, skills, plugins, and configurations for coding agents and IDEs.

## What's Inside

- **`.cursor/rules/`** — Cursor AI rules and project conventions
- **`skills/`** — Reusable Agent Skills for AI coding assistants

## Skills

| Skill | Description |
|-------|-------------|
| [dingtalk-adoc-reader](./skills/dingtalk-adoc-reader/) | DingTalk native document (adoc) read-only access: list, download, extract text, export PDF. Cookie-based auth, no enterprise app approval needed. |

### Install

Install all skills:

```bash
npx skills add whhe/ai-workshop
```

Install a specific skill:

```bash
npx skills add whhe/ai-workshop --skill dingtalk-adoc-reader
```

## License

[MIT](LICENSE) © He Wang
