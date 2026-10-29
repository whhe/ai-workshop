---
name: "resolve-review-comments"
description: "Use when the user asks to address unresolved or newly added review feedback on a GitHub pull request or GitLab merge request, including follow-up comments on previously processed threads and semantically expressed requests for bounded end-to-end autonomous handling without repeated confirmations."
---

IRON LAW: When complete read-only collection and triage find no pending review work, finish with `no-action` and make no changes or review request. Only when feedback requires handling, publish in this order: local commit → replies and Resolve/Reopen transitions → required PR/MR title/body updates → push. When no code update is needed and the remote head is unchanged, publish replies and transitions, update metadata as needed, then actively trigger review. Verify every preceding operation before the trigger; never push first and resolve threads afterward.

# Resolve Review Comments

## Workflow

- [ ] 1. Preflight and review-trigger setup
- [ ] 2. Fetch complete review context ⛔ BLOCKING
- [ ] 3. Build the item ledger, triage, and evaluate the no-action exit ⛔ BLOCKING
- [ ] 4. Implement fixes
- [ ] 5. Review-fix loop until verification and full-diff review converge
- [ ] 6. Commit and obtain publication approval
- [ ] 7. Reply, transition threads, and synchronize PR/MR metadata ⛔ BLOCKING
- [ ] 8. Push new commits or actively trigger review
- [ ] 9. Verify automation and completeness

## Review-Trigger Model

Automatic review is triggered only when the PR/MR commit history changes: appending commits or force-pushing a replacement history. Replies, Resolve/Reopen transitions, and title/body edits do not automatically trigger review. A local commit changes nothing remotely; pushing the changed history is the automatic-review boundary. Pushing an unchanged head does not trigger a new review.

First evaluate the Step 3 no-action gate. The two publication paths below apply only when review feedback requires handling; absence of code changes alone does not select no-push. Prepare the complete review context before crossing the trigger boundary:

| Publication mode | Required order |
|------------------|----------------|
| Pending review work with new attributable commits to publish | Commit locally → reply and mark eligible findings resolved → update title/body as needed → push the final SHA |
| Pending review work without a code update; local and remote heads already match | Reply and mark eligible findings resolved → update title/body as needed → actively trigger review against the unchanged head |

“Reply and resolve” contains two distinct mutations: publish and verify the reply first, then apply and verify the computed thread state. Keep an unaccepted Skip open and reopen a previously resolved thread when its current disposition requires it. General comments and review summaries have no Resolve operation. Complete all replies and thread transitions before updating metadata, and verify all required context before pushing or manually triggering review.

Use the configured review integration's supported command, API, or rerun action for an active trigger. Record the exact mechanism and how its final-SHA result will be identified at preflight. No-code publication requires an active review request; an old successful run is not a substitute. Do not manufacture an empty commit or force push solely to trigger review. Replacement-history pushes remain subject to repository policy and explicit destructive-operation authorization; the trigger model is not permission to rewrite history.

If observed automation contradicts this model, stop forward publication, reconcile remote state, and report the discrepancy rather than silently adopting a push-first workflow.

## Global Rules

