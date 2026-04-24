# AI Workshop

A personal collection of AI-related mini-projects, skills, plugins, and configurations for coding agents and IDEs.

## What's Inside

- **`.cursor/rules/`** — Cursor AI rules and project conventions
- **`skills/`** — Reusable Agent Skills for AI coding assistants

## Skills

| Skill | Description |
|-------|-------------|
| [code-analysis](./skills/code-analysis/) | Multi-pass source code analysis and feature deep-dive. Produces structured documents with architecture diagrams, flow traces, and precise coverage of trigger conditions, edge cases, and error paths. |
| [code-review](./skills/code-review/) | Risk-priority code review with test-fix-retest closed loop. Covers behavioral regressions, SOLID/architecture, security, performance, dead code, and test coverage. |
| [dingtalk-docs-reader](./skills/dingtalk-docs-reader/) | DingTalk document read-only access: list, download, extract text, export PDF. Cookie-based auth, no enterprise app approval needed. Table documents (asheet) not supported. |
| [github-issue-pr-draft](./skills/github-issue-pr-draft/) | Draft/update GitHub issue and PR titles and bodies; writes only after explicit user confirmation. Templates, upstream resolution, and log redaction: see skill [SKILL.md](./skills/github-issue-pr-draft/SKILL.md). |

### Install

Install all skills:

```bash
npx skills add whhe/ai-workshop
```

Install a specific skill:

```bash
npx skills add whhe/ai-workshop --skill code-analysis
npx skills add whhe/ai-workshop --skill code-review
npx skills add whhe/ai-workshop --skill dingtalk-docs-reader
npx skills add whhe/ai-workshop --skill github-issue-pr-draft
```

## License

[MIT](LICENSE) © He Wang
