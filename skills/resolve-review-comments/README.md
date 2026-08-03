# resolve-review-comments

An Agent Skill for end-to-end resolution of review feedback on a GitHub PR or GitLab MR.

## Features

- **Complete collection** — exhausts pagination for resolved and unresolved inline threads, general comments, all submitted review summaries including dismissed reviews, nested replies, and every terminal review-automation output observed at the triage linearization snapshot; an authoritatively expired or deleted historical output requires a tombstone plus an equivalent current-head replacement review
- **Item-level ledger** — tracks stable comment/note IDs separately from thread/discussion IDs, with per-action decisions for multi-request comments plus revisions, accepted-Skip closure evidence, exactly one reusable reply per actionable item, and transitions
- **Full triage gate** — classifies every current item and independently actionable request before code changes
- **Semantic autonomous authorization** — recognizes a clear multilingual intent to delegate one PR/MR end to end without optional repeated confirmations, records a bounded standing authorization, preserves repository-mandated post-diff commit and separate-push checkpoints, and falls back to guarded mode when publication authority or non-interruption intent is ambiguous
- **Self-contained review loop** — performs impact analysis and up to three adversarial review-fix iterations without depending on another skill
- **CI-safe publication ordering** — makes the final SHA remote and every workflow-planned context write from the frozen review snapshot except the atomic trigger-producing operation authoritative before a planned publication event can accept or release review work; delayed run start is not suppression, one selected context trigger may be deferred until remote confirmation, and every run caused by serial thread transitions is reconciled
- **Immediate transitions** — keeps the interval from push confirmation through resolve/reopen results free of unrelated work and reconciles or reverses a partially failed transition sequence without leaving its outcome implicit
- **Replay-safe writes** — uses deterministic reply markers, exact-target refreshes, visibility-bounded reconciliation, and retries only for proven non-triggering or provider-idempotent writes
- **Concurrent-publication safety** — uses an authoritatively non-triggering exclusive lease when available; otherwise freezes and revalidates optimistic guards, sends trigger-safe writes once without unsafe retry, and reports rather than conceals concurrent drift
- **GitHub/GitLab portability** — prefers provider conditional operations but includes a guarded refresh-write-verify path for standard GitHub GraphQL and GitLab REST APIs
- **Fork and worktree safety** — binds publication to the PR/MR source repository URL and full ref, isolates every pre-existing worktree or index change from implementation and verification, and executes untrusted-head code only without host credentials or default network access
- **Bounded verification** — terminally reconciles pre-existing active review runs and waits the recorded comment-visibility bound before manual dispatch, then accounts for every planned or sent-unknown trigger with one non-resetting deadline plus recorded delivery/visibility bounds

## How It Works

1. **Preflight** — parses the URL and derives a prospective guarded or bounded autonomous authorization mode from the complete request and parsed URL without keyword matching. Before any authenticated request, it checks the exact-host credential binding: guarded mode may authenticate and select or verify the exact binding, while prospective autonomous mode stops and reports if the binding is missing or ambiguous. Through the bound interface, it confirms the provider, authoritative PR/MR target, source repository URL/full ref, head SHA, and head trust boundary; then freezes the mode and, in autonomous mode, the standing envelope; records pre-existing work and finite visibility bounds; and inventories known review-automation triggers
2. **Fetch** — retrieves every review collection and nested connection to pagination completion
3. **Ledger and triage** — normalizes canonical item IDs, fingerprints current revisions, classifies every independent request within each item, and records explicit reviewer acceptance before a skipped request can become closed
4. **Implement and review** — applies minimal fixes, requires focused checks to pass, permits an explicitly accepted unverified scope only in guarded mode, and adversarially reviews the complete accumulated diff
5. **Commit and authorize** — follows trusted-base repository approval rules in every mode; mandatory post-diff commit and separate-push checkpoints cannot be waived, while other repositories may let autonomous mode validate commit and exact-push authority against the standing envelope
6. **Synchronize context** — re-fetches all items with bidirectional deletion detection, rebuilds the trigger inventory, records current metadata for compensation, and reuses one exact existing reply or publishes one replay-safe reply under a lease or guarded convergence path, preserving any documented suppression, batching, or coalescing guarantee; multiple exact matches block unless an independent grant already names the exact retain/delete IDs, and one selected context trigger may be deferred until the final SHA is remote
7. **Push and transition** — revalidates trigger evidence, conditionally pushes to the exact source repository/ref, executes any single deferred context trigger after remote confirmation, then immediately refreshes and resolves/reopens threads without unrelated work
8. **Verify** — terminally reconciles pre-existing in-flight work before any remaining manual trigger, accounts every trigger-to-run outcome, requires publication-associated runs to pass, reconciles historical outputs against their reviewed SHA and the current head, and compares visibility-window-separated snapshots within one non-resetting deadline

