# PR Content Rules & Default Template

## Template policy

If an upstream template exists, use it. For each unchecked checkbox item:

- **User action** required (e.g., "I have signed the CLA"): ask the user.
- **Automatable** (e.g., "Compared diff to issue scope", "Ran tests locally"): do it autonomously in Step 2.

If no template exists, use the default template below.

## PR rules

- **Title**: follow the repository's documented PR-title convention or validation rules. If none exist, prefer [semantic commit format](https://www.conventionalcommits.org/) — `type(scope): subject` — as a default.
  - Common types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`.
  - `scope` is optional (e.g., `fix: handle empty list` is valid).
  - When using semantic format, mark breaking changes with `!` (e.g., `feat(api)!: drop v1 endpoints`). For another repository convention, use its breaking-change notation; describe the impact and migration in the body regardless.
  - Prefer concise subjects, aiming for about 72 characters when practical. Enforce a hard limit only when the repository or platform requires it.
  - No issue/PR references in the title.
- **Body structure** (use template if present; otherwise default):
  - `## Summary` — 1–3 sentences. Use [linking keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) inline (`Closes #N` / `Fixes #N` for full resolution; `Refs #N` / `See #N` for related context) — no separate `## Related` section.
  - `## Changes` — bulleted list of concrete changes.
  - `## Motivation` — why the change is needed; link triggering issue/discussion inline if not in Summary. **Omit entirely** when the Summary already links to an issue via `Closes`/`Fixes` that covers the motivation — avoid repeating what the issue already says.
  - `## Breaking changes` — **required when applicable**. Describe impact, migration path, affected consumers. Mark `**BREAKING:**` prominently. Omit entirely if none.
- **Commits-to-body consistency**: the body must cover every non-trivial commit; flag drift before confirming.

## Base branch selection

For a new PR, record `head → base`. Use an explicit user-selected base first, then applicable repository contribution or release guidance, then the upstream repository's authoritative default branch from platform metadata. Ask only when the target remains ambiguous or cannot be verified. When updating a PR, preserve its existing base unless the user requests retargeting. A familiar name such as `main` or `master` does not establish the intended base.

## Default PR template

```markdown
## Summary

<1–3 sentences: what this PR does. Put linking keywords inline here, e.g., "Closes #42 by ..." or "Refs #99".>

## Changes

- <concrete change 1>
- <concrete change 2>

## Motivation

<Why this change is needed. Link to the problem or user need inline if not already in Summary.
Omit this section when the Summary already links to an issue via Closes/Fixes that covers the motivation.>
```

If — and only if — this PR contains a breaking change, append after `## Motivation`:

```markdown
## Breaking changes

**BREAKING:** <impact, migration path, affected consumers>
```
