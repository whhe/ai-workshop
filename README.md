# AI Workshop

A personal collection of AI-related mini-projects, skills, plugins, and configurations for coding agents and IDEs.

## What's Inside

- **`.claude/`** — Portable Claude Code global configuration
- **`.cursor/rules/`** — Cursor AI rules and project conventions
- **`skills/`** — Reusable Agent Skills for AI coding assistants
- **`scripts/`** — Shell utilities for managing skills locally

## Skills

| Skill | Description |
|-------|-------------|
| [code-analysis](./skills/code-analysis/) | Multi-pass source code analysis and feature deep-dive. Produces structured documents with architecture diagrams, flow traces, and precise coverage of trigger conditions, edge cases, and error paths. |
| [code-review](./skills/code-review/) | Risk-priority code review with test-fix-retest closed loop. Covers behavioral regressions, SOLID/architecture, security, performance, dead code, and test coverage. |
| [dingtalk-docs-reader](./skills/dingtalk-docs-reader/) | DingTalk document read-only access: list, download, extract text, export PDF. Cookie-based auth, no enterprise app approval needed. Table documents (asheet) not supported. |
| [github-issue-pr-draft](./skills/github-issue-pr-draft/) | Draft/update GitHub issue and PR titles and bodies; writes only after explicit user confirmation. Templates, upstream resolution, and log redaction: see skill [SKILL.md](./skills/github-issue-pr-draft/SKILL.md). |
| [resolve-review-comments](./skills/resolve-review-comments/) | End-to-end resolution of unresolved review comments on a GitHub PR or GitLab MR: fetch unresolved threads, triage, implement, self-review, commit, push, mark threads resolved, and update the PR/MR description. |

### Install

The Claude Code global config assumes the rules are synced to `~/.cursor/rules/` and the listed skills are installed globally.

Install all skills:

```bash
npx skills add whhe/ai-workshop --global
```

Install a specific skill:

```bash
npx skills add whhe/ai-workshop --skill code-analysis --global
npx skills add whhe/ai-workshop --skill code-review --global
npx skills add whhe/ai-workshop --skill dingtalk-docs-reader --global
npx skills add whhe/ai-workshop --skill github-issue-pr-draft --global
npx skills add whhe/ai-workshop --skill resolve-review-comments --global
```

## Scripts

| Script | Description |
|--------|-------------|
| `skill-path.sh` | Resolve a skill's absolute path by target (`repo \| claude \| cursor \| global`) and name |
| `sync-skill.sh` | Bidirectional sync between repo and claude/cursor/global: `pull` (external→repo) or `push` (repo→external) |
| `lint-skill.sh` | Multi-round convention audit via Claude Code CLI — reads `skill-conventions.mdc`, fixes violations, loops until passing |

## License

[MIT](LICENSE) © He Wang
