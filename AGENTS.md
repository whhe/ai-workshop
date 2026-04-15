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
| `code-analysis-doc.mdc` | no | Code analysis document structure & pseudocode standards |
| `coding.mdc` | no | Coding conventions — load before creating or editing any source file |
| `git.mdc` | no | Git rules — load before any git operation or code change on a branch |
| `skill-conventions.mdc` | no | Skill authoring conventions — load when creating or editing a SKILL.md |
| `skill-usage.mdc` | yes | Skill discovery & loading discipline (scan → match → load) |
| `workflow.mdc` | yes | Think first, goal-driven execution, post-task cleanup, doc sync, project config |

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
│       ├── dingtalk_adoc_reader/  # Python package
│       └── SKILL.md       # Skill entry point
├── .gitignore
├── AGENTS.md              # This file (model-facing)
├── LICENSE
└── README.md              # Human-facing readme
```
