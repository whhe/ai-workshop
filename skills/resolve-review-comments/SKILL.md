---
name: resolve-review-comments
description: "End-to-end resolution of unresolved review comments on a GitHub PR or GitLab MR: fetch open threads, triage, implement fixes following project conventions, self-review, commit, push, mark threads resolved, and update the PR/MR description. Use when given a PR or MR URL with review comments to address."
---

IRON LAW: Every unresolved comment must be explicitly handled — as **Implement**, as **Skip** (with written technical justification), or as **Clarify** (awaiting user input). Silent omission is forbidden.

# Resolve Review Comments

## Workflow

- [ ] 1. Preflight
- [ ] 2. Fetch Unresolved Comments
- [ ] 3. Triage ⛔ GATE — blocks all subsequent steps
- [ ] 4. Implement Fixes
- [ ] 5. Self-Review
- [ ] 6. Commit
- [ ] 7. Push & Mark Resolved
- [ ] 8. Update PR/MR Description

## Global Rules

- **Skill delegation**: At start, scan available skills for the categories below. Record matches; if none found for a category, execute directly.

  | Category | Use in steps |
  |----------|-------------|
  | Platform API (read/write PRs, comments, threads) | 2, 7 |
  | Code modification / review feedback | 4 |
  | Code review / change validation | 5 (Self-Review § 5b) |
  | PR/MR description drafting | 8 |

- **No review metadata in outputs**: Commit messages, PR/MR title/body must never contain reviewer names, comment/thread IDs, phrases like "per review feedback"/"as suggested by"/"address review", or references to files outside this repository. All outputs must be understandable from diff + commit history alone.
- **Minimal change**: Resolve exactly what comments request. Do not refactor adjacent code unless the comment requires it.

---

### 1. Preflight

1. Detect platform: GitHub (`github.com`) or GitLab (self-hosted / `gitlab.com`).
2. Extract: `owner/repo`, PR/MR number, head branch.
3. Fetch metadata: title, body, head branch, base branch.
4. Verify local branch matches PR/MR head with no uncommitted conflicts.

Stop if local branch diverges from remote head.

---

### 2. Fetch Unresolved Comments

- **GitHub**: REST (`pulls/{pr}/comments`) does NOT expose resolved status. Use GraphQL — query `pullRequest.reviewThreads`, filter `isResolved: false`. Also fetch general issue comments via REST (`issues/{pr}/comments`).
- **GitLab**: Fetch discussions (`merge_requests/{iid}/discussions`).

  ⚠️ Discussion-level `resolved` field does not exist — `d.get("resolved")` always returns `None`. The authoritative status is `notes[0].resolved`:

  | `notes[0].resolvable` | `notes[0].resolved` | Action |
  |---|---|---|
  | `false` | `null` | Skip (system event / plain comment) |
  | `true` | `false` | **Include** (unresolved) |
  | `true` | `true` | Skip (resolved) |

  Discussions with an empty `notes` array are system-generated placeholders — skip them.

Record per thread: thread/discussion ID (GitHub: node `id` for `resolveReviewThread` mutation), file path + line, full comment text.

Stop if zero unresolved threads.

---

### 3. Triage ⛔ GATE

Classify every comment before touching code:

| Decision | Criteria |
|----------|----------|
| **Implement** | Correct and applicable to this codebase |
| **Skip** | Would break callers, adds dead code, or conflicts with codebase — state technical reason |
| **Clarify** | Ambiguous intent — ask user |

Rules:
- Read target file + surrounding context before classifying.
- Identify dependency order among Implement items.
- Do NOT begin code changes until triage is complete.

**Gate**: If any Skip or Clarify exists, present full triage table to user. Wait for all to resolve before continuing.

---

### 4. Implement Fixes

Before writing code: check for project coding conventions (`CLAUDE.md`, `CONTRIBUTING.md`, convention rule files). Apply if found.

Apply Implement items in dependency order. Per fix:

1. Read target file at relevant lines.
2. Apply minimal change resolving the comment.
3. Verify compilation + linting pass.
4. Update callers, dependents, and tests if contract changed.

---

### 5. Self-Review

#### 5a. Impact Analysis (mandatory — not delegatable to a skill)

Map blast radius of all changes:
1. For every modified symbol: find all callers and consumers.
2. For every changed interface/contract: find all implementers and call sites.
3. For every modified file: check importing modules.

This produces the **review scope** (changed files + affected dependents). If ripple is unexpectedly wide, report to user.

#### 5b. Review-Fix Loop (max 3 iterations)

1. Review full scope from 5a — changed files **and** all callers, dependents, and importers identified there. Prefer subagent (fresh context reduces confirmation bias). At minimum check:
   - Do the changes break any caller, consumer, or dependent from 5a?
   - Are there security or correctness issues in the modified code paths or related parts?
   - Are tests added or updated for changed behavior, including at integration points?
   - Are all fixes consistent with each other and with the rest of the codebase?
2. If findings: fix all issues, re-run 5a, repeat.
3. If clean: proceed to Step 6.

If cap reached with remaining findings, report to user before continuing.

---

### 6. Commit

1. Check for project commit convention (`commitlint.config.*`, `.gitmessage`, `CONTRIBUTING.md`). Follow if found; otherwise use Conventional Commits.
2. Separate commits for independent changes.

Commit message must comply with **No review metadata** (see Global Rules).

---

### 7. Push & Mark Resolved

Push branch, then per comment:

- **Implemented → resolve thread.**
- **Skipped → reply with technical reason, leave thread open** (reviewer must be able to respond).

Resolve API:
- GitHub: GraphQL `resolveReviewThread` mutation with thread node `id` from Step 2.
- GitLab: `PUT /projects/{id}/merge_requests/{iid}/discussions/{discussion_id}` with `{ "resolved": true }`.

On failure: record thread ID, continue processing remaining threads, report all failures at end.

---

### 8. Update PR/MR Description

Priority chain (stop at first match):

1. **Skill available** (see Global Rules delegation table) → delegate.
2. **Repo config exists** (`.github/pull_request_template.md`, `.gitlab/merge_request_templates/`, or equivalent) → follow its structure.
3. **Neither** → generate from `git diff/log` against base branch, using Conventional Commits for title format.

Content: only repository-derivable information. Comply with **No review metadata** (Global Rules).

If no update needed, state why and skip.

---

## Pre-Delivery Self-Check

- [ ] Every unresolved comment has a decision: Implement, Skip (reason posted to thread), or Clarify (escalated to user).
- [ ] All implemented fixes compile and pass linting.
- [ ] Impact analysis (5a) identified all callers, consumers, and dependents of changed symbols.
- [ ] Review-fix loop (5b) completed with zero findings, or unresolved issues reported to user.
- [ ] Each commit message contains no review metadata and no references outside this repository.
- [ ] Each skipped comment has a reply with a technical reason; thread is left open.
- [ ] PR/MR title follows project commit convention (or Conventional Commits if none found).
- [ ] PR/MR body contains only repository-derivable content.
