# resolve-review-comments

An Agent Skill for end-to-end resolution of unresolved review comments on a GitHub PR or GitLab MR.

## Features

- **Platform-agnostic** — works with GitHub and GitLab (cloud or self-hosted)
- **Full triage gate** — classifies every comment before touching code; skips require written justification
- **Self-review loop** — validates all changes as a whole before committing
- **Clean commit discipline** — enforces Conventional Commits format; prohibits review metadata in commit messages and PR/MR body
- **Thread management** — marks implemented comments resolved; posts reply for skipped comments
- **Skill-aware** — hints the agent to check for available skills at each step without hard-wiring dependencies

## How It Works

1. **Preflight** — parse the URL, detect platform, verify local branch matches PR/MR head
2. **Fetch** — retrieve all unresolved review threads with their thread IDs
3. **Triage** — classify each comment as Implement / Skip / Clarify; gate blocks until confirmed
4. **Implement** — apply minimal fixes in dependency order, respecting project conventions
5. **Self-review** — review the full changeset for regressions and correctness
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
