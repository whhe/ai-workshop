# code-analysis

An Agent Skill for structured source code analysis and feature deep-dive, producing evidence-backed technical documents.

## Features

- **Multi-pass analysis** — entry point discovery → dependency mapping → core flow tracing
- **Depth tiers** — scales from single-feature analysis to full-codebase architecture overview
- **Precision-first** — every conclusion cites file path and line range; trigger conditions, edge cases, and error paths are stated explicitly (never glossed over)
- **Mermaid diagrams** — component diagrams for architecture, flowcharts for branching logic, sequence diagrams for cross-component interactions
- **Structured output** — metadata table, architecture overview, per-module analysis, end-to-end flow traces, references

## How It Works

The skill guides an AI coding agent through a 4-step workflow:

1. **Scope & Depth** — determine what to analyze (feature, module, cross-module, or codebase) and target audience
2. **Structure Discovery** — three passes: entry points & boundaries, dependencies & layering, core flow tracing
3. **Compose Document** — assemble findings into a structured document with diagrams and code references
4. **Self-Check** — verify every claim has code evidence, all branches are documented, no placeholders remain

## Install

```bash
npx skills add whhe/ai-workshop --skill code-analysis --global
```

## Usage

Ask your AI coding agent to analyze code. Example prompts:

- "Analyze how the authentication flow works in this codebase"
- "Write a technical deep-dive of the payment module"
- "Trace the request lifecycle from API entry to database write"
- "Produce an architecture overview of this repository"

The agent will automatically load the skill, run the analysis passes, and produce a structured document.

## License

[MIT](../../LICENSE)