- **Self-contained execution**: Use `gh` for GitHub and `glab` for GitLab. Request explicit user authorization before installing a missing CLI, then recheck installation. Guide exact-host login when necessary and recheck authentication. Keep triage, changes, review, replies, and metadata drafting in this workflow; do not depend on another skill.
- **Bounded autonomous authorization**: Infer authorization from the complete request, not keywords, language, or regex. Select `autonomous` only when the request identifies one PR/MR, delegates end-to-end resolution, authorizes the necessary repository and review-system mutations, and asks to avoid repeated confirmations. Otherwise select `guarded`. Record an autonomous standing envelope for this PR/MR covering triage, attributable edits, targeted tests, replies, metadata updates, Resolve/Reopen, review triggering and observation, and the exact PR/MR-scoped publication-lease lifecycle. Include commit/push only when trusted-base repository rules permit advance authorization. Mandatory post-diff commit and separate-push checkpoints apply in every mode. Bind push authority to the authoritative source repository, full head ref, and exact attributable final SHA. Revalidate every mutation against its scope. Do not repeat optional confirmations inside the envelope. Scope expansion, unresolved Clarify, unverifiable required checks, unsafe attribution, unrecoverable drift, ambiguous remote outcomes, lost publication ownership, or an unapproved destructive operation requires stopping and reporting the exact blocker without a follow-up question in autonomous mode.
- **Complete collection**: Exhaust every page, cursor, continuation token, and nested connection before filtering. Partial results never prove completeness.
- **Minimal scope and verification**: Implement accepted feedback and required caller updates only. Reuse existing focused checks; add a targeted test only for a changed observable contract or an uncovered stable regression. Do not run broad suites or add tests solely for coverage or symmetry.
- **Change-only repository text**: Commit messages and PR/MR title/body must make sense from repository diff/history alone. Exclude reviewer names, comment IDs, “address review,” self-review/test execution reports, agent history, approval exchanges, and agent attribution.
- **Replay safety**: Refresh the exact target before a write. After ambiguity, reconcile its complete collection through the recorded visibility bound. Reuse a unique exact effect; multiple matches block further writes. Permit at most one identical retry for a proven non-triggering operation with unchanged preconditions or an operation using the same provider idempotency key. Never blindly retry a push or manual trigger.
- **Concurrent-publication safety**: Prefer an exclusive lease keyed by provider, repository stable ID, and PR/MR number; its lifecycle must not trigger review. Otherwise freeze and revalidate optimistic guards for the remote head, metadata, item fingerprints, reply targets, and thread states before each mutation. Record the lease owner token and expiry. Before every protected write, verify current ownership and enough remaining lifetime for the operation and its bounded reconciliation; renew through an authorized row before repeating freshness checks when needed. Expiry or ownership loss stops writes, including compensation. On every early stop or return after acquisition, reconcile outstanding mutations, perform only safe authorized compensation, then release and verify the lease if still owned; report any unknown release outcome. A lease coordinates only the writers it covers. Refresh-write-verify detects conflicts but does not prove atomic exclusion of external reviewers. If the requested guarantee requires inclusion of feedback written after the final snapshot, stop unless an atomic provider revision or a lease covering every context writer can enforce it.
- **Mutation authorization ledger**: Before the first remote write, freeze one row per exact operation: reply create/edit/compensating-create, duplicate delete, Resolve/Reopen and inverse, metadata update/restore, push, manual trigger, or lease acquire/renew/release. Record target, payload/state, preconditions, authorization source/scope, permitted compensation, and result. In guarded mode every row needs current-request preauthorization or explicit confirmation. In autonomous mode match the standing envelope, except repository-checkpoint approvals and independent exact-ID duplicate-delete grants. The ledger records authority; it never creates it. Revalidate substitutions and compensations before writing.
- **Untrusted-head execution**: Classify head repository and author under trusted-base repository policy; default to untrusted when policy/evidence is missing. Read workflow rules and verification commands from the trusted base. Execute untrusted code only in a credential-free, host-isolated environment without default network access. Without isolation, perform static review; guarded mode may request a trusted runner or explicit acceptance of the exact unverified scope when policy permits, while autonomous mode stops and reports.

## 1. Preflight and Review-Trigger Setup

1. Parse the exact provider and host from the PR/MR URL without sending reusable credentials. Check the matching CLI, obtain permission before any installation, and verify exact-host authentication with `gh auth status --active --hostname <host>` or `glab auth status --hostname <host>`. Continue only after both checks pass.
2. Record base/head repository stable IDs, canonical clone URLs, PR/MR number, title/body, base/head full refs, local HEAD, and authoritative remote head SHA. Bind the authenticated head-repository URL and full head ref as the push destination; never infer it from the local branch or remote name. Stop if ambiguous.
3. Freeze guarded/autonomous mode against the authoritative identity. In autonomous mode record the original request, allowed operations, exact PR/MR/repository/ref, `final SHA: pending`, mandatory repository checkpoints, and `blocker policy: stop-and-report` in the standing envelope. A mismatch with the delegated target blocks execution.
4. Start at the authoritative remote head. A detached checkout is valid with an explicit destination. If ahead, every commit/hunk must be attributable and authorized; otherwise use an isolated checkout at the remote head. Never publish from a behind or diverged base. Record pre-existing staged, unstaged, and untracked changes separately; when any exist, use an isolated worktree/index at the remote head or stop before editing. Do not unstage, overwrite, or commit baseline work. Record any required isolated-checkout preparation at preflight, but defer creating or changing a checkout until the Step 3 gate establishes pending work; a no-action result needs no checkout preparation.
5. Record head trust evidence, trusted verification instructions, and available execution isolation. Confirm the selected platform interface supports pagination, direct full-ID thread retrieval, replies, metadata, Resolve/Reopen where supported, and automation observation.
6. Inspect accessible trusted workflows/configuration, current checks/runs, integration metadata, and prior bot activity. Record the automatic commit-history trigger, actor/ref filters, exact manual-review mechanism, and run/output identification rules. Record reply and metadata writes separately from transitions. Do not treat ordinary CI as the review integration or claim no automation exists merely because none was observed. A missing active-review mechanism does not block read-only collection or a no-action exit; report it as a blocker only if triage establishes that an active review request is required.
7. Record an observation-start time, a finite total verification budget, and finite event-delivery, run-queue, and comment-visibility bounds. Preserve them across re-entry. Exhaust current related runs and bot items to establish a baseline.
8. Classify every observed run in this priority order: `must-pass` when authoritative trigger or reviewed-SHA evidence associates it with this publication or eventual final SHA; otherwise `must-reconcile` while active; otherwise `historical` when terminal. Re-evaluate on every enumeration and upgrade to `must-pass` when later evidence establishes association; never downgrade it. `must-pass` requires an acceptable terminal conclusion; other runs require output reconciliation, not a passing conclusion. Historical findings that still apply remain actionable.

