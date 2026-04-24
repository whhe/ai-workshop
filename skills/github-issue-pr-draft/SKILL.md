---
name: github-issue-pr-draft
description: "Drafts and updates GitHub issue and pull request titles and bodies. Posts to GitHub only after explicit user confirmation of the final title, body, and target. Use when the user wants to file or edit an issue, create or update a pull request, or refresh a PR description for new commits."
---

IRON LAW: Never create or update issues/PRs without explicit user confirmation of the final title, body, and target.

# GitHub Issue & PR Draft

This skill governs **content and process** only; execution-agnostic (`gh`, GitHub MCP, REST, etc.). Domain-specific rules live in `references/` and load per the **Resources** table — do not preload them.

## Workflow

| Marker | Meaning |
|--------|---------|
| `⚠️ REQUIRED` | Must not be skipped |
| `⛔ BLOCKING` | Prerequisite — blocks all subsequent steps |

- [ ] Step 1: Preflight ⚠️ REQUIRED
- [ ] Step 2: Task-Specific Context Gathering ⚠️ REQUIRED
- [ ] Step 3: Draft Content ⚠️ REQUIRED
- [ ] Step 4: Confirmation Gate ⛔ BLOCKING
- [ ] Step 5: Execute & Report ⚠️ REQUIRED

### 1. Preflight ⚠️ REQUIRED

Identify in this order:

1. **Upstream repository** — resolve `owner/repo`. If the user gave an explicit GitHub issue/PR URL or `owner/repo`, use it. Otherwise load [preflight-upstream.md](references/preflight-upstream.md) for the full resolution algorithm.
2. **Task type** — classify: Create issue / Update issue / Create PR / Update PR.
3. **Templates** — detect upstream templates:
   - Issue: `.github/ISSUE_TEMPLATE/*.md|*.yml`, `.github/ISSUE_TEMPLATE.md`, or repo issue-form config
   - PR: `.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/*.md`, or `docs/PULL_REQUEST_TEMPLATE.md`

### 2. Task-Specific Context Gathering ⚠️ REQUIRED

- **Create issue**: keyword-search upstream for duplicates (open + closed). Surface likely matches before drafting. Collect reproduction facts (environment, steps, expected vs actual).
- **Update issue**: read current state (title, body, labels, linked refs, recent comments). Identify what needs updating.
- **Create PR**: enumerate commits since base branch, summarize diff, identify linked issues, flag breaking changes.
- **Update PR**: read current PR (title, body, labels, comments, review status), enumerate new commits since last update, identify what changed.

### 3. Draft Content ⚠️ REQUIRED

Load the rules file matching the task type: [issue-rules.md](references/issue-rules.md) for issues, [pr-rules.md](references/pr-rules.md) for PRs. If the draft will include pasted logs, errors, or command output, also load [redaction.md](references/redaction.md).

### 4. Confirmation Gate ⛔ BLOCKING

Present the full draft to the user:

- Final **title** and **body** (exact markdown)
- **Target**: `owner/repo`; issue/PR number if updating; for new PRs: `head → base`
- **Side effects** (labels to add/remove)
- **Open questions** (unchecked template items requiring user input; redaction placeholders with originals)

Wait for explicit go-ahead (e.g. "create it", "update it", or the same intent in the user's language). Do not proceed on implicit or partial approval.

### 5. Execute & Report ⚠️ REQUIRED

Perform only the confirmed actions; do not bundle extra changes. Return the resulting URL(s) and numbers.

## Anti-Patterns

**Never:**

- Act without explicit user "go" (Step 4).
- Paste raw logs without applying redaction rules.
- Write fix implementations in an issue body.
- Invent template sections the upstream template lacks.
- Skip duplicate search before creating an issue.
- Include issue/PR references (`#N`, URLs) in titles — all references go in the body.

**Avoid:**

- Bundling unrelated edits into one PR update.
- Repeating points already made earlier in a thread.
- Using non-imperative verbs in issue titles ("Adding feature" → "Add feature").
- Overly vague PR subjects ("Fix bug" → "Fix null pointer exception in user authentication").

## Pre-Publish Self-Check

Before Step 4, verify:

- [ ] Title: no `#N`, `/issues/`, or `/pull/` fragments; imperative mood for issues; semantic format for PRs (`type(scope): subject`).
- [ ] Related issues/PRs: inline linking keywords only (`Closes #N`, `Fixes #N`, `Refs #N`, `See #N`); no standalone `## Related` section unless the upstream template names it.
- [ ] Content matches the **single** loaded rules file for this artifact (`issue-rules.md` or `pr-rules.md`).
- [ ] PRs: body covers every non-trivial commit; breaking changes flagged with `!` in title and `## Breaking changes` section in body.
- [ ] Issues: reproduction steps complete; expected vs actual behavior stated; environment details included.
- [ ] Pasted logs: Bucket 1 applied; Bucket 2 placeholders + originals only under Open questions.
- [ ] File refs: `path:line` or `path:start-end` format; no absolute paths.
- [ ] Template checkboxes: resolved or listed as open question.

## Resources

| File | When to load |
|------|--------------|
| [preflight-upstream.md](references/preflight-upstream.md) | Step 1 only if upstream `owner/repo` was not explicit in the user message |
| [issue-rules.md](references/issue-rules.md) | Step 3–4: issue draft or update |
| [pr-rules.md](references/pr-rules.md) | Step 3–4: PR draft or update |
| [redaction.md](references/redaction.md) | Step 3: body will include pasted logs, errors, or command output |
