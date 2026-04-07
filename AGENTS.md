# AGENTS.md

> Model-facing project context. Keep concise and in sync with `.cursor/rules/`.

## Project

- **Name**: ai-workshop
- **Description**: Personal AI-related mini-projects, skills, plugins, and configurations
- **Stack**: Python (skills), Markdown (SKILL.md)
- **GitHub**: `whhe/ai-workshop`

## Rules

Rules in `.cursor/rules/` mirror `~/.cursor/rules/` (system-level), except `yuque-mcp.mdc` which is system-only.

| File | Always | Description |
|------|--------|-------------|
| `workflow.mdc` | yes | Workflow, clarification, post-task cleanup, doc sync, project config |
| `git.mdc` | yes | Branching, no unsolicited ops, stash, rebase, semantic commit format |
| `skill-usage.mdc` | yes | Skill discovery & loading discipline (scan → match → load) |
| `coding.mdc` | yes | Coding conventions, style, type safety, error handling, testing |
| `code-analysis-doc.mdc` | no | Code analysis document structure & pseudocode standards |

## Skills

| Skill | Path |
|-------|------|
| dingtalk-adoc-reader | `skills/dingtalk-adoc-reader/` |

## Structure

```
.
├── .cursor/rules/         # Cursor AI rules
├── skills/                # Agent Skills
│   └── dingtalk-adoc-reader/
│       ├── SKILL.md       # Skill entry point
│       └── dingtalk_adoc_reader/  # Python package
├── AGENTS.md              # This file (model-facing)
├── README.md              # Human-facing readme
├── LICENSE
└── .gitignore
```