## 2. Fetch Complete Review Context ⛔ BLOCKING

Record the endpoint/interface, page/batch count, and terminal no-continuation evidence for every list query.

### GitHub

Fetch GraphQL `pullRequest.reviewThreads` without filtering resolved threads, every thread's complete nested `comments`, all PR issue comments, and all submitted reviews with non-empty bodies, including `DISMISSED` reviews. Exclude only unpublished/pending reviews. REST review comments cannot replace GraphQL resolved-state collection. Issue comments and top-level review bodies are `reply_only`.

### GitLab

Fetch every discussion page and any separate notes collection. Record and skip empty-note placeholders before accessing `notes[0]`. Determine discussion type from the root note, not a discussion-level `resolved` field. Exclude system notes individually; classify every other note as follows:

| Root note | Non-system notes in the discussion |
|-----------|-------------------------------------|
| `system: true` | `general-comment`, `reply_only` |
| `system: false`, `resolvable: false` | `general-comment`, `reply_only` |
| `system: false`, `resolvable: true` | `review-thread-comment`; root note supplies resolved state |

Store full discussion IDs separately from note IDs.

### Review-Automation Outputs

Enumerate related runs again, classify new runs, and fetch complete terminal outputs: annotations, summaries, reports, and findings not published as comments. Represent each independent actionable finding in the ledger before marking its output reconciled. When an authoritative cross-reference identifies the same finding in a comment/note, link the output as Context to that canonical item rather than duplicating the action.

For an authoritatively expired/deleted/erased historical output, record a tombstone with stable run/output ID, reviewed SHA, status, exact unavailability evidence, and `body_sha256: N/A`. Plan an equivalent final-SHA replacement review through Step 8; link the tombstone to a terminal, acceptable, completely reconciled `must-pass` replacement. If equivalent scope cannot be identified or executed, stop. Unavailable `must-reconcile` or `must-pass` output does not qualify for this replacement rule.

### Canonical Identity and Revisions

Use kinds `review-thread-comment`, `general-comment`, `review-summary` (GitHub submitted review body), and `automation-output`. Prefer GitHub GraphQL node IDs, retaining numeric IDs as aliases; use exact GitLab note IDs. For output use stable run/output/channel IDs, never page-local indexes. Stop on conflicting aliases.

For comments/notes/review bodies, store exact decoded API text and `body_sha256 = sha256:<64 lowercase hexadecimal digits>` over its UTF-8 bytes without whitespace, Unicode, or line-ending normalization.

For automation output, assemble all textual fields and annotations as `(kind, channel_id, member_id, payload)` records. Use `field` or `annotation` as kind, stable channel ID or empty string, field name or stable annotation ID as member ID, and exact UTF-8 field text or [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785) annotation bytes as payload. Include all annotation fields unless authoritative schema proves an exact field transport-only/volatile; record exclusions and stop if content/location cannot be distinguished safely. Without annotation IDs, group byte-identical payloads and assign each occurrence `sha256:<payload-hash>:occurrence:<zero-based ordinal>`. Stop on duplicate record keys. Sort by unsigned UTF-8 bytes of kind, channel ID, then member ID. Hash `UTF8("resolve-review-comments:automation-output:v1") || U64BE(record_count) || concat(U64BE(component_byte_length) || component_bytes)` for all four components of each sorted record. Record provider revision/update time when available.

