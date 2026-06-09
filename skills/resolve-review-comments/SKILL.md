---
name: resolve-review-comments
description: "End-to-end resolution of unresolved review comments on a GitHub PR or GitLab MR: fetch open threads, triage, implement fixes following project conventions, self-review, commit, push, mark threads resolved, and update the PR/MR description. Use when given a PR or MR URL with review comments to address."
---

IRON LAW: Every unresolved comment must be explicitly handled — as **Implement**, as **Skip** (with written technical justification), or as **Clarify** (awaiting user input). Silent omission is forbidden.

# Resolve Review Comments

## Workflow

| Marker | Meaning |
|--------|---------|
| `⚠️ REQUIRED` | Must not be skipped |
| `⛔ BLOCKING` | Prerequisite — blocks all subsequent steps |

- [ ] Step 1: Preflight ⚠️ REQUIRED
- [ ] Step 2: Fetch Unresolved Comments ⚠️ REQUIRED
- [ ] Step 3: Triage ⛔ BLOCKING
- [ ] Step 4: Implement Fixes ⚠️ REQUIRED
- [ ] Step 5: Self-Review Changes ⚠️ REQUIRED
- [ ] Step 6: Commit ⚠️ REQUIRED
- [ ] Step 7: Push and Mark Comments Resolved ⚠️ REQUIRED
- [ ] Step 8: Update PR/MR Description ⚠️ REQUIRED

---

### 1. Preflight ⚠️ REQUIRED

#### 1a. Skill Discovery

Before executing any step, scan the list of available skills and identify candidates for each of the following activities:

| Activity | What to look for |
|----------|-----------------|
| Platform API access (read and write: PRs, MRs, comments, resolving threads, posting replies) | Skills that interact with GitHub, GitLab, or generic VCS APIs, including write operations |
| Implementing review feedback | Skills that guide code modification or review feedback handling |
| Code review and change validation | Skills that audit code changes for correctness and regressions |
| Drafting or updating PR/MR descriptions | Skills that manage pull request or merge request content |

Record which skill (if any) is available for each activity. Use those skills in the corresponding steps below — do not re-scan later.

If no skill is found for an activity, execute that activity directly using available tools.

#### 1b. Context Setup

Parse the URL and establish context:

1. **Detect platform**: GitHub (`github.com`) or GitLab (self-hosted or `gitlab.com`).
2. **Extract identifiers**: `owner/repo`, PR or MR number, head branch name.
3. **Fetch metadata**: current title, body, head branch, base branch.
4. **Verify local state**: confirm the local branch matches the head branch and has no uncommitted changes that could conflict.

If the local branch diverges from the PR/MR head, stop and report — do not proceed.

---

### 2. Fetch Unresolved Comments ⚠️ REQUIRED

Retrieve all threads that are still open:

- **GitHub**: the REST API (`pulls/{pr}/comments`) does **not** expose resolved status. Use the GraphQL API instead — query `pullRequest.reviewThreads` and filter nodes where `isResolved: false`. Also fetch general issue comments via REST (`issues/{pr}/comments`).
- **GitLab**: fetch discussions (`merge_requests/{iid}/discussions`). Filter for entries where `resolved: false`.

