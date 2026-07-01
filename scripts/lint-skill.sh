#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONVENTIONS="$HOME/.cursor/rules/skill-conventions.mdc"
MAX_ROUNDS=5

usage() {
  echo "Usage: $(basename "$0") <target> <skill-name>"
  echo ""
  echo "  target      repo | claude | cursor | global"
  echo "  skill-name  skill directory name (no path prefix)"
  exit 1
}

[ $# -ne 2 ] && usage

TARGET="$1"
SKILL="$2"

SKILL_DIR="$("$SCRIPT_DIR/skill-path.sh" "$TARGET" "$SKILL")"

if [ ! -d "$SKILL_DIR" ]; then
  echo "Error: skill directory not found: $SKILL_DIR" >&2
  exit 1
fi

if [ ! -f "$CONVENTIONS" ]; then
  echo "Error: conventions file not found: $CONVENTIONS" >&2
  exit 1
fi

echo "Skill:       $SKILL_DIR"
echo "Conventions: $CONVENTIONS"

round=0
while [ $round -lt $MAX_ROUNDS ]; do
  round=$((round + 1))
  echo ""
  echo "=== Round $round / $MAX_ROUNDS ==="

  PROMPT="Audit the skill at '${SKILL_DIR}' against the conventions defined in '${CONVENTIONS}'.

Follow these steps exactly:
1. Read '${CONVENTIONS}' in full.
2. Read every file inside '${SKILL_DIR}'.
3. Identify every violation of the conventions.
4. Fix each violation by editing the relevant files directly.
5. Re-read edited files to verify the fixes are correct.
6. Output exactly one status marker as the very last line of your response:
   [CONVENTIONS_PASS]  — all constraints are satisfied, nothing left to fix
   [CONVENTIONS_FAIL]  — one or more constraints could not be resolved (list them before the marker)"

  output=$(cd "$REPO_ROOT" && claude -p "$PROMPT" \
    --allowedTools "Read,Edit,Write" \
    --permission-mode bypassPermissions 2>&1)
  printf '%s\n' "$output"

  if printf '%s' "$output" | grep -qF '[CONVENTIONS_PASS]'; then
    echo ""
    echo "All constraints satisfied after $round round(s)."
    exit 0
  fi

  if ! printf '%s' "$output" | grep -qF '[CONVENTIONS_FAIL]'; then
    echo "" >&2
    echo "Warning: no status marker in output; treating as fail." >&2
  fi
done

echo "" >&2
echo "Error: skill still has unresolved issues after $MAX_ROUNDS round(s)." >&2
exit 1
