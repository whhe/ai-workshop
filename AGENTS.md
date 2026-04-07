# AGENTS.md

> Model-facing project context. Keep concise and in sync with `.cursor/rules/`.

## Project

- **Name**: ai-workshop
- **Description**: Personal AI-related mini-projects, skills, plugins, and configurations
- **Stack**: Python (skills), Markdown (SKILL.md)
- **GitHub**: `whhe/ai-workshop`

## Rules

All rules in `.cursor/rules/` are always applied unless otherwise specified:

- `workflow.mdc` — General workflow (clarification, post-task cleanup, doc sync)
- `code-style.mdc` — Code style (comments, formatting, diff hygiene)
- `git.mdc` — Git rules (branching, commit format, no unsolicited operations)
- `project-config.mdc` — Project config (venv, env vars, scaffolding)
- `sqlalchemy.mdc` — SQLAlchemy session handling (Python files only)
- `code-analysis-doc.mdc` — Code analysis document standards

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
