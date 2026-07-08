# Global Instructions

## Language

Always respond in 简体中文 unless the user explicitly asks otherwise. Use English by default for code comments, identifiers, commands, file paths, and API names.

## Rule Files

User rules are maintained at `~/.cursor/rules/`. Load them on demand.

| File | When to load |
|------|-------------|
| `workflow.mdc` | Before any non-trivial task |
| `skill-usage.mdc` | Before deciding how to approach a task |
| `coding.mdc` | Before creating or editing any source file |
| `git.mdc` | Before any git commit or rebase operation |
| `skill-conventions.mdc` | Before creating or editing a `SKILL.md` file |

## Code Reviews

Use the `code-review` skill for code reviews.
Use the `resolve-review-comments` skill for review comments.

## Git Operations

NEVER run `git commit` or `git push` without explicit user request. Always ask for confirmation before any commit or push operation.

## Package Installation

When running bare install commands outside repository-managed dependency flows, use Aliyun mirrors by default unless the user explicitly specifies otherwise.

- **pip**: `pip install -i https://mirrors.aliyun.com/pypi/simple/ <packages>`
- **npm**: `npm install --registry https://registry.npmmirror.com <packages>`
- **yarn**: `yarn config set registry https://registry.npmmirror.com`
