---
name: code-analysis
description: "Structured source code analysis and feature deep-dive with multi-pass methodology. Use when the user asks to analyze a codebase, explain how a feature works, trace a data flow, write a code walkthrough, or produce a technical analysis document."
---

IRON LAW: Every conclusion MUST trace back to source code — cite file path, line range, and code snippet. No code evidence = no conclusion. When describing logic, NEVER gloss over trigger conditions, boundary checks, or error paths — state them explicitly.

# Code Analysis — Multi-Pass Source & Feature Deep-Dive

## Workflow

- [ ] Step 1: Scope & Depth ⛔ BLOCKING
- [ ] Step 2: Structure Discovery ⚠️ REQUIRED
- [ ] Step 3: Compose Document ⚠️ REQUIRED
- [ ] Step 4: Self-Check ⚠️ REQUIRED

### 1. Scope & Depth ⛔ BLOCKING

Clarify with the user before proceeding:

| Question | Why it matters |
|----------|----------------|
| What to analyze? | A single feature, a module, cross-module interaction, or the entire repo? |
| Target audience? | Onboarding engineer, architect, or external reviewer? Affects depth and jargon level. |
| Output destination? | Markdown file, wiki page, PR comment? Affects formatting and length. |

Determine depth tier:

| Tier | Scope | Expected output |
|------|-------|-----------------|
| **Feature** | One feature end-to-end | Entry point, flow, trigger conditions, edge cases, key code paths |
| **Module** | One module / package | Public API surface, internal structure, dependencies, data flow |
| **Cross-module** | Interaction between 2+ modules | Interface contracts, call chains, data transformations across boundaries |
| **Codebase** | Entire repository | Architecture layers, component map, 2-3 critical end-to-end flows |

If the user's request maps clearly to a tier, skip the clarification and proceed.

### 2. Structure Discovery ⚠️ REQUIRED

Execute passes in order. Depth tier determines how broadly each pass applies.

#### Pass A — Entry Points & Boundaries

Identify how the system is entered and where its boundaries lie:

- **Entry points**: HTTP handlers, CLI commands, event listeners, scheduled tasks, main functions, exported APIs.
- **External boundaries**: databases, caches, message queues, third-party services, file system.
- **Internal boundaries**: module/package interfaces, abstraction layers, plugin contracts.

For each entry point, state: trigger condition, input shape, and the first internal function it calls.

#### Pass B — Dependencies & Layering

Map the structural relationships:

- Module dependency graph (who imports whom).
- Layering: presentation → business logic → data access → infrastructure. Flag violations.
- Shared state: globals, singletons, thread-locals, caches. Note lifecycle and ownership.
- Configuration: where config is loaded, how it propagates, which values affect behavior branching.

When the dependency graph has more than 5 nodes, produce a Mermaid component diagram.

#### Pass C — Core Flow Tracing

Select 2-3 critical paths (user-facing or architecturally important) and trace each end-to-end.

For every path, cover ALL of the following:

1. **Trigger condition** — what exact condition causes entry? Cite the expression (e.g., `if request.method == "POST" and path.startswith("/api/v2")`).
2. **Normal path** — step-by-step through the happy case, noting each function call and data transformation.
3. **Branch logic** — every if/else, switch/match, and guard clause. State the semantic meaning of each branch, not just the main one.
4. **Boundary & edge cases** — null/empty/zero values, empty collections, concurrent access, timeouts, overflow. How does the code handle each? If it doesn't, flag it.
5. **Error path** — catch/fallback/retry logic: what exception is caught, how recovery works, whether side effects are rolled back.
6. **Exit condition** — what the caller receives (return value, response, event emitted) and in what state the system is left.

Use Mermaid flowcharts for paths with 3+ branches or async steps. Use sequence diagrams when the path crosses 3+ components.

### 3. Compose Document ⚠️ REQUIRED

Assemble findings into the following structure.

#### Metadata Table

Place at the very beginning of the document:

| Item | Value |
|------|-------|
| Author | `<tool>` / `<model>` |
| Created | `<YYYY-MM-DD HH:mm>` (current time) |
| Repository | HTTPS URL from `git remote get-url origin` |
| Commit | Short hash + subject, e.g. `a1b2c3d feat: add login` |

