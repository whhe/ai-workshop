# AGENTS.md

> Model-facing project context. Keep concise and in sync with `.cursor/rules/`.

## Project

- **Name**: ai-workshop
- **Description**: Personal AI-related mini-projects, skills, plugins, and configurations
- **Stack**: Python (skills), Markdown (SKILL.md)
- **GitHub**: `whhe/ai-workshop`

## Rules

- Project conventions: `.cursor/rules/project-conventions.mdc` (always applied)
- Code analysis doc standards: `.cursor/rules/code-analysis-doc.mdc` (always applied)

## Skills (skills.sh)

Skills are published to [skills.sh](https://skills.sh/) via GitHub. Install: `npx skills add whhe/ai-workshop`.

Each skill lives in `skills/<name>/` with a required `SKILL.md` (YAML frontmatter: `name`, `description`). The `name` field **must** match the directory name (lowercase, hyphens only).

| Skill | Path |
|-------|------|
| dingtalk-adoc-reader | `skills/dingtalk-adoc-reader/` |

## Structure

```
.
├── .cursor/rules/         # Cursor AI rules
├── skills/                # Agent Skills (skills.sh)
│   └── dingtalk-adoc-reader/
│       ├── SKILL.md       # Skill entry point
│       └── dingtalk_adoc_reader/  # Python package
├── AGENTS.md              # This file (model-facing)
├── README.md              # Human-facing readme
├── LICENSE
└── .gitignore
```
