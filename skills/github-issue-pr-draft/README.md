# github-issue-pr-draft

An Agent Skill that drafts and updates GitHub issue and pull request content for posting, with a blocking confirmation gate before any write. Follows upstream templates, semantic PR titles, and conventional commit best practices.

## Features

- **Template-aware drafting** — detects upstream `ISSUE_TEMPLATE` / `PULL_REQUEST_TEMPLATE` and follows them verbatim; falls back to built-in defaults only when none exist
- **Smart upstream resolution** — single-remote repos pick automatically; fork scenarios (2 remotes, one matching the current GitHub login) auto-select the other as upstream; otherwise ask the user
- **Confirmation gate** — never creates or mutates issues/PRs without explicit user approval of the final title, body, and target (including PR `head → base`)
- **Semantic PR titles** — enforces [Conventional Commits](https://www.conventionalcommits.org/) format (`type(scope): subject`) with optional `scope`, `!` for breaking changes, and ≤ 72-char subjects
- **No references in titles** — forbids `#N` or issue/PR URLs in both issue and PR titles; all references go inline in body prose
- **Three-bucket log redaction** — always strips absolute path prefixes and credentials from pasted logs; asks the user about context-dependent items (IPs, emails, internal domains, etc.); never touches narrative prose
- **Execution-agnostic** — works with `gh` CLI, GitHub MCP, REST API, or any available tool at runtime

## How It Works

The skill guides an AI coding agent through a 5-step workflow:

1. **Preflight** — resolve `owner/repo` (automatic when unambiguous per remote layout; otherwise ask), classify task type, detect templates
2. **Task-Specific Context Gathering** — search for duplicates, read PR/issue state, collect reproduction facts
3. **Draft Content** — apply content rules, template structure, and log redaction
4. **Confirmation Gate** (⛔ blocking) — present full draft; wait for explicit user approval
5. **Execute & Report** — perform only the confirmed actions; return URLs and numbers

## Install

```bash
npx skills add whhe/ai-workshop --skill github-issue-pr-draft --global
```

## Usage

Use it when the goal is **published or updated** issue/PR text on GitHub (after you approve the draft), not for purely local brainstorming unless you say you will post later. Example prompts:

- "Open an issue upstream about the crash we just reproduced"
- "Update PR #123 to reflect the latest commits"
- "Create a PR against the upstream repo for this branch"
- "Edit issue #42's body to add the new repro steps"
- "Draft the upstream issue from this repro; do not publish until I approve the title and body"

The agent will automatically load the skill, gather context, draft the content, and wait for your confirmation before creating or modifying anything on GitHub.

## License

[MIT](../../LICENSE)