Before publication, every planned remote event is classified as triggering, non-triggering, or unknown. An unknown event is blocked when it could expose partial context; administrator-only metadata that is unrelated to a classified event does not globally disable the workflow. If observed behavior contradicts a classification, the workflow stops and reports that the ordering guarantee may not have held.

The final complete review-context read is the optimistic linearization snapshot. Standard refresh-write-verify APIs guarantee the ordering of the workflow's frozen publication plan, not atomic exclusion of feedback added later by external reviewers. Later drift starts a new triage/publication cycle. A contract requiring one trigger to include feedback written concurrently after that snapshot needs a provider conditional revision or an exclusive mechanism covering every review-context writer; without one, the workflow stops rather than claiming that stronger guarantee.

## Prerequisites

For GitHub CLI fallback, authenticate to the exact PR host:

```bash
gh auth login --hostname <github-host>
```

For GitLab REST fallback, bind a token with API access to one exact host:

```bash
export GITLAB_HOST=gitlab.example.com
export GITLAB_TOKEN=your_personal_access_token
```

Require the normalized MR host to equal `GITLAB_HOST` before sending the token. Derive the API base URL only after that check; never send `GITLAB_TOKEN` to a host selected solely from the MR URL.

## Install

```bash
npx skills add whhe/ai-workshop --skill resolve-review-comments --global
```

## Usage

Provide a PR or MR URL to your AI coding agent:

- "Resolve the review comments on this PR: https://github.com/owner/repo/pull/42"
- "Address all open review threads on this MR: https://gitlab.example.com/group/project/-/merge_requests/7"

These requests use guarded mode: commit, exact push, and each planned remote mutation require current-request preauthorization or explicit confirmation.

For bounded end-to-end autonomous handling:

```text
全权处理这个 PR/MR：https://github.com/owner/repo/pull/42；范围内无需重复确认，遇到阻塞直接报告。
```

Equivalent requests in any language are interpreted by their complete meaning, not by matching this phrase. Autonomous mode requires a clear PR/MR target, end-to-end delegation, publication authority, and a request not to repeat confirmation prompts. Ambiguous requests remain in guarded mode.

The default standing envelope covers triage, attributable edits and tests, replies, metadata updates, Resolve/Reopen transitions, review automation, and the exact PR/MR-scoped publication-lease lifecycle. It includes commit or exact-SHA push only when the trusted-base repository rules permit standing authorization for that operation. Repository-mandated post-diff commit confirmation and separate push confirmation remain mandatory. The envelope is bound to the current PR/MR, authoritative source repository, full ref, and attributable final SHA; optional repeated confirmation is waived only inside those bounds. Duplicate deletion and scope expansion are not included: deleting duplicates requires an independent grant naming the exact retain/delete IDs, and any expansion stops the workflow.

Autonomous mode does not bypass verification or safety gates. An unresolved Clarify, failing or unverifiable required check, unsafe attribution, unrecoverable drift, unsafe trigger ordering, ambiguous remote result, lost publication ownership, scope expansion, or destructive operation outside the envelope stops the workflow and produces a blocker report without another question.

## License

[MIT](../../LICENSE)
