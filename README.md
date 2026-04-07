# AI Workshop

A personal collection of AI-related mini-projects, skills, plugins, and configurations for coding agents and IDEs.

## What's Inside

- **`skills/`** — Reusable Agent Skills for AI coding assistants
- **`.cursor/rules/`** — Cursor AI coding rules and project conventions
  - `workflow.mdc` — General workflow (clarification, cleanup, doc sync)
  - `code-style.mdc` — Code style (comments, formatting, diff hygiene)
  - `git.mdc` — Git rules (branching, commit format, no unsolicited operations)
  - `project-config.mdc` — Project config (venv, env vars, scaffolding)
  - `sqlalchemy.mdc` — SQLAlchemy session handling
  - `code-analysis-doc.mdc` — Code analysis document standards

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
