---
name: resolve-review-comments
description: "End-to-end resolution of unresolved review comments on a GitHub PR or GitLab MR: fetch open threads, triage, implement fixes following project conventions, review-fix loop (via skill or inline fallback), commit, push, mark threads resolved, and update the PR/MR description. Use when given a PR or MR URL with review comments to address."
---

IRON LAW: Every unresolved comment must be explicitly handled — as **Implement**, as **Skip** (with written technical justification), or as **Clarify** (awaiting user input). Silent omission is forbidden.

# Resolve Review Comments

## Workflow

- [ ] 1. Preflight (incl. Skill Resolution)
- [ ] 2. Fetch Unresolved Comments
- [ ] 3. Triage ⛔ GATE — blocks all subsequent steps
- [ ] 4. Implement Fixes
- [ ] 5. Review-Fix Loop (max 3 iterations)
- [ ] 6. Commit
- [ ] 7. Push & Mark Resolved
- [ ] 8. Update PR/MR Description

## Global Rules

- **Skill delegation**: At start (Skill Resolution in Step 1), scan installed skills for the categories below. Per category: one match → lock; multiple matches → present to user, let user pick, lock; no match → lock to fallback. All subsequent steps use the locked resolution — do NOT re-scan during execution.

  | Category | Use in steps | Fallback |
  |----------|-------------|----------|
  | Platform API (read/write PRs, comments, threads) | 2, 7 | `gh` CLI / GitLab REST |
  | Code review / change validation | 5 (Review-Fix Loop) | Built-in minimum checklist (§5 step 2 checks) |
  | PR/MR description drafting | 8 | Repo template or `git diff/log` |
  | Code modification | 4, 5 | N/A — always executed inline; never delegated |

- **No review metadata in outputs**: Commit messages, PR/MR title/body must never contain reviewer names, comment/thread IDs, phrases like "per review feedback"/"as suggested by"/"address review", or references to files outside this repository. All outputs must be understandable from diff + commit history alone.
- **Minimal change**: Resolve exactly what comments request. Do not refactor adjacent code unless the comment requires it.

---

### 1. Preflight (incl. Skill Resolution)

1. Detect platform: GitHub (`github.com`) or GitLab (self-hosted / `gitlab.com`).
2. Extract: `owner/repo`, PR/MR number, head branch.
3. Fetch metadata: title, body, head branch, base branch.
4. Verify local branch matches PR/MR head with no uncommitted conflicts.

Stop if local branch diverges from remote head.

5. **Skill Resolution** — execute the delegation scan described in Global Rules. Lock every category before proceeding.

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

Record per thread: thread/discussion ID (GitHub: node `id` for `resolveReviewThread` mutation — general issue comments fetched from `issues/{pr}/comments` have no such ID; mark them `reply_only`), file path + line, full comment text. Store the ID **verbatim and in full** as returned by the API — never truncate or abbreviate for display, because the same variable is used in Step 7. If you abbreviate for display, use a separate variable.

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

### 5. Review-Fix Loop (max 3 iterations)

Each iteration:

1. **Impact Analysis** (mandatory — not delegable to a skill) — map blast radius of all accumulated changes (from Step 4 and all previous iterations of this loop — do NOT scope to the latest fix only):
   - For every modified symbol: find all callers and consumers.
   - For every changed interface/contract: find all implementers and call sites.
   - For every modified file: check importing modules.
   This produces the **review scope** (changed files + affected dependents). If ripple is unexpectedly wide, report to user.

