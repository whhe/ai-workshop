# resolve-review-comments

An Agent Skill for end-to-end resolution of review feedback on a GitHub PR or GitLab MR.

## Features

- **Complete collection** — exhausts pagination for resolved and unresolved inline threads, general comments, all submitted review summaries including dismissed reviews, nested replies, and every terminal review-automation output observed at the triage linearization snapshot; an authoritatively expired or deleted historical output requires a tombstone plus an equivalent current-head replacement review
- **Item-level ledger** — tracks stable comment/note IDs separately from thread/discussion IDs, with per-action decisions for multi-request comments plus revisions, accepted-Skip closure evidence, exactly one reusable reply per actionable item, and transitions
- **Full triage gate** — classifies every current item and independently actionable request before code changes; an empty or clean review with no pending work exits read-only without modifying anything or requesting another review
- **Autonomous by default** — a request to resolve feedback on an existing PR/MR covers task-scoped edits, commits, pushes, replies, metadata updates, thread transitions, and review requests without separate approval prompts; explicit report-only, local-only, or no-push limits remain binding
- **Self-contained review loop** — performs impact analysis and adversarial review-fix iterations until verification and full-diff review converge; reports concrete blockers or lack of progress instead of imposing a round limit
- **Change-only commit messages** — requires English prose and semantic subjects unless explicitly instructed otherwise, checks the complete message before committing, and excludes review/test execution reports and agent history even when installed without companion Git rules
- **Change-only PR/MR descriptions** — checks the entire desired title and body, including retained text, for English prose and semantic titles unless explicitly overridden; excludes review/test execution reports, agent history, and process-only template sections, and reports conflicts with mandatory templates before publication
- **Commit-history-triggered review** — treats appended commits and replacement-history pushes as the only automatic review triggers; replies, thread transitions, and title/body edits prepare context without automatically starting review
- **Pre-push resolution** — commits locally, publishes replies and resolves/reopens threads, updates title/body as needed, then pushes; without code updates, completes the same context preparation and actively requests review instead
- **Replay-safe writes** — uses deterministic reply markers, exact-target refreshes, visibility-bounded reconciliation, and retries only for proven non-triggering or provider-idempotent writes
- **Concurrent-publication safety** — checks lease ownership and expiry before protected writes and releases it on success or early exit; otherwise freezes and revalidates optimistic guards, sends trigger-safe writes once without unsafe retry, and reports rather than conceals concurrent drift
- **GitHub/GitLab portability** — prefers provider conditional operations but includes a guarded refresh-write-verify path for standard GitHub GraphQL and GitLab REST APIs
- **Fork and worktree safety** — binds publication to the PR/MR source repository URL and full ref, isolates every pre-existing worktree or index change from implementation and verification, and executes untrusted-head code only without host credentials or default network access
- **Bounded verification** — terminally reconciles pre-existing active review runs and waits the recorded comment-visibility bound before manual dispatch, then verifies push or active-review outcomes with one non-resetting deadline plus recorded delivery/visibility bounds

## How It Works

1. **Preflight** — parses the URL, identifies the exact host and provider, checks `gh` or `glab`, installs a missing CLI when environment policy permits or reports the prerequisite, and verifies exact-host login. Records the authoritative PR/MR, source repository URL/full ref, head SHA, trust boundary, task scope and explicit user restrictions, and review-automation triggers
2. **Fetch** — retrieves every review collection and nested connection to pagination completion
3. **Ledger and triage** — normalizes canonical item IDs, fingerprints current revisions, classifies every independent request within each item, and records explicit reviewer acceptance before a skipped request can become closed. After complete collection and reconciliation, exit with `no-action` if nothing requires handling; skip all remaining steps and make no repository or PR/MR changes, lease acquisition, or review request
4. **Implement and review** — applies minimal fixes, verifies the changed contract and repository publication gates, distinguishes new failures from evidence-backed unrelated baseline failures, stops publication on required checks that cannot be verified, and adversarially reviews the complete accumulated diff
5. **Commit and bind scope** — inspects the complete diff, commits attributable fixes locally, and binds the exact push SHA/repository/ref without separate confirmation. The publication plan places replies and Resolve/Reopen transitions before metadata updates and push
6. **Synchronize context** — re-fetches all items with bidirectional deletion detection, publishes or reuses replay-safe replies, verifies each required thread transition, and then updates title/body only as needed. Exact-target authorization, lease or optimistic guards, duplicate protection, and safe compensation apply throughout
7. **Trigger review** — with new commits, conditionally pushes the exact final SHA to the authoritative source repository/ref only after all context is verified. With no code update and an unchanged remote head, actively requests review using the configured integration's supported mechanism; an old successful run is not a substitute
8. **Verify** — reconciles pre-existing in-flight work and every related output, requires an acceptable final-SHA review result linked to the new push or manual request, and compares visibility-window-separated snapshots within one non-resetting deadline. Reuse an equivalent automatic review for missing historical output, or actively request uncovered replacement scope after push. Clean outputs and neutral acknowledgements do not trigger another publication cycle

