# AI Workshop

A personal collection of AI-related mini-projects, skills, plugins, and configurations for coding agents and IDEs.

## What's Inside

- **`skills/`** — Reusable [Agent Skills](https://skills.sh/) for AI coding assistants
- **`.cursor/rules/`** — Cursor AI coding rules and project conventions
  - `project-conventions.mdc` — Workflow, code style, git, config, and ORM patterns
  - `code-analysis-doc.mdc` — Writing standards for code analysis documents

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

### Publish

Skills are automatically listed on [skills.sh](https://skills.sh/) when users install them via `npx skills add`. No explicit publish step is needed — just push to GitHub and share the install command.

To create a new skill:

```bash
npx skills init <skill-name>
```

Then move the generated folder into `skills/` and push.

## License

[MIT](LICENSE) © He Wang
