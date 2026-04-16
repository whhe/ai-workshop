# AI Workshop

A personal collection of AI-related mini-projects, skills, plugins, and configurations for coding agents and IDEs.

## What's Inside

- **`.cursor/rules/`** — Cursor AI rules and project conventions
- **`skills/`** — Reusable Agent Skills for AI coding assistants

## Skills

| Skill | Description |
|-------|-------------|
| [code-review](./skills/code-review/) | Risk-priority code review with test-fix-retest closed loop. Covers behavioral regressions, SOLID/architecture, security, performance, dead code, and test coverage. |
| [dingtalk-docs-reader](./skills/dingtalk-docs-reader/) | DingTalk document read-only access: list, download, extract text, export PDF. Cookie-based auth, no enterprise app approval needed. Table documents (asheet) not supported. |

### Install

Install all skills:

```bash
npx skills add whhe/ai-workshop
```

Install a specific skill:

```bash
npx skills add whhe/ai-workshop --skill code-review
npx skills add whhe/ai-workshop --skill dingtalk-docs-reader
```

## License

[MIT](LICENSE) © He Wang