Automatic review starts only when PR/MR commit history changes: appending new commits or force-pushing replacement history. Replies, resolving threads, and title/body edits do not automatically trigger it. First distinguish no pending feedback from feedback that needs handling:

- **No pending review work:** confirm through complete read-only collection and triage, report the result, and stop. Do not edit code, reply, transition threads, update title/body, commit, push, or trigger review. Already handled feedback and clean outputs alone do not justify another cycle. Incomplete collection or unfinished review runs are not proof of no work.

Only when feedback requires handling do the two publication paths apply:

- **With new commits:** local commit → reply and resolve eligible findings → update title/body as needed → push.
- **With pending feedback but without code updates:** reply and resolve eligible findings → update title/body as needed → actively trigger review.

No-action has its own read-only completion criteria; it does not require a new review result. If this invocation already published changes or context, it must still verify that publication. Unrelated title/body cleanup cannot create pending review work.

Unaccepted Skip findings remain open; general comments have no thread-resolution operation. Do not create empty commits or rewrite history solely to trigger review. If observed automation contradicts this trigger model, stop and report the discrepancy rather than switching to push-first resolution.

The final complete review-context read is the optimistic linearization snapshot. Standard refresh-write-verify APIs guarantee the ordering of the workflow's frozen publication plan, not atomic exclusion of feedback added later by external reviewers. Later drift starts a new triage/publication cycle. A contract requiring one trigger to include feedback written concurrently after that snapshot needs a provider conditional revision or an exclusive mechanism covering every review-context writer; without one, the workflow stops rather than claiming that stronger guarantee.

## Prerequisites

For GitHub, install `gh` and authenticate to the exact PR host:

```bash
gh auth login --hostname <github-host>
```

For GitLab, install `glab` and authenticate to the exact MR host:

```bash
glab auth login --hostname <gitlab-host>
```

The workflow checks the matching CLI and exact-host login with:

```bash
gh auth status --active --hostname <github-host>
glab auth status --hostname <gitlab-host>
```

If the matching CLI is missing, the workflow installs it through a supported package manager when environment policy permits, or reports the missing prerequisite without adding a routine authorization prompt. If its exact-host login check fails, authenticate it before continuing. The workflow repeats both checks and proceeds only after they pass.

## Install

```bash
npx skills add whhe/ai-workshop --skill resolve-review-comments --global
```

## Usage

Provide a PR or MR URL to your AI coding agent:

- "Resolve the review comments on this PR: https://github.com/owner/repo/pull/42"
- "Address all open review threads on this MR: https://gitlab.example.com/group/project/-/merge_requests/7"

These resolution requests proceed end to end by default. No special “autonomous” phrase or separate approval is needed for task-scoped edits, commits, pushes, replies, existing PR/MR title/body updates, Resolve/Reopen transitions, or review triggers. Creating a new PR/MR is outside this workflow and requires confirmation of final title, body, and target; a dedicated issue/PR drafting workflow retains its final-content confirmation gate. A read-only code review does not imply a request to fix or publish.

Explicit limits such as “report only”, “local only”, or “do not push” narrow execution. The standing scope binds operations to one authoritative PR/MR, source repository, full ref, and attributable final SHA. Remove duplicate replies only when exact IDs and byte-identical content prove they belong to this workflow; preserve reviewer content and stop on ambiguity.

Default autonomy removes routine approval exchanges, not verification or safety gates. Unresolved Clarify, failing or unavailable required checks, unsafe attribution, unrecoverable drift, ambiguous remote results, lost publication ownership, scope expansion, or unsafe destructive operations stop execution with a concrete blocker report. Platform permissions and higher-priority restrictions still apply. Empty or clean reviews retain the no-action exit.

## License

[MIT](../../LICENSE)