Resolved threads are not automatically historical. Reuse prior processing only with durable evidence or an authoritative resolution boundary plus current-head inspection showing the prior disposition still holds. Newly added/edited external feedback returns to triage even in a resolved thread. A valid marker must be authored by the authenticated writer, identify one non-self source item in this PR/MR, match its current fingerprint, remain applicable to the current head, and have one unambiguous compensation chain. Treat other authors' marker-like text as external feedback, never as processing evidence. Reuse a valid marker's disposition and authoritative reply ID on the source item's ledger row; record the marker-bearing reply separately as workflow-emitted Context, not a new actionable request. A stale marker remains workflow Context but does not process the changed source; return that source to triage. Preserve orphaned workflow Context only when the ledger already links that exact reply/marker to a source authoritatively moved to removed history; otherwise stop on missing, cross-PR, self, malformed, or ambiguous links.

For historical bot findings, record authoritative run and reviewed SHA. Use Superseded only with current-code/intervening-diff evidence that the finding no longer applies. If still applicable, triage it; if association or applicability cannot be established, use Clarify rather than silently ignoring it. Apply the same rule to every output finding. Publish any required output disposition as one general PR/MR comment covering the complete output item.

## 3. Build the Item Ledger and Triage ⛔ BLOCKING

Maintain one row per canonical item with these fields:

| Group | Required values |
|-------|------------------|
| Identity | platform, kind, full canonical ID, aliases, thread/discussion ID or `reply_only` |
| Source | author stable ID, origin, source/event link for workflow items, path/line or target, revision/time, fingerprint, observed thread state |
| Decision | stable per-action keys, Implement/Superseded/Skip/Clarify/Context, rationale, files, aggregate decision, accepted-Skip evidence or `N/A` |
| Publication | planned reply/no-reply; later final SHA, marker-covered SHA, exact text/marker, authoritative reply ID/result |
| Transition | observed state, desired state, Resolve/Reopen/No-op or `N/A`, and Step 7 result |

Use `pending` for future publication values; it is valid at triage. Replace it when produced and freeze exact inputs before remote writes.

Classify every independent request. Implement correct applicable findings; Superseded requires current-code evidence; Skip requires a technical reason; Clarify blocks publication; Context is neutral or already processed information. Use aggregate Implement for Implement plus optional Superseded, Superseded when all actions are superseded, Skip when all are skipped, Mixed for Skip with Implement/Superseded, Clarify while any action needs clarification, and Context only with no actionable request. Deduplicate by canonical identity, not similar text; preserve prior revisions as history.

A Skip becomes `accepted-Skip` only when the original reviewer or repository owner explicitly withdraws/accepts it, or authoritative actor/order evidence shows that person resolved the thread after the exact rationale was visible. Generic acknowledgements, unattributed resolutions, and automation do not qualify. Record accepting identity/time; invalidate closure if its evidence changes. Preserve the original decision/reply rather than relabeling or replying solely for closure.

Compute one desired state per thread:

- Resolved: at least one action, all Implement, Superseded, or valid accepted-Skip.
- Open: any unaccepted Skip or Clarify.
- Unchanged: neutral Context only.

Plan Resolve for open → resolved, Reopen for resolved → open, otherwise No-op. `reply_only` uses `N/A`. Plan exactly one reusable reply covering every action for each Implement/Superseded/Skip/Mixed item. Context may use no-reply unless a status response is required.

Immediately before presenting triage, repeat complete run/output and review collection, ledger all terminal findings, and freeze IDs/fingerprints/statuses as the triage snapshot. Present the complete item/action table before editing. Guarded mode requires confirmation for Skip unless already explicitly authorized and user clarification where authoritative context cannot resolve intent. Autonomous mode records Skip rationale without another prompt and stops on material unresolved Clarify.

### No-Action Exit ⛔ BLOCKING

After complete collection and triage, determine whether any feedback still needs a code change, a new or corrected disposition reply, or a Resolve/Reopen transition. Reuse valid prior processing evidence; already handled feedback with authoritative replies and the desired thread state is not pending work. An empty review and a clean result or neutral acknowledgement requiring no response qualify for `outcome: no-action`. Title/body cleanup alone does not establish pending review work.

