---
name: code-review
description: "Risk-priority code review with test-fix-retest closed loop. Use when the user asks to review code changes, evaluate merge readiness, audit for security or performance risks, or identify regressions in a branch or PR."
---

IRON LAW: Every finding MUST cite file, line range, and code evidence. No evidence = no finding.

# Code Review — Risk-Priority with Fix Loop

## Workflow

- [ ] Step 1: Preflight ⚠️ REQUIRED
- [ ] Step 2: Risk-Priority Audit (Passes A–F) ⚠️ REQUIRED
- [ ] Step 3: Present Findings ⚠️ REQUIRED
- [ ] Step 4: Fix Loop (conditional — user confirms first)
- [ ] Step 5: Pre-Publish Self-Check ⚠️ REQUIRED

### 1. Preflight — Establish Baseline ⚠️ REQUIRED

Collect in parallel:

- Branch state: `git status --short --branch`
- Commits vs base: `git log --oneline --decorate --no-merges <base>..HEAD`
- Change scope: `git diff --stat <base>...HEAD` and `git diff --name-only <base>...HEAD`

Default `base` to `main`; override if user specifies another branch.
For a **PR URL**, use the platform API to fetch diff and metadata (description, comments, CI status).

Explore related modules, usages, contracts, entry points, ownership boundaries, and critical paths.

### 2. Risk-Priority Audit ⚠️ REQUIRED

Review **all commits** on the branch. Execute passes in order.

#### Pass A — Behavioral Regression & Compatibility

- Did any branch logic, default value, feature flag, or input/output contract change?
- Are API parameters, defaults, and legacy-data handling backward-compatible?
- Does naming/return-value semantics match the existing codebase? Flag "interface says X, implementation does Y" drift.

For every change impacting existing logic, state: original behavior → new behavior, impact scope, risk.

#### Pass B — SOLID & Architecture

- **SRP**: Does this module have exactly one reason to change?
- **OCP**: Can a new variant be added without editing existing code?
- **LSP**: Can any subclass substitute the parent without the caller knowing?
- **ISP**: Do all implementers use all interface methods?
- **DIP**: Is business logic tied to concrete I/O, storage, or hardcoded values?
- Overly loose types (`Any`/`any`/`dict`/untyped) masking domain constraints?

Prefer incremental refactor plans over large rewrites. Load [solid-checklist.md](references/solid-checklist.md) for deeper smell prompts.

#### Pass C — Security & Reliability

- Can an unauthenticated or unauthorized user reach this code path? Could tenant A's data leak to tenant B?
- What happens if two requests hit this code simultaneously? Could state change between check and act?
- If this operation fails halfway, is data left consistent?
- Unpinned deps, dependency confusion, known CVEs?
- TLS verification disabled on HTTP clients (`verify=False`, `InsecureSkipVerify`, `rejectUnauthorized: false`)?

Call out both **exploitability** and **impact**. Load [security-checklist.md](references/security-checklist.md) for deeper threat-model analysis.

#### Pass D — Performance & Stability

- What if this runs with 10×/100× data? Are resources bounded and released?
- N+1 queries? CPU-intensive work in a hot path that could be cached or batched?
- On failure: enough context to debug? Secrets leaked in logs or error output?
- What if this value is null, 0, or empty?

Load [code-quality-checklist.md](references/code-quality-checklist.md) for detailed sub-checks.

#### Pass E — Removal Candidates

- Identify unused, redundant, or feature-flagged-off code.
- Distinguish **safe delete now** vs **defer with plan**.

Load [removal-plan.md](references/removal-plan.md) if candidates are found.

#### Pass F — Test Coverage & Language-Specific Checks

- Every new behavior needs at least one happy-path and one failure/edge-case test.
- Missing tests for changed logic count as regression risk.
- Bug-fix changes need a regression test reproducing the original failure.
- Cross-module changes need integration-level coverage.
- **Assertion discriminability**: verify fixtures and assertions can distinguish real behavior from bypass/no-op — including cases where filtered and unfiltered results would look the same under the data you used, or where one happy path cannot prove a branch ran. Strengthen with cardinality, identity or negative cases, or observable effects appropriate to the feature.

Language-specific gotchas (non-obvious items the general passes may miss):

| Language | Check | Flag when | Pass |
|----------|-------|-----------|------|
| Python | Naive/aware `datetime` mixing | Naive and aware datetime objects compared, subtracted, or assigned to the same field without explicit conversion | A |
| Python | ORM lazy-load on detached instance | An ORM relationship or deferred column is accessed after the session that loaded the object is closed | D |
| Python | ORM dialect portability | Queries rely on engine-specific SQL or vendor-only functions, raw SQL fragments, or dialect-only types instead of APIs the ORM can translate for every backend the project supports. Confirm compilation or execution against each dialect/version in that supported set | A, D |
| TS/React | `useEffect`/`useMemo`/`useCallback` dependency issues | A reactive dependency is missing, redundant, or is an unstable reference (new object/array/function created each render) | D |
| JS/Node | Global patches/polyfills without guards | A monkey-patch or polyfill executes unconditionally — no environment check, feature detection, or scope isolation | A |

### 3. Present Findings ⚠️ REQUIRED

**Report first** — present findings before making any changes.
Load [output-template.md](references/output-template.md) for document structure, severity levels, and evidence rules.

After presenting, ask user how to proceed (fix all / fix High only / fix specific items / no changes). Do NOT implement changes until user confirms.

### 4. Fix Loop (conditional)

⛔ Enter only after user explicitly confirms which issues to fix. Fix only issues within review scope.

Each iteration:

1. Run the smallest relevant verification (unit tests, integration tests, or linter).
2. Apply the minimal fix (avoid introducing new behavior).
3. Re-run the same verification immediately.
4. Expand scope only if necessary.

Cap at **3 iterations**. If still unstable, stop and report the blocker.

Test strategy (adapt per project):

- **Python**: `pytest` on target test file first, then related directory.
- **Frontend**: component/page tests first, then related suites.
- **API changes**: at least one happy-path and one failure/edge-case.
- **Missing prerequisites** (command not found, deps missing): state "unverified" with impact scope; provide reproducible commands; never fake results.

### 5. Pre-Publish Self-Check ⚠️ REQUIRED

Run the self-check in [output-template.md](references/output-template.md) § Pre-Publish Self-Check before finalizing.

## Constraints & Anti-Patterns

**Never:**

- Dismiss implicit behavior changes from default-value modifications.
- Label an unverified item as "passed."
- Bypass critical checks to make tests pass (removing auth, swallowing exceptions, downgrading security).
- Commit or push without explicit user request.
- Make fixes before presenting findings.

**Avoid:**

- Listing style/naming issues before security and correctness.
- Reporting "no issues found" without listing what was checked.
- Copy-pasting code without explaining what is wrong.
- Treating all findings as equal severity.
- Guessing at behavior instead of reading actual code and diff.

## Resources

Load on demand — only when a finding needs deeper analysis.

| File | When to load |
|------|--------------|
| [solid-checklist.md](references/solid-checklist.md) | Pass B finding needs smell prompts or refactor heuristics |
| [security-checklist.md](references/security-checklist.md) | Pass C finding needs threat-model detail |
| [code-quality-checklist.md](references/code-quality-checklist.md) | Pass D finding needs stability/performance sub-checks |
| [removal-plan.md](references/removal-plan.md) | Pass E found removal candidates |
| [output-template.md](references/output-template.md) | Step 3 & 5 — document structure, evidence rules, self-check |
