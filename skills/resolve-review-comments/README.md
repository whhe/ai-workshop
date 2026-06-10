# resolve-review-comments

An Agent Skill for end-to-end resolution of unresolved review comments on a GitHub PR or GitLab MR.

## Features

- **Platform-agnostic** — works with GitHub and GitLab (cloud or self-hosted)
- **Full triage gate** — classifies every comment before touching code; skips require written justification
- **Self-review loop** — impact analysis + up to 3 review-fix iterations before committing
- **Clean commit discipline** — enforces Conventional Commits format; prohibits review metadata and external file references in commit messages and PR/MR body
- **Thread management** — marks implemented comments resolved; posts reply for skipped comments
- **Minimal change** — resolves exactly what comments request; no unrequested refactoring
- **No review metadata** — outputs are understandable from diff + history alone; no reviewer names or thread IDs leak into commits or descriptions
- **Skill-aware** — discovers available skills at start and delegates platform API, code modification, and review validation accordingly

## How It Works

1. **Preflight** — parse the URL, detect platform, verify local branch matches PR/MR head
2. **Fetch** — retrieve all unresolved review threads with their thread IDs
3. **Triage** — classify each comment as Implement / Skip / Clarify; gate blocks until confirmed
4. **Implement** — apply minimal fixes in dependency order, respecting project conventions
5. **Self-review** — map blast radius (callers, dependents, importers), then review-fix loop (max 3 iterations)
6. **Commit** — one or more Conventional Commits; no review metadata allowed
7. **Push + mark resolved** — push, then resolve threads or reply with skip reasons
8. **Update description** — refresh PR/MR title (Conventional Commits) and body (repo-only content)

## Install

```bash
npx skills add whhe/ai-workshop --skill resolve-review-comments
```

## Usage

Provide a PR or MR URL to your AI coding agent:

- "Resolve the review comments on this PR: https://github.com/owner/repo/pull/42"
- "Address all open review threads on this MR: https://gitlab.example.com/group/project/-/merge_requests/7"

The agent will load the skill, fetch unresolved threads, triage them, and walk through the full resolution workflow.

## License

[MIT](../../LICENSE)