Before declaring no-action, reconcile all observed active review runs and their complete terminal outputs within the recorded finite bounds, then refresh the authoritative head and complete review context. Re-triage drift. Partial/inaccessible collection, unresolved Clarify, unavailable output needing replacement, active runs that remain unfinished, or attributable unpublished fixes from an earlier cycle are not evidence of a clean review; report the exact blocker or resume the required handling instead.

When no pending work remains and this invocation has not already performed publication mutations, record `outcome: no-action` and finish after Step 3. Make no repository edits, commits, pushes, replies, thread transitions, metadata updates, lease acquisitions, or review requests. Report the read-only result to the user only. Skip Steps 4–9; their publication-specific completion requirements do not apply. No-action completion requires terminal pagination evidence, reconciled observed runs/outputs, no undecided or pending review work, and no workflow mutations. If this invocation already published fixes or context, continue Step 9 verification of that publication instead of using no-action to bypass it.

Only pending review work proceeds to Steps 4–9. Derive any title/body update from that work, never use an unrelated formatting opportunity to manufacture a publication cycle.

## 4. Implement Fixes

Read trusted-base instructions and surrounding code. Implement accepted actions in dependency order, including those inside Mixed items. For Superseded actions cite existing code/diff; make no no-op change.

1. Reproduce/verify with the smallest relevant check when possible.
2. Apply the minimal fix and required caller/dependent updates. Add targeted tests only when the changed contract or an uncovered stable regression warrants them; avoid duplicate tests for pure refactors, docs, configuration, or wiring.
3. Run focused compilation/lint/test/manual checks, broadening only across affected boundaries. Require contract checks and repository publication gates to pass. New/worsened failures and failures of unknown relevance block publication. A proven unrelated/pre-existing failure is non-blocking only with baseline evidence, scope, and explanation that it does not invalidate the fix; mandatory gates still apply.
4. If a required check cannot run, record exact unverified scope/impact. Guarded mode may obtain explicit acceptance only when policy permits; autonomous mode stops and reports.

## 5. Review-Fix Loop

Review the entire accumulated diff after every modification without a fixed round cap. Map callers, consumers, implementations, imports, tests, and documented contracts. Challenge authorization/tenant isolation, data loss, compatibility, null/empty inputs, concurrency, partial failure, resource bounds, inconsistent fixes, and missing discriminating tests where warranted.

When independent review is available and authorized, supply conventions, full diff, and affected-code list without a leading rationale/verdict. Otherwise perform the same evidence-driven review inline. Report only observable failures or documented-contract violations, with file/range/evidence/impact. Fix in-scope findings, rerun checks, and restart full-diff review. Record out-of-scope issues without expanding authority. Continue until verification passes and the latest full-diff review has no in-scope findings. Stop on concrete blockers or repeated attempts without new evidence/improvement; iteration count alone does not require reauthorization.

## 6. Commit and Obtain Publication Approval

1. Refresh authoritative repository URL/ref/head; stop on unexpected mapping/SHA drift. Compare worktree and index against baseline and identify attributable paths/hunks. Never stage baseline work.
2. Show the final diff and follow trusted-base commit approval rules in every mode. Mandatory post-diff confirmation cannot be waived. Otherwise guarded mode needs current-request authority or explicit approval; autonomous mode needs attributable candidates and `commit` in the envelope. No task change means no new commit.
3. Unless explicitly overridden, use English commit prose and a Conventional Commits subject (`type(scope): subject`, optional scope/`!`); documented repository format is an exception. Inspect subject/body/footers for concrete changes, rationale, behavior, compatibility, and relevant issue references only. Exclude execution reports and process/history metadata; describing changed test code is allowed, reporting its execution is not.
4. Stage only approved attributable hunks, inspect the entire cached diff, and commit locally. Use an isolated index/worktree or stop if baseline staged entries appear. Confirm remaining work matches the recorded baseline.
5. Capture the final SHA and inspect every commit plus the complete `remote_head..final_sha` diff. Prove all commits/hunks attributable. Bind the autonomous envelope to that SHA only after revalidating PR/MR/repository/ref/scope. On same-scope re-entry requiring new fixes, invalidate the prior SHA binding, restore pending, and repeat attribution before rebinding; this alone needs no renewed authorization. Identity/ref/scope mismatch invalidates authority and stops execution.
6. Re-evaluate the Step 3 no-action gate before selecting a publication mode. For pending review work, select `publication mode: push` when new attributable commits await publication; otherwise require local HEAD = authoritative remote head and select `no-push`. Never publish unattributed ahead commits or create an empty commit. In no-push mode plan an active review trigger.
7. Obtain exact-SHA/source-URL/full-ref push authority under trusted-base rules. Mandatory separate-push confirmation applies in every mode. Otherwise guarded mode requires approval, autonomous mode requires an exact envelope match. Include the exact order in approval: replies → transitions → metadata → push; label each operation separately. No-push needs no push approval/refspec, but its manual-review mutation must be authorized.

