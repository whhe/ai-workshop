# resolve-review-comments

An Agent Skill for end-to-end resolution of unresolved review comments on a GitHub PR or GitLab MR.

## Features

- **Platform-agnostic** — works with GitHub and GitLab (cloud or self-hosted)
- **Full triage gate** — classifies every actionable comment before touching code and records non-actionable context; skips require written justification
- **Adversarial Review-Fix Loop** — per iteration: impact analysis, code review (via skill or inline fallback), and fix; max 3 iterations; remaining findings trigger a user checkpoint
- **Clean commit discipline** — enforces Conventional Commits format; prohibits review metadata and external file references in commit messages and PR/MR body
- **Thread management** — marks implemented comments resolved; posts reply for skipped comments
- **Minimal change** — resolves exactly what comments request; no unrequested refactoring
- **No review metadata** — outputs are understandable from diff + history alone; no reviewer names or thread IDs leak into commits or descriptions
- **Skill-aware** — scans installed skills at start (Skill Resolution) and delegates platform API, code review / change validation, and PR/MR description drafting; code modification is always executed inline

## How It Works

1. **Preflight** — parse the URL, detect platform, verify local branch matches PR/MR head, and resolve skill delegation
2. **Fetch** — retrieve the complete collection of review threads, exhaust any pagination or continuation mechanism, then identify all unresolved threads with their thread IDs
3. **Triage** — classify actionable feedback as Implement / Skip / Clarify and non-actionable replies as Context; gate blocks until confirmed
4. **Implement** — apply minimal fixes in dependency order, respecting project conventions
5. **Review-Fix Loop** — per iteration: map blast radius (callers, dependents, importers), run code review (via skill or inline fallback), fix findings; max 3 iterations; remaining findings trigger a user checkpoint
6. **Commit** — one or more Conventional Commits; no review metadata allowed
7. **Push + mark resolved** — push, apply one aggregate disposition per thread, then re-fetch unresolved and processed threads and return any unseen comments or notes to triage
8. **Update description** — refresh PR/MR title (project convention or Conventional Commits) and body (repo-only content)

## Prerequisites

For GitHub PRs, authenticate the `gh` CLI:

```bash
gh auth login
```

For GitLab MRs, provide a Personal Access Token with `api` scope:

```bash
export GITLAB_TOKEN=your_personal_access_token
```

## Install

```bash
npx skills add whhe/ai-workshop --skill resolve-review-comments --global
```

## Usage

Provide a PR or MR URL to your AI coding agent:

- "Resolve the review comments on this PR: https://github.com/owner/repo/pull/42"
- "Address all open review threads on this MR: https://gitlab.example.com/group/project/-/merge_requests/7"

The agent will load the skill, fetch unresolved threads, triage them, and walk through the full resolution workflow.

## License

[MIT](../../LICENSE)
