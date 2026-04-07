# AI Workshop

A personal collection of AI-related mini-projects, skills, plugins, and configurations for coding agents and IDEs.

## What's Inside

- **`skills/`** — Reusable Agent Skills for AI coding assistants
- **`.cursor/rules/`** — Cursor AI coding rules and project conventions (mirrors `~/.cursor/rules/`, except `yuque-mcp.mdc`)
  - `workflow.mdc` — Workflow, clarification, post-task cleanup, doc sync, project config
  - `git.mdc` — Branching, no unsolicited ops, stash, rebase, semantic commit format
  - `skill-usage.mdc` — Skill discovery & loading discipline
  - `coding.mdc` — Coding conventions, style, type safety, error handling, testing
  - `code-analysis-doc.mdc` — Code analysis document structure & pseudocode standards

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