2. **Adversarial Review** — evaluate the full review scope (changed files **and** all callers, dependents, and importers from step 1) using the locked review skill with an adversarial stance.

   The review must default to "these fixes introduced new problems" and require evidence to accept. This counters confirmation bias — the natural tendency to validate fixes you know are intended to be correct. Only flag issues that would cause observable failure in production or violate a documented contract — theoretical concerns that require multiple unlikely preconditions do not count as findings.

   **Iteration equivalence**: every review iteration — whether iteration 1 or 3 — must start from the same baseline context: project structure, conventions, and the current full diff plus caller/dependent list. No prior review findings, fix rationale, or iteration history may carry forward. Only the diff content differs across iterations (it grows as fixes accumulate).

   - **Preferred**: spawn a fresh subagent per iteration (iteration equivalence is automatic — each subagent starts with zero prior context). The prompt must:
     1. Provide only the diff, affected files, and caller/dependent list from Impact Analysis — no description of the original review comments or fix rationale.
     2. Instruct: "Your job is to find problems in these changes. Default to 'this is wrong' and require evidence to accept. For each modified region, attempt to construct a realistic scenario where the code fails (e.g., edge cases, concurrency, null/empty inputs, type mismatches, caller breakage — adapt to what is relevant). Only flag issues that would cause observable failure in production or violate a documented contract — theoretical concerns that require multiple unlikely preconditions do not count. Mark clean if you cannot construct such a scenario after trying."
     3. Apply the locked review skill's regression-relevant checklist with the adversarial stance (skip architecture and cleanup passes — re-review targets regressions, not architecture or cleanup).
   - **Fallback** (subagents unavailable): to satisfy iteration equivalence, reset context before each review — discard all prior review findings, fix rationale, and iteration history, then re-read the full diff and caller/dependent list from scratch (`git diff` or `git diff <base>..HEAD`). Proceed inline with the locked review skill as if this were the first and only review, focusing on regression-relevant checks (skip architecture and cleanup passes — re-review targets regressions, not architecture or cleanup). Before each check, ask: "How could this fix be wrong?" Quality degrades across iterations as accumulated context becomes harder to discard — prefer the subagent path when available.

   At minimum check (both paths):
   - Do the changes break any caller, consumer, or dependent?
   - Are there security or correctness issues in the modified code paths or related parts?
   - Are tests added or updated for changed behavior, including at integration points?
   - Are all fixes consistent with each other and with the rest of the codebase?

3. **Verdict** — if findings: fix all issues, verify compilation + linting pass, return to Impact Analysis (step 1 of this loop). If clean: proceed to Step 6.

If cap reached with remaining findings, report to user before proceeding to Step 6.

---

### 6. Commit

1. Check for project commit convention (`commitlint.config.*`, `.gitmessage`, `CONTRIBUTING.md`). Follow if found; otherwise use Conventional Commits.
2. Separate commits for independent changes.

Commit message must comply with **No review metadata** (see Global Rules).

---

### 7. Push & Mark Resolved

Push branch, then per comment:

- **Implemented → resolve thread** (for GitHub `reply_only` threads, post a reply with a link to the fixing commit instead — `IssueComment`s cannot be resolved via the mutation).
- **Skipped → reply with technical reason, leave thread open** (reviewer must be able to respond).

Resolve API:
- GitHub: GraphQL `resolveReviewThread` mutation with thread node `id` from Step 2.
- GitLab: `PUT /projects/{id}/merge_requests/{iid}/discussions/{discussion_id}` with `{ "resolved": true }`.

**Success check**:
- GitHub GraphQL: HTTP 2xx alone is not enough — inspect the GraphQL response for an `errors` array and confirm the mutation returned the resolved thread data.
- GitLab REST: use the HTTP status code (2xx = success), **not** JSON body parsing. Response bodies from GitLab often contain non-ASCII characters (CJK text, emoji) that break naive `json.load()` in shell pipelines, causing false failure reports. A parse error on a 200 response is not a failure — do not retry.

**One call per thread/discussion**: Call the resolve API exactly once per thread/discussion ID. For GitLab, do not retry just because the response body failed to parse. Never fall back to a "short" or reconstructed ID if parsing fails — that would create a duplicate resolve event.

On genuine failure (GitHub GraphQL `errors` / missing mutation data, or non-2xx status for either platform): record thread ID, continue processing remaining threads, report all failures at end.

---

### 8. Update PR/MR Description

Update both **title** and **body**. Title must follow the project commit convention if found, otherwise Conventional Commits format — this applies regardless of which option below is used.

Priority chain (stop at first match — governs body generation):

1. **Skill available** (see Global Rules delegation table) → delegate.
2. **Repo config exists** (`.github/pull_request_template.md`, `.gitlab/merge_request_templates/`, or equivalent) → follow its structure.
3. **Neither** → generate from `git diff/log` against base branch.

Content: only repository-derivable information. Comply with **No review metadata** (Global Rules).

If no update needed, state why and skip.

---

## Pre-Delivery Self-Check

- [ ] Every unresolved comment has a decision: Implement, Skip (reason posted to thread), or Clarify (escalated to user).
- [ ] All implemented fixes compile and pass linting.
- [ ] Impact analysis (§5 step 1) identified all callers, consumers, and dependents of changed symbols.
- [ ] Review-Fix Loop (§5) completed with zero findings, or unresolved issues reported to user.
- [ ] Each commit message contains no review metadata and no references outside this repository.
- [ ] Each skipped comment has a reply with a technical reason; thread is left open.
- [ ] PR/MR title follows project commit convention (or Conventional Commits if none found).
- [ ] PR/MR body contains only repository-derivable content.