## 7. Reply, Transition Threads, and Synchronize Metadata ⛔ BLOCKING

1. Repeat complete Step 2 collection and direct processed-thread fetches. Compare IDs/fingerprints bidirectionally. New/edited/deleted external items return to triage; preserve removals as history. Missing/changed workflow effects require reconciliation, not silent recreation. Refresh exact repository/ref/head/title/body and freeze `expected_old_sha`; stop on unexpected drift.
2. Draft title/body from final diff/history and repository templates. Unless explicitly overridden, use English prose and a Conventional Commits title; an existing title/template is not itself an exception. Include concrete changes, rationale, behavior, compatibility, and issue references only. Omit process-only template sections/checklists and execution reports, including retained text/footers. Report conflicts with mandatory templates before publication.
3. Freeze final SHA, exact replies/markers, per-thread transitions/inverses, current and desired metadata, operation order, authorization ledger, and guards. Identify metadata dependent on the pending SHA. Acquire an authorized eligible lease if available; otherwise use optimistic guards. Validate the complete plan before writing.
4. Publish and authoritatively verify every required reply using the procedure below. Then execute and verify all planned Resolve/Reopen transitions serially. After those succeed, update title/body only as needed and verify exact values. All of these operations precede push or active review triggering.

### Reply Procedure

Every workflow reply is the exact human-readable reply, one LF, then a final marker line:

```text
resolve-review-comments:v1 {"platform":"github","item_kind":"review-thread-comment","item_id":"<full-id>","body_sha256":"sha256:<source-hash>","disposition":"Implement","final_sha":"<full-sha>","supersedes_reply_id":null}
```

Use canonical provider/kind/ID, current source fingerprint, aggregate disposition, and final SHA. For compensation, name the prior full reply ID. An eligible reused ancestor reply retains its original marker SHA; record the current workflow SHA separately.

Before each reply refresh the exact source and complete target replies. Return to triage if source changed/missing. Reuse one exact authenticated-writer reply/marker covering the current or prepared SHA. Reuse an ancestor marker only when the intervening diff/current code prove disposition and text remain accurate. If intended text/disposition changed, edit when supported and authorized; otherwise create one authorized compensating reply with an acyclic single-terminal chain. Stop on forks/cycles/ambiguous chains.

Post once, then re-fetch complete replies and match exact author/body/marker. Reuse one match. Multiple matches block all further reply mutations; delete only under an independent grant naming exact retain/delete IDs, refreshed and verified before each deletion. The default autonomous envelope does not authorize deletion. After ambiguity reconcile through the visibility bound; with zero matches and unchanged preconditions permit at most one identical non-triggering/provider-idempotent retry, then reconcile again.

Reply content:

- Implement: state each result and relevant Superseded evidence. Before push describe the final local SHA as the prepared fix, not as already remote; use wording still true after publication. Do not post/edit solely to announce the later push.
- Superseded: cite current code/intervening diff and state no new change was needed.
- Skip: give the technical reason. Mixed: include all applicable results/evidence/reasons in one reply.
- Context: reply only when a status response is required, with the same marker/replay rules. Clarify cannot reach publication.

Record authoritative reply IDs and upsert each as workflow-emitted Context linked to its source. Treat manual command comments separately; exact command syntax may require `marker: N/A`.

### Pre-Push Thread Transitions

Keep the ledger's computed desired states; “resolve feedback” does not override an unaccepted Skip. For each non-No-op transition:

