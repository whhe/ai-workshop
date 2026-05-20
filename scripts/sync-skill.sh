#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  echo "Usage: $(basename "$0") <direction> <target> <skill-name>"
  echo ""
  echo "  direction   pull  — copy from target into repo"
  echo "              push  — copy from repo into target"
  echo "  target      claude | cursor"
  echo "  skill-name  skill directory name (no path prefix)"
  exit 1
}

[ $# -ne 3 ] && usage

DIRECTION="$1"
TARGET="$2"
SKILL="$3"

case "$DIRECTION" in
  pull|push) ;;
  *) echo "Error: direction must be 'pull' or 'push'." >&2; usage ;;
esac

case "$TARGET" in
  claude|cursor) ;;
  *) echo "Error: target must be 'claude' or 'cursor'." >&2; usage ;;
esac

REPO_PATH="$("$SCRIPT_DIR/skill-path.sh" repo     "$SKILL")"
EXT_PATH="$( "$SCRIPT_DIR/skill-path.sh" "$TARGET" "$SKILL")"

if [ "$DIRECTION" = pull ]; then
  SRC="$EXT_PATH"
  DST="$REPO_PATH"
else
  SRC="$REPO_PATH"
  DST="$EXT_PATH"
fi

if [ ! -d "$SRC" ]; then
  echo "Error: source directory not found: $SRC" >&2
  exit 1
fi

# Resolve symlinks so we copy real file content, not link targets
REAL_SRC="$(cd "$SRC" && pwd -P)"

echo "$DIRECTION: $REAL_SRC → $DST"
mkdir -p "$DST"
rsync -a --delete "$REAL_SRC/" "$DST/"
echo "Done."
