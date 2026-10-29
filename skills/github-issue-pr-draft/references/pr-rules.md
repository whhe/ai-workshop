# PR Content Rules & Default Template

## Template policy

Use the upstream template's change-related sections when present; otherwise use the default template below. The change-only content rules apply to the entire title and body, including template checklists and footers.

- Omit sections and checklists about review, testing execution/results, approvals, or agent workflow. Do not fill them with status claims or placeholder text.
- If the repository explicitly requires such content, surface the conflict separately to the user before publication; do not silently include forbidden content or claim template compliance.
- Perform applicable verification as part of the workflow; report its process and results only in the user conversation, outside the draft body.

## Language and content boundary

- Unless explicitly instructed otherwise, write all PR title, body, and footer prose in **English**. The conversation's language alone does not override this default. Preserve exact identifiers, proper names, and quoted user-facing strings as needed, with English surrounding prose.
- Include only concrete changes, their rationale, resulting behavior, and compatibility or migration impact. Relevant issue references may accompany these descriptions.
- Never include self-review or self-test procedures/results, check commands or logs, agent conversation history, plans, approval exchanges, agent attribution, or unrelated metadata. Claims such as "all tests passed" and "self-review found no issues" do not belong in the title or body.
- Describe added or changed test code as a change (e.g., "Add regression coverage for empty input"); omit execution reports (e.g., "Ran pytest; all tests passed").

## PR rules

- **Title**: unless explicitly instructed otherwise by the user or documented repository requirements, **require** [semantic commit format](https://www.conventionalcommits.org/) — `type(scope): subject`. A template or an existing non-semantic title alone is not an exception.
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