1. Refresh remote head, exact thread/source, and applicable guards; require `expected_old_sha` in push mode or final SHA in no-push mode. The prepared local fix may not be remote yet. Verify all required replies are authoritative and exact mutation authorization still holds.
2. Use a provider conditional operation where available; otherwise exact refresh → one mutation → authoritative result/direct full-ID re-fetch. GitHub uses `resolveReviewThread` / `unresolveReviewThread`; GitLab updates the full discussion ID with `resolved=true` / `false`.
3. Verify desired state from the full thread. Process serially, recording success before the next transition. HTTP success alone is insufficient. An unchanged state after a definitive retryable failure permits one bounded retry under replay safety, then verify again; ambiguous state blocks progress.
4. Record every success/failure/cancellation and permitted inverse. After an abort, cancel unattempted transitions. Restore successful transitions in reverse order only with exact inverse authority, unchanged guards, and retained lease ownership where applicable; otherwise reconcile and report partial state. Never push or trigger review with an incomplete required transition sequence.

### Metadata and Publication Gate

After all replies/transitions succeed, refresh exact title/body and guards, apply only necessary authorized changes, and verify them. Re-fetch complete review context, thread states, metadata, and repository/ref/head. Require a bidirectional ledger match including workflow-emitted replies. External drift returns to triage; workflow-effect/metadata drift requires reconciliation and replanning. Freeze this as the final pre-trigger linearization snapshot. Without an atomic revision or a lease covering every context writer, disclose that later external feedback cannot be atomically excluded.

Before leaving Step 7, require all replies, transitions, and metadata authoritative. The last review-triggering operation remains unsent. If publication later fails or aborts, do not claim the local fixes are remote. Restore pending-SHA-dependent metadata or thread states only through authorized inverse rows and unchanged exact guards; verify compensation and report anything left prepared, partial, or unknown. Never erase truthful prepared-fix replies solely because a push failed. Lost lease ownership permits reconciliation reads, not compensation writes.

## 8. Push New Commits or Actively Trigger Review

1. Revalidate exact repository/ref, expected remote head, complete review-context snapshot, reply effects, thread states, metadata, trigger mechanism, and operation authority. If a lease is held, require enough remaining lifetime for final freshness reads, trigger dispatch/reconciliation, and bounded verification, or renew through its authorized row before repeating freshness checks. Stop/replan on drift; do not trigger against stale context.
2. Refresh observed run classifications at this boundary, preserving `must-pass`. Freeze the final SHA and complete context immediately before dispatch. Perform no unrelated work between this check and the push/manual trigger.

### Push Mode

Revalidate exact tuple approval/envelope and resolve the exact final SHA object. Push `<final_sha>:<full_head_ref>` to the authoritative source URL with a conditional lease bound to `expected_old_sha`. Never infer source from current HEAD or destination from a local branch name; never fall back to an unconditional force push. A replacement-history update additionally requires repository permission and exact destructive-operation authority.

After success or ambiguity, read the authoritative remote head. Final SHA means success. If the expected old SHA remains unchanged and no retry occurred, permit one identical leased retry and inspect again. Any other state, or failure after that retry, blocks completion: reconcile the prepared replies/thread states/metadata, perform only safe authorized compensation, and report. Record push-trigger acceptance and match the resulting final-SHA review in Step 9. Do not send a redundant manual trigger merely because the run is not immediately visible.

### Historical-Output Replacement Reviews

In push mode, after confirming the final remote SHA, reconcile the automatic review and its complete outputs within the Step 9 deadline. Close each historical-output tombstone only when an acceptable, fully reconciled final-SHA review authoritatively covers its equivalent scope. Reuse the automatic run when it qualifies. Otherwise plan an exact replacement-review mutation, verify its authorization, and use the active-trigger procedure below after repeating the complete context and remote-head checks. This is a scoped replacement, not a redundant trigger for a merely delayed automatic run. Return any newly discovered findings to triage before dispatch. In no-push mode, combine the replacement scope with the required active-review request when supported; separately authorize additional requests only for uncovered scope.

### No-Push Mode

Send no push. Confirm the remote head still equals final SHA and that all replies, transitions, and required metadata updates remain authoritative. Actively request review through the exact supported mechanism recorded at preflight. An unchanged commit history will not automatically trigger it.

Before dispatch, reconcile pre-existing active related runs and their complete outputs within the original finite budget. Wait the recorded queue/delivery/comment-visibility bounds and return new findings to triage. Preserve this cycle's required manual trigger unless an authoritative result proves that its exact planned active-review request was already accepted; a historical or unrelated successful run does not satisfy it.

### Active-Trigger Procedure

