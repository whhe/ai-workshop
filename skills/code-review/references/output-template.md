# Review Output Template

Output the review directly in the conversation. If the user explicitly requests a file, generate as `docs/review_<branch-name>.md` (overwrite on regeneration — never append).

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| **High (blocker)** | Security vulnerability, data loss risk, correctness bug | Must block merge |
| **High** | Behavioral regression, significant SOLID violation, performance regression | Should fix before merge |
| **Medium** | Code smell, maintainability concern, minor design issue | Fix in this PR or create follow-up |
| **Low** | Style, naming, minor suggestion | Optional improvement |

## Template

```
## Code Review Summary

**Branch**: <branch> → <base>
**Files reviewed**: X files, Y lines changed
**Overall assessment**: APPROVE / REQUEST_CHANGES / COMMENT

---

## Findings

### High (blocker)
(none or numbered list)

### High
1. **[file:line — symbol]** Brief title
   - Impact area (business / security / performance / compatibility / maintainability)
   - Evidence (code snippet or diff excerpt)
   - Risk explanation
   - Suggested fix
   - Test status (verified / unverified + reason)

### Medium
2. (continue numbering across sections)

### Low
...

(If no issues found: state what was checked, areas not covered, and residual risks.)

---

## Changes Impacting Existing Logic

| Location | Original Behavior | New Behavior | Impact Scope | Risk |
|----------|-------------------|--------------|--------------|------|
| `file:line` — `symbol` | ... | ... | ... | None / Risk + reason |

## Removal / Iteration Plan
(if applicable — safe-to-remove items and deferred items)

## Fix Loop Iterations
(if Fix Loop was entered)

| Iteration | Issue Addressed | Fix Applied | Verification Result | Re-review Outcome |
|-----------|----------------|-------------|---------------------|-------------------|
| 1 | Finding #N — brief title | What changed | ✅ Pass / ❌ Fail + reason | ✅ No new issues / ⚠️ New finding #N |

## Test & Verification Notes
- Checks performed / not performed
- Language-specific checks applied

## Merge Recommendation
- Ready to merge / Mergeable after fixes / Not recommended
- Blockers (if any)
- Optional improvements (suggest splitting into separate PRs)
```

## Evidence Rules

- Every finding must include `file`, `lines`, and `symbol`. Include code snippet for High/Medium.
- Prefer quoting actual diff code over abstract descriptions.
- If a line range cannot be reliably determined, write "line range unverified" with explanation.

## Pre-Publish Self-Check

Before finalizing the report:

- Re-read the full diff to confirm no runtime / security / data-consistency issue more severe than the reported findings was missed.
- If low-risk style issues (copy, i18n, minor hardcoding) are included, verify higher-risk stability/security/compatibility issues are already covered.
- Confirm findings are ordered by severity (High blocker → High → Medium → Low).
- Eliminate cross-section duplication — the same issue should not appear in full in both "Findings" and "Changes Impacting Existing Logic."
- Confirm the heading `## Code Review Summary` appears exactly once; no duplicate top-level structure.
- For regenerated reports, verify no leftover content from the previous version.
- State whether this is a fresh review or a re-review, and which prior findings were re-checked vs. newly added.
- Verify language-specific checks were applied for all languages present in the diff; list which checks were performed in "Test & Verification Notes."