Rules:
- Author: use real tool/model name from runtime context. Fallback: `AI-assisted`. Never fabricate.
- Repository: run `git remote get-url origin`, convert SSH to HTTPS, strip `.git`.
- Commit: run `git log -1 --format='%h %s'`.

#### Document Body

Follow this fixed order:

**A. Overview** — One paragraph: what the system/feature does, who uses it, and why it exists.

**B. Architecture / Component Diagram** — Mermaid diagram showing major components and their relationships. Required for Module tier and above; optional for Feature tier.

**C. Feature / Module Analysis** — For each feature or module, present in this order:

1. **Overall Logic Flow**
   - Describe the end-to-end flow in plain language first.
   - Add a Mermaid flowchart or pseudocode block when the flow has branches, loops, or async steps.

2. **Usage & Trigger Conditions**
   - How the feature is invoked: UI entry, CLI command, scheduled task, event trigger, etc.
   - State the exact trigger expression, not just "when triggered."
   - If the feature exposes an API, document it:

     | Field | Content |
     |-------|---------|
     | Endpoint | `METHOD /path` |
     | Request params | Table: param / type / required / description |
     | Response structure | Table or JSON schema |
     | Key logic | What the endpoint does internally |
     | Request example | Curl or HTTP snippet |
     | Response example | JSON snippet |

3. **Implementation Details**
   - Prefer pseudocode + source file path over raw code.
   - Reference source code as `startLine:endLine:filepath`; keep snippets ≤ 30 lines.
   - Highlight non-obvious design decisions, trade-offs, or known limitations.
   - Cover ALL branches, not just the happy path.

**D. End-to-End Flow Traces** — The 2-3 paths traced in Pass C, presented as narrative with diagrams. Required for Cross-module and Codebase tiers; optional for Feature/Module.

**E. References** — Official docs, RFCs, design docs, ADRs, and links to key source files.

### 4. Self-Check ⚠️ REQUIRED

Run every item before delivering. Each must pass.

| # | Check | How to verify |
|---|-------|---------------|
| 1 | Every factual claim cites file path + line range | Search the document for claims without code references |
| 2 | No "when condition is met" without stating the condition | Search for vague trigger phrases |
| 3 | Every if/else and switch has all branches explained | Compare branch count in code vs document |
| 4 | Error/catch paths are described, not skipped | Search for try/catch in traced code; confirm each is documented |
| 5 | Mermaid diagrams match the text narrative | Walk through diagram nodes and verify they correspond to described steps |
| 6 | Metadata table is complete and Repository URL is clickable | Verify all four rows are filled |
| 7 | Author field uses real tool/model names, not fabricated | Confirm values match runtime context; if unknown, must say `AI-assisted` |

## Precision Requirements

These rules apply throughout the entire workflow — discovery, composition, and self-check.

### Trigger Conditions

State the exact predicate, not a summary. Cite the source expression.

- BAD: "When validation fails, an exception is thrown."
- GOOD: "When `age < 0` or `age > 150`, raises `ValidationError('age out of range')` (`validators.py:23`). The caller in `controller.py:45` catches it and returns HTTP 400."

### Branch Logic

Document every branch, not just the primary path.

- BAD: "The function processes the request and returns a response."
- GOOD: "If `user.is_admin` (`handler.py:30`), bypasses rate limiting and calls `admin_process()`. Otherwise, checks `rate_limiter.allow(user.id)` (`handler.py:33`): if allowed, calls `standard_process()`; if denied, returns HTTP 429 with `Retry-After` header."

### Boundary & Edge Cases

Enumerate each boundary explicitly (null, empty, zero, overflow, concurrent). Never use "etc." or "and other edge cases." If no guard exists, flag it as a potential runtime error.

### Error Paths

For every catch/fallback/retry: state what is caught, recovery mechanism, and whether side effects persist or roll back.

## Anti-Patterns

- Paste 50+ lines of raw source code without summarizing the logic.
- Write "handles errors appropriately" or "processes the data" without specifics.
- Describe only the happy path and skip else/default/catch branches.
- Use "etc.", "and so on", or "other edge cases" to avoid enumerating boundaries.
- Claim behavior without citing a file path and line range.
- Produce a diagram that contradicts or omits steps described in the text.
- List every function signature without explaining data flow between them.
- Describe what code "is" (structure catalog) without explaining what it "does" (behavior trace).