Apply this procedure to the required no-push request and any authorized historical-output replacement. Before dispatch, reconcile active related runs and repeat complete run/output and review-context collection after the delivery, queue, and comment-visibility bounds; new or changed external findings return to triage. Revalidate the exact trigger row, final remote SHA, authoritative repository/ref, metadata, replies, and thread states immediately before dispatch. Dispatch once and record acceptance/run ID. If it creates a comment/note, resolve one canonical item ID and ledger it as workflow-emitted Context linked to the trigger event; record exact author/body/window while visibility is pending. Preserve exact command syntax without a processing marker when required.

On ambiguity reconcile complete related runs/outputs and expected command comments through delivery/queue bounds. Reuse one uniquely matched effect; multiple matches block. With zero matches retry at most once only under the same provider idempotency key or documented coalescing guaranteeing one resulting run; otherwise report ambiguity without another trigger.

## 9. Verify Automation and Completeness

At the first post-publication observation, including pre-manual-trigger reconciliation, derive one absolute deadline from the preflight budget. Reuse it on every re-entry; new items/runs never reset it.

1. Exhaust related runs and bot outputs from baseline onward, repeatedly re-evaluating run classifications and upgrading final-SHA/publication-associated runs to `must-pass`. Newly observed unrelated runs remain `must-reconcile` even when already terminal until their complete output is reconciled; creation/update time alone does not establish final-SHA association. Account for the push or manual trigger with a uniquely matched final-SHA review run/output or authoritative ignored/coalesced evidence. Require at least one acceptable terminal review result authoritatively linked to this publication's push or active request, final SHA, and required review scope. An ignored dispatch without such a result is incomplete; coalescing qualifies only when it names an equivalent observed result. A historical result associated only by SHA cannot substitute for this publication's review.
2. Wait until all `must-pass` and `must-reconcile` runs are terminal and their complete outputs are reconciled. Require acceptable conclusions for `must-pass`. A failed/cancelled run is superseded only when authoritative retry/concurrency metadata names a replacement that terminates acceptably. Historical findings still require current-head reconciliation or the tombstone/replacement procedure.
3. Require the related run/output set stable through delivery/queue bounds. New runs or upgrades restart this observation, not the absolute deadline. Resolve pending manual-command comments to canonical workflow Context rows.
4. Re-fetch exact repository/ref/head/title/body, complete review context, and every processed thread including resolved threads. Require final remote SHA, desired metadata, canonical IDs/fingerprints, replies, and thread states to match the ledger. After the comment-visibility bound repeat complete run/output and context reads; require two stable snapshots within the same deadline.
5. Reconcile external additions/edits/deletions through triage, preserving removed history. Neutral acknowledgements and clean automation outputs that require no reply, code change, transition, or metadata update may be ledgered as Context and resume final verification without another publication or review request. Start a new publication cycle only when pending feedback requires a new disposition reply, code change, or transition (with any related metadata update); with no code updates it follows replies/transitions → optional metadata → active review again. Head/repository/ref drift returns to preflight; metadata/workflow-effect drift requires Step 7 reconciliation. Reuse successful reply IDs/markers and never create an empty commit.

Publication completion requires (the Step 3 no-action exit has its own read-only completion criteria):

- terminal pagination evidence for every collection and one ledger row per current item, with every independent action decided;
- authoritative IDs/results for every required reply, transition, metadata update, and active-trigger comment;
- passing contract checks and mandatory repository gates, or only policy-permitted guarded acceptance of an exact unverified scope; unrelated failures have baseline evidence and scope justification;
- every mutation matched its exact authorization row, including mandatory commit/push checkpoints, separate duplicate-delete grants, and any compensation or lease lifecycle operation;
- local commit (when needed), verified replies/transitions, and required metadata updates all preceded push; or, with no update, verified context preceded an accepted active-review request;
- final remote head, metadata, replies, and thread states match the ledger; no unpushed fix is represented as published;
- at least one acceptable terminal review result linked to this publication's trigger, final SHA, and required scope; every related run/output reconciled, historical tombstones linked to acceptable equivalent replacements, every `must-reconcile` terminal, and every `must-pass` terminal with an acceptable conclusion;
- final queue stability and two visibility-separated complete context snapshots, with external-writer race limits stated accurately.

After all other checks, execute and verify the authorized lease release and confirm this workflow no longer owns it, or record `N/A` when no lease existed. If any condition fails, report exact incomplete items, thread states, run/query outcomes, compensation results, or lease state instead of claiming success.
