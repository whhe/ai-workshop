# AGENTS.md

> Model-facing project context. Keep concise and in sync with `.cursor/rules/`.

## Project

- **Name**: ai-workshop
- **Description**: Personal AI-related mini-projects, skills, plugins, and configurations
- **Stack**: Python (skills), Markdown (SKILL.md)
- **GitHub**: `whhe/ai-workshop`

## Structure

```
.
├── .claude/                 # Claude Code global config
├── .cursor/rules/           # Cursor AI rules
├── skills/                  # Agent Skills
├── .gitignore
├── AGENTS.md                # This file (model-facing)
├── LICENSE
└── README.md                # Human-facing readme
```

## Rules

Rules in `.cursor/rules/` mirror `~/.cursor/rules/` (system-level), except `yuque-mcp.mdc` which is system-only.

| File | Always | Description |
|------|--------|-------------|
| `coding.mdc` | no | Coding conventions — load before creating or editing any source file |
| `git.mdc` | no | Git — commit/rebase, branching, stash, PRs, semantic commits; load trigger and owner-repo checks in the rule file |
| `skill-conventions.mdc` | no | Skill authoring conventions — load when creating or editing a SKILL.md |
| `skill-usage.mdc` | yes | Skill discovery & loading discipline (scan → match → load) |
| `workflow.mdc` | yes | Think first, goal-driven execution, post-task cleanup, doc sync, project config |

## Skill Constraints

- **Self-containment**: each skill MUST be independently usable in isolation. Skills MUST NOT reference, import, delegate to, or share content with other skills — no cross-skill file references, no shared reference files between skill directories. If two skills need identical instructions, duplicate the text in each; divergence from duplication is preferable to coupling.

## Skills

| Skill | Path |
|-------|------|
| code-analysis | `skills/code-analysis/` |
| code-review | `skills/code-review/` |
| dingtalk-docs-reader | `skills/dingtalk-docs-reader/` |
| github-issue-pr-draft | `skills/github-issue-pr-draft/` |
| resolve-review-comments | `skills/resolve-review-comments/` |
