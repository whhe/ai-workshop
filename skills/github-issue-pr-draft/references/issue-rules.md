# Issue Content Rules & Default Template

## Template policy

If an upstream template exists, use it. For each unchecked checkbox item:

- **User action** required (e.g., "I have signed the CLA"): ask the user.
- **Automatable** (e.g., "Searched for duplicate issues"): do it autonomously in Step 2.

If no template exists, use the default template below.

## Issue rules

- **Title**: imperative, specific, no issue/PR references; avoid emojis unless recent upstream issues use them consistently.
- **Body structure** (use template if present; otherwise default):
  - `## Description` — one-paragraph summary. Weave in related issue/PR/doc links here (or in `## Current behavior`); no separate references section.
  - `## Current behavior` — what actually happens; include redacted logs/errors.
  - `## Expected behavior` — what should happen.
  - `## Suggested direction` *(optional — only when the reporter has a concrete root-cause hypothesis)* — high-level hint only. **No** detailed fix implementations, diffs, or code snippets.
- **File references**: `relative/path/to/file.ext:LINE` or `relative/path/to/file.ext:START-END`. Fenced code block only when the exact snippet matters.

## Default issue template

```markdown
## Description

<One-paragraph summary of the problem or request. Link related issues/PRs/docs inline when they add context, e.g., "similar to #42" or "discussed in [RFC-7](...)".>

## Current behavior

<What actually happens. Include redacted logs or error messages.>

## Expected behavior

<What should happen instead.>

## Suggested direction

<Optional high-level hint, e.g., "likely in the auth middleware's token-refresh path". Remove this section if not applicable. Do NOT write diffs or detailed fix code here.>
```
