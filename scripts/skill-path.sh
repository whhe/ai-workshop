#!/usr/bin/env bash
# Outputs the absolute path to a skill for a given target.
# Usage: skill-path.sh <target> <skill-name>
# Targets: repo | claude | cursor
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[ $# -ne 2 ] && {
  echo "Usage: $(basename "$0") <target> <skill-name>" >&2
  echo "Targets: repo | claude | cursor" >&2
  exit 1
}

target="$1"
skill="$2"

case "$target" in
  repo)   echo "$REPO_ROOT/skills/$skill" ;;
  claude) echo "$HOME/.claude/skills/$skill" ;;
  cursor) echo "$HOME/.cursor/skills/$skill" ;;
  *)
    echo "Error: unknown target '$target'. Use repo, claude, or cursor." >&2
    exit 1
    ;;
esac
