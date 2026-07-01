# code-review

An Agent Skill that performs risk-priority code review with an optional test-fix-retest closed loop.

## Features

- **6-pass risk-priority audit** — behavioral regression, SOLID & architecture, security, performance, dead code removal, test coverage
- **Evidence-based findings** — every issue cites file, line range, and code evidence
- **Fix loop** — after review, optionally enters a test → fix → retest cycle (auto when user explicitly requests fixing, otherwise user-confirmed)
- **Language-specific checks** — Python datetime/ORM pitfalls, React hook dependency issues, JS polyfill risks
- **Structured output** — severity-ranked report with clear pass/fail per category

## How It Works

The skill guides an AI coding agent through a structured review workflow:

1. **Preflight** — collect branch state, commit history, and change scope
2. **Audit (Passes A–F)** — walk through each risk category in priority order
3. **Report** — present findings ranked by severity before any changes
4. **Fix loop** — apply minimal fixes with verification (auto when user explicitly requests fixing, otherwise user-confirmed)
5. **Self-check** — validate the report against quality criteria before publishing

## Install

```bash
npx skills add whhe/ai-workshop --skill code-review --global
```

## Usage

Ask your AI coding agent to review code. Example prompts:

- "Review the changes on this branch"
- "Is this PR ready to merge?"
- "Check this branch for security and performance risks"
- Paste a PR URL directly

The agent will automatically load the skill, run the audit passes, and present a structured report.

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
