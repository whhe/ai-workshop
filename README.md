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
| [resolve-review-comments](./skills/resolve-review-comments/) | End-to-end resolution of GitHub PR or GitLab MR feedback: completely collect and triage items, implement and self-review, synchronize replies and PR/MR context, conditionally push, transition threads, and verify review automation. |

### Install

The Claude Code global config assumes the rules are synced to `~/.cursor/rules/`. The Codex setup manifest tracks the current global skill set; repository-only skills can be installed separately below.

Set up a fresh Codex machine (clone/update this repository, link the rules, write `~/.codex/AGENTS.md`, and install the current global skill set):

```bash
mkdir -p ~/.codex
git clone https://github.com/whhe/ai-workshop.git ~/.codex/ai-workshop
~/.codex/ai-workshop/scripts/setup-codex.sh
```

The script keeps the repository at `~/.codex/ai-workshop` by default. Override `CODEX_WORKSHOP_DIR`, `CODEX_HOME`, `CODEX_RULES_DIR`, `CODEX_WORKSHOP_REPO_URL`, or `CODEX_SKILLS_AGENT` when needed. Skills are installed and reconciled for the Codex agent only by default. Re-running it pulls fast-forward updates and refreshes the rule links; existing rule files are backed up before they are replaced. The tracked global skill manifest is [scripts/codex-skills.txt](./scripts/codex-skills.txt).

Update an already initialized machine:

```bash
~/.codex/ai-workshop/scripts/update-codex.sh
```

The update script requires an existing worktree, pulls with `git pull --ff-only`, refreshes rule links, installs newly added manifest entries, removes skills previously managed by this tool that were deleted from the manifest, updates the remaining tracked skills, and verifies the final skill list.

Install all skills from this repository manually:

```bash
npx skills add whhe/ai-workshop --global --agent codex
```

Install a specific skill:

```bash
npx skills add whhe/ai-workshop --skill code-analysis --global --agent codex
npx skills add whhe/ai-workshop --skill code-review --global --agent codex
npx skills add whhe/ai-workshop --skill dingtalk-docs-reader --global --agent codex
npx skills add whhe/ai-workshop --skill github-issue-pr-draft --global --agent codex
npx skills add whhe/ai-workshop --skill resolve-review-comments --global --agent codex
```

## Scripts

| Script | Description |
|--------|-------------|
| `skill-path.sh` | Resolve a skill's absolute path by target (`repo \| claude \| cursor \| global`) and name |
| `sync-skill.sh` | Bidirectional sync between repo and claude/cursor/global: `pull` (external→repo) or `push` (repo→external) |
| `lint-skill.sh` | Multi-round convention audit via Claude Code CLI — reads `skill-conventions.mdc`, fixes violations, loops until passing |
| `codex-skills.txt` | Source and name manifest for the global skills managed by the Codex setup/update scripts |
| `setup-codex.sh` | Bootstrap a fresh Codex machine and keep its global rules and skills synchronized |
| `update-codex.sh` | Pull the latest rules and update the tracked global skills on an existing Codex machine |

## License

[MIT](LICENSE) © He Wang
