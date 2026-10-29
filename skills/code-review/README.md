# code-review

An Agent Skill that performs risk-priority code review with proportional verification and an optional fix loop.

## Features

- **6-pass risk-priority audit** — behavioral regression, SOLID & architecture, security, performance, dead code removal, and proportional verification
- **Evidence-based findings** — every issue cites file, line range, and code evidence
- **Fix loop** — only when fixing is requested, enters a verify → fix → re-verify cycle, adding tests only when the changed risk warrants them; otherwise remains report-only
- **Adversarial re-review** — re-reads the entire accumulated change and affected callers against a frozen baseline, including commits, staged and unstaged changes, and new files
- **Language-specific checks** — Python datetime/ORM pitfalls, React hook dependency issues, JS polyfill risks
- **Structured output** — severity-ranked report with clear pass/fail per category and traceable fix iterations

## How It Works

The skill guides an AI coding agent through a structured review workflow:

1. **Preflight** — establish the review scope, freeze its baseline commit, and collect commit history, tracked changes, and new files
2. **Audit (Passes A–F)** — walk through each risk category in priority order
3. **Report** — present findings ranked by severity before any changes
4. **Fix loop** — apply minimal fixes with verification only when fixing is requested; otherwise end after the report without changes or an approval prompt
5. **Self-check** — validate the report against quality criteria before publishing

The fix loop has no fixed iteration cap: it continues until relevant verification passes and the latest full-diff re-review finds no remaining in-scope issues. Missing prerequisites, a required decision outside the authorized scope, or repeated attempts without new evidence or improvement stop the loop with a report of unresolved findings and the blocker. Iteration count alone does not require renewed authorization. Each iteration records the issue addressed, the applied fix, the verification result, and the adversarial re-review outcome.

## Install

```bash
npx skills add whhe/ai-workshop --skill code-review --global
```

## Usage

Ask your AI coding agent to review code. Example prompts:

- "Review the changes on this branch"
- "Is this PR ready to merge?"
- "Check this branch for security and performance risks"
- "Review this branch and fix all findings"
- Paste a PR URL directly

The agent will automatically load the skill, run the audit passes, and present a structured report. Review-only requests do not modify files, commit, push, update PR/MR metadata, or trigger automation. When fixing is requested, task-scoped Git operations need no separate authorization prompts under applicable Git rules; explicit local-only or no-push limits still apply.

The skill only enters the fix loop automatically when the original request clearly asks to apply fixes, such as "review and fix" or "fix all issues." Phrases like "review this fix" describe existing work and do not trigger automatic changes.

## References

The skill includes supplementary checklists loaded on demand:

| File | Purpose |
|------|---------|
| `solid-checklist.md` | SOLID smell prompts and refactor heuristics |
| `security-checklist.md` | Threat-model analysis details |
| `code-quality-checklist.md` | Stability and performance sub-checks |
| `removal-plan.md` | Safe deletion guidance for dead code |
| `output-template.md` | Report structure, severity levels, and self-check |

## License

[MIT](../../LICENSE)
