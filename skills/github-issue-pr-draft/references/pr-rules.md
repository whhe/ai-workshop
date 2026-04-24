# PR Content Rules & Default Template

## Template policy

If an upstream template exists, use it. For each unchecked checkbox item:

- **User action** required (e.g., "I have signed the CLA"): ask the user.
- **Automatable** (e.g., "Compared diff to issue scope", "Ran tests locally"): do it autonomously in Step 2.

If no template exists, use the default template below.

## PR rules

- **Title**: [semantic commit format](https://www.conventionalcommits.org/) — `type(scope): subject`.
  - Common types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`.
  - `scope` is optional (e.g., `fix: handle empty list` is valid).
  - For breaking changes, append `!` to the type/scope (e.g., `feat(api)!: drop v1 endpoints`). Must agree with body's `## Breaking changes` section.
  - Keep `subject` ≤ 72 chars.
  - No issue/PR references in the title.
- **Body structure** (use template if present; otherwise default):
  - `## Summary` — 1–3 sentences. Use [linking keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) inline (`Closes #N` / `Fixes #N` for full resolution; `Refs #N` / `See #N` for related context) — no separate `## Related` section.
  - `## Changes` — bulleted list of concrete changes.
  - `## Motivation` — why the change is needed; link triggering issue/discussion inline if not in Summary.
  - `## Breaking changes` — **required when applicable**. Describe impact, migration path, affected consumers. Mark `**BREAKING:**` prominently. Omit entirely if none.
- **Commits-to-body consistency**: the body must cover every non-trivial commit; flag drift before confirming.

## Base branch selection

When creating a PR: `head → base`. Base selection order: use `main` if it exists on upstream; else `master`; else ask the user. Non-default long-lived branches (e.g., `develop`, release branches) require user confirmation.

## Default PR template

```markdown
## Summary

<1–3 sentences: what this PR does. Put linking keywords inline here, e.g., "Closes #42 by ..." or "Refs #99".>

## Changes

- <concrete change 1>
- <concrete change 2>

## Motivation

<Why this change is needed. Link to the problem or user need inline if not already in Summary.>
```

If — and only if — this PR contains a breaking change, append after `## Motivation`:

```markdown
## Breaking changes

**BREAKING:** <impact, migration path, affected consumers>
```
