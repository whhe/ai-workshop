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
| `workflow.mdc` | yes | Think first, goal-driven execution, post-task cleanup, doc sync, project config |
| `git.mdc` | no | Git rules — load before any git operation or code change on a branch |
| `skill-usage.mdc` | yes | Skill discovery & loading discipline (scan → match → load) |
| `coding.mdc` | no | Coding conventions — load before creating or editing any source file |
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