For each unresolved thread, record:
- Thread/discussion ID — for GitHub GraphQL threads, this is the node `id` field (required for Step 7's `resolveReviewThread` mutation)
- File path and line (for inline comments)
- Full comment text

If there are no unresolved threads, stop and inform the user — nothing to do.

> Use the skill identified for platform API access in Step 1a, if one was found.

---

### 3. Triage ⛔ BLOCKING

Classify every comment **before touching code**:

| Decision | Meaning |
|----------|---------|
| **Implement** | Correct for this codebase — will be applied |
| **Skip** | Should not be applied — requires a specific technical reason |
| **Clarify** | Intent is unclear — must ask the user before proceeding |

Evaluation rules:

- Read the relevant file and surrounding context before deciding — do not triage from the comment text alone.
- If a suggestion would break existing behavior or callers, classify as **Skip** and state the impact.
- If a suggestion adds unused code (no callers, no references), classify as **Skip** with evidence.
- If suggestions are interdependent, identify the dependency order before marking them **Implement**.
- Do NOT start any code changes until all comments are triaged and all **Clarify** items are resolved.

**Gate**: If any comment is classified as **Skip** or **Clarify**, present the full triage table to the user and wait for all such items to be resolved before continuing.

---

### 4. Implement Fixes ⚠️ REQUIRED

Implement only comments triaged as **Implement**, in dependency order.

Before writing code:

- Check whether project coding conventions are available (look for convention rule files, `CLAUDE.md`, or equivalent). Apply them.
- Use the skill identified for implementing review feedback in Step 1a, if one was found.

For each fix:

1. Read the target file at the relevant lines.
2. Apply the minimal change that resolves the comment — do not refactor adjacent code unless the comment requires it.
3. Verify the fix compiles and passes linting before moving to the next.
4. Identify callers, dependents, and related tests. Update them if the change affects their contract.

If a fix reveals a deeper structural problem, note it for the user but apply only the minimal change now.

---

### 5. Self-Review Changes ⚠️ REQUIRED

#### 5a. Impact Analysis (mandatory — not delegatable to a skill)

Before any review begins, map the full blast radius of the changes:

1. For every modified function, type, or exported symbol, find all callers and consumers in the codebase.
2. For every changed interface or contract (API shape, return type, side effect), identify all implementers and call sites.
3. For every modified file, check whether other modules import it and depend on the affected behavior.

Collect the full list of affected files and symbols. This list is the **review scope** for Step 5b — it includes both the changed files and all related parts identified here.

If the impact analysis finds that the changes ripple further than expected, report this to the user before continuing.

#### 5b. Review–Fix Loop

Repeat until the review produces no findings, or until the cap of **3 iterations** is reached:

1. **Review** the full scope from Step 5a (changed files plus all affected related parts).
   - **If the environment supports spawning subagents, prefer using a subagent for this step.** A subagent starts with a fresh context and has no knowledge of the implementation decisions made during Steps 3–4, which reduces confirmation bias and produces a more objective assessment. Pass the full review scope from Step 5a and sufficient codebase context to the subagent; the subagent may itself use the skill identified for code review in Step 1a.
   - If subagents are not available, use the skill identified for code review and change validation in Step 1a directly, if one was found.
   - In either case, pass the complete scope from Step 5a — do not limit to directly changed files.
   - At minimum, check:
     - Do the changes break any caller, consumer, or dependent identified in Step 5a?
     - Are there security or correctness issues in the modified code paths or related parts?
     - Are tests added or updated for changed behavior, including at integration points?
     - Are the individual fixes consistent with each other and with the rest of the codebase?

2. **If findings exist**: fix every issue.
   - Use the skill identified for implementing review feedback in Step 1a, if one was found.
   - After fixing, re-run Step 5a impact analysis to check whether the fixes introduced new affected symbols, then return to step 1 of this loop.

3. **If no findings**: loop complete — proceed to Step 6.

If the cap of 3 iterations is reached and findings still remain, stop and report the unresolved issues to the user before proceeding.

---

### 6. Commit ⚠️ REQUIRED

First, check whether the project defines a commit message convention:

- Look for `commitlint.config.*`, `.gitmessage`, or commit format instructions in `CLAUDE.md`, `CONTRIBUTING.md`, or `README.md`.
- If a project-specific convention is found, follow it.
- If none is found, use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>
```

**Conventional Commits rules (fallback only):**

- `type`: `fix`, `feat`, `refactor`, `test`, `docs`, or `chore`
- `scope`: module, package, or area affected — not a PR/MR number
- `subject`: imperative mood, ≤72 characters, no trailing period
- `body`: describe *what* changed and *why* in terms of the repository content only

**What the commit message must NOT contain:**

- References to review comments, reviewer names, or thread/comment IDs
- Phrases like "as suggested by", "per review feedback", "based on reviewer's comment", "address review"
- References to files or documents outside this repository
- PR/MR URLs or platform-specific identifiers (PR numbers in the body are acceptable only when referring to this same repository)

A reader with access to only the diff and commit history must fully understand the change without needing platform access. If multiple independent changes were made, use separate commits.

---

### 7. Push and Mark Comments Resolved ⚠️ REQUIRED

Push the branch:

```bash
git push origin <branch>
```

Then handle each comment by its triage decision:

- **Implemented → mark resolved**:
  - GitHub: resolve the thread via GraphQL `resolveReviewThread` mutation, passing the thread node `id` recorded in Step 2.
  - GitLab: update the discussion (`PUT /projects/{id}/merge_requests/{iid}/discussions/{discussion_id}`, body `{ "resolved": true }`).
- **Skipped → reply and leave open**: post a reply to the thread with the technical reason from Step 3. Do NOT mark as resolved — the reviewer must be able to respond.

If any marking or reply operation fails, do not stop — record the failed thread ID, continue processing remaining threads, and report all failures at the end for the user to handle manually.

> Use the skill identified for platform API access in Step 1a, if one was found.

---

### 8. Update PR/MR Description ⚠️ REQUIRED

Evaluate whether the title and body need updating.

**Title rules:**
- Follow the same commit convention identified in Step 6. If no project convention was found, use Conventional Commits format: `type(scope): subject`.
- Update if the current title does not conform.

**Body rules — what to include:**
- Commit summaries, diff descriptions, linked issue numbers (`Closes #N`), test instructions
- Only information derivable from the repository itself

**Body rules — what to remove or never add:**
- Quoted or paraphrased review comments
- Explanations that a change was made in response to review
- Reviewer names or thread references
- References to files or documents outside the repository

If neither title nor body needs changing, state explicitly that no update was made and why.

> Use the skill identified for PR/MR description management in Step 1a, if one was found.

---

## Constraints & Anti-Patterns

**Never:**

- Mark a comment resolved without implementing its fix.
- Skip a comment without a written technical justification posted to the thread.
- Combine unrelated changes in a single commit.
- Include review metadata (commenter names, thread IDs, quoted comments) in commit messages or PR/MR body.
- Push before Step 5 self-review is complete.
- Begin implementation before Step 3 triage gate is cleared.

**Avoid:**

- Implementing suggestions without verifying them against the actual codebase.
- Over-scoping fixes — resolve exactly what the comment requests.
- Leaving `TODO` or placeholder text in modified files.
- Treating commit message and PR body as interchangeable — they have different audiences and rules.

---

## Pre-Delivery Self-Check

- [ ] Every unresolved comment has a decision: Implement, Skip (with reason posted), or Clarify (escalated to user).
- [ ] All implemented fixes compile and pass linting.
- [ ] Impact analysis (Step 5a) identified all callers, consumers, and dependents of changed symbols.
- [ ] Review–fix loop (Step 5b) completed with zero findings on the final pass, or unresolved issues were reported to the user.
- [ ] Each commit message contains no external references and no review metadata.
- [ ] Each skipped comment has a reply with a technical explanation; thread is left open.
- [ ] PR/MR title follows the project's commit convention (or Conventional Commits format if no project convention was found in Step 6).
- [ ] PR/MR body contains only repository-derivable content — no review comment references.
