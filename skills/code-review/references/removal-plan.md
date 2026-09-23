# Removal & Iteration Plan Template

## Safe to Remove Now

| Field | Details |
|-------|---------|
| **Location** | `path/to/file:line` |
| **Rationale** | Why this should be removed |
| **Evidence** | Unused (no references), dead feature flag, deprecated API |
| **Impact** | None / Low — no active consumers |
| **Deletion steps** | 1. Remove code 2. Update tests whose expectations are obsolete; remove tests only when they exclusively cover that code 3. Remove config only when no active consumer remains |
| **Verification** | Run the smallest relevant existing checks, confirm no active references remain, and use runtime monitoring when the change warrants it |

## Defer Removal (Plan Required)

| Field | Details |
|-------|---------|
| **Location** | `path/to/file:line` |
| **Why defer** | Active consumers, needs migration, stakeholder sign-off |
| **Preconditions** | Feature flag off for N weeks, telemetry shows 0 usage |
| **Breaking changes** | List any API/contract changes |
| **Migration plan** | Steps for consumers to migrate |
| **Timeline** | Target date or sprint |
| **Owner** | Person/team responsible |
| **Rollback plan** | How to restore if issues found |

## Pre-Removal Checklist

- [ ] Searched codebase for all references
- [ ] Checked for dynamic/reflection-based usage
- [ ] Verified no external consumers (APIs, SDKs, docs)
- [ ] Feature flag telemetry reviewed (if applicable)
- [ ] Tests updated when expectations became obsolete; tests removed only when they directly cover deleted code; shared tests preserved
- [ ] Documentation updated
- [ ] Team notified (if shared code)
