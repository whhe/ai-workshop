#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

readonly DEFAULT_REPO_URL="https://github.com/whhe/ai-workshop.git"
readonly REPO_URL="${CODEX_WORKSHOP_REPO_URL:-$DEFAULT_REPO_URL}"
readonly CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
readonly WORKSHOP_DIR="${CODEX_WORKSHOP_DIR:-$CODEX_DIR/ai-workshop}"
readonly RULES_DIR="${CODEX_RULES_DIR:-$HOME/.cursor/rules}"
readonly GLOBAL_AGENTS="${CODEX_DIR}/AGENTS.md"
readonly SKILLS_AGENT="${CODEX_SKILLS_AGENT:-codex}"
SKILL_MANIFEST="${CODEX_SKILL_MANIFEST:-}"
readonly MANAGED_SKILLS_STATE="${CODEX_SKILLS_STATE:-$CODEX_DIR/ai-workshop-skills.txt}"

SKILL_SPECS=()

die() {
  echo "Error: $*" >&2
  exit 1
}

require_commands() {
  command -v git >/dev/null 2>&1 || die "git is required."
  command -v npx >/dev/null 2>&1 || die "npx is required. Install Node.js first."
  command -v node >/dev/null 2>&1 || die "node is required. Install Node.js first."
  command -v ln >/dev/null 2>&1 || die "ln is required."
}

load_skill_manifest() {
  local line manifest

  manifest="$SKILL_MANIFEST"
  if [ -z "$manifest" ]; then
    if [ -f "$WORKSHOP_DIR/scripts/codex-skills.txt" ]; then
      manifest="$WORKSHOP_DIR/scripts/codex-skills.txt"
    else
      manifest="$SCRIPT_DIR/codex-skills.txt"
    fi
  fi

  [ -f "$manifest" ] || die "Skill manifest not found: $manifest"
  SKILL_MANIFEST="$manifest"

  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      ""|\#*) continue ;;
      *\|*) SKILL_SPECS+=("$line") ;;
      *) die "Invalid skill manifest entry: $line" ;;
    esac
  done < "$SKILL_MANIFEST"

  [ "${#SKILL_SPECS[@]}" -gt 0 ] || die "Skill manifest is empty: $SKILL_MANIFEST"
}

clone_or_update_repo() {
  mkdir -p "$(dirname "$WORKSHOP_DIR")"

  if [ -d "$WORKSHOP_DIR" ]; then
    update_existing_repo
    return
  fi

  echo "Cloning repository: $REPO_URL -> $WORKSHOP_DIR"
  git clone "$REPO_URL" "$WORKSHOP_DIR"
}

update_existing_repo() {
  [ -d "$WORKSHOP_DIR" ] || die "Codex is not initialized at $WORKSHOP_DIR. Run setup-codex.sh first."
  git -C "$WORKSHOP_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || die "$WORKSHOP_DIR exists but is not a Git repository. Set CODEX_WORKSHOP_DIR to another path."

  echo "Updating repository: $WORKSHOP_DIR"
  git -C "$WORKSHOP_DIR" pull --ff-only
}

backup_existing_rule() {
  local path="$1"
  local backup="${path}.bak.$(date +%Y%m%d%H%M%S).$$"

  mv "$path" "$backup"
  echo "Backed up existing rule: $path -> $backup"
}

link_rules() {
  local source rule target target_source

  [ -d "$WORKSHOP_DIR/.cursor/rules" ] || die "Rules directory not found in $WORKSHOP_DIR."
  mkdir -p "$RULES_DIR"
  cleanup_stale_rules

  for source in "$WORKSHOP_DIR"/.cursor/rules/*.mdc; do
    [ -e "$source" ] || continue
    rule="${source##*/}"
    target="$RULES_DIR/$rule"

    if [ -L "$target" ]; then
      target_source="$(readlink "$target")"
      if [ "$target_source" != "$source" ]; then
        backup_existing_rule "$target"
        ln -s "$source" "$target"
      fi
    elif [ -e "$target" ]; then
      backup_existing_rule "$target"
      ln -s "$source" "$target"
    else
      ln -s "$source" "$target"
    fi
  done

  echo "Rules linked from $WORKSHOP_DIR/.cursor/rules to $RULES_DIR"
}

cleanup_stale_rules() {
  local target target_source

  [ -d "$RULES_DIR" ] || return 0

  for target in "$RULES_DIR"/*.mdc; do
    [ -L "$target" ] || continue
    target_source="$(readlink "$target")"
    case "$target_source" in
      "$WORKSHOP_DIR/.cursor/rules/"*)
        if [ ! -e "$target_source" ]; then
          rm -f "$target"
          echo "Removed stale rule link: $target"
        fi
        ;;
    esac
  done
}

write_global_agents() {
  local temp_file always_rule conditional_rule
  local -a always_rules=(skill-usage.mdc workflow.mdc)
  local -a conditional_rules=(coding.mdc git.mdc skill-conventions.mdc)
  temp_file="$(mktemp "${TMPDIR:-/tmp}/codex-agents.XXXXXX")"

  cat > "$temp_file" <<EOF
# Global Rule Router

These rules apply to every Codex task, regardless of the current working directory.

The rules below are maintained in the ai-workshop repository at:

- $WORKSHOP_DIR/.cursor/rules/

They are linked into $RULES_DIR so updating the repository and rerunning this script refreshes the active rules.

Before acting, load these files directly from disk:

Always load:
EOF

  for always_rule in "${always_rules[@]}"; do
    if [ -f "$WORKSHOP_DIR/.cursor/rules/$always_rule" ]; then
      printf '%s\n' "- $RULES_DIR/$always_rule" >> "$temp_file"
    fi
  done

  cat >> "$temp_file" <<EOF

Load conditionally:

EOF

  for conditional_rule in "${conditional_rules[@]}"; do
    if [ -f "$WORKSHOP_DIR/.cursor/rules/$conditional_rule" ]; then
      case "$conditional_rule" in
        coding.mdc)
          printf '%s\n' "- Creating or editing source code, scripts, or tests:" "  $RULES_DIR/$conditional_rule" >> "$temp_file"
          ;;
        git.mdc)
          printf '%s\n' "- Committing, amending, rebasing, branching, stashing, pushing, or creating/updating a PR:" "  $RULES_DIR/$conditional_rule" >> "$temp_file"
          ;;
        skill-conventions.mdc)
          printf '%s\n' "- Creating, editing, or reviewing a skill or SKILL.md:" "  $RULES_DIR/$conditional_rule" >> "$temp_file"
          ;;
      esac
    fi
  done

  cat >> "$temp_file" <<EOF

If multiple conditions match, load every matching file once, then proceed.

Any other \`.mdc\` file in $RULES_DIR is authoritative. Inspect its frontmatter and load it when its conditions match the task.
EOF

  mkdir -p "$CODEX_DIR"
  if [ -f "$GLOBAL_AGENTS" ] && cmp -s "$temp_file" "$GLOBAL_AGENTS"; then
    rm -f "$temp_file"
    echo "Global rules are already current: $GLOBAL_AGENTS"
    return
  fi
  if [ -f "$GLOBAL_AGENTS" ] && ! cmp -s "$temp_file" "$GLOBAL_AGENTS"; then
    backup_existing_rule "$GLOBAL_AGENTS"
  fi
  mv "$temp_file" "$GLOBAL_AGENTS"
  echo "Global rules written to $GLOBAL_AGENTS"
}

install_skills() {
  local spec package skill

  for spec in "${SKILL_SPECS[@]}"; do
    package="${spec%%|*}"
    skill="${spec#*|}"

    echo "Installing global skill: $skill from $package"
    npx --yes skills add "$package" --skill "$skill" --global --agent "$SKILLS_AGENT" --yes
  done
}

manifest_has_skill() {
  local candidate="$1"
  local spec

  for spec in "${SKILL_SPECS[@]}"; do
    [ "${spec#*|}" = "$candidate" ] && return 0
  done
  return 1
}

remove_stale_skills() {
  local installed old_skill

  [ -f "$MANAGED_SKILLS_STATE" ] || return 0
  installed="$(npx --yes skills list --global --agent "$SKILLS_AGENT" --json)"

  while IFS= read -r old_skill || [ -n "$old_skill" ]; do
    [ -n "$old_skill" ] || continue
    if ! manifest_has_skill "$old_skill"; then
      if json_has_skill "$old_skill" "$installed"; then
        echo "Removing retired global skill: $old_skill"
        npx --yes skills remove "$old_skill" --global --agent "$SKILLS_AGENT" --yes
      else
        echo "Retired global skill already absent: $old_skill"
      fi
    fi
  done < "$MANAGED_SKILLS_STATE"
}

json_has_skill() {
  local skill="$1"
  local installed="$2"

  printf '%s' "$installed" | SKILL_NAME="$skill" node -e '
    const fs = require("fs");
    const skill = process.env.SKILL_NAME;
    const installed = JSON.parse(fs.readFileSync(0, "utf8"));
    process.exit(installed.some((entry) => entry.name === skill) ? 0 : 1);
  '
}

reconcile_skills() {
  local spec package skill

  remove_stale_skills

  for spec in "${SKILL_SPECS[@]}"; do
    package="${spec%%|*}"
    skill="${spec#*|}"

    echo "Synchronizing global skill: $skill from $package"
    npx --yes skills add "$package" --skill "$skill" --global --agent "$SKILLS_AGENT" --yes
  done
}

write_managed_skills_state() {
  local temp_file spec
  temp_file="$(mktemp "${TMPDIR:-/tmp}/codex-skills.XXXXXX")"

  for spec in "${SKILL_SPECS[@]}"; do
    printf '%s\n' "${spec#*|}" >> "$temp_file"
  done

  mkdir -p "$CODEX_DIR"
  mv "$temp_file" "$MANAGED_SKILLS_STATE"
}

verify_skills() {
  local installed spec skill
  installed="$(npx --yes skills list --global --agent "$SKILLS_AGENT" --json)"

  for spec in "${SKILL_SPECS[@]}"; do
    skill="${spec#*|}"
    if ! json_has_skill "$skill" "$installed"; then
      die "Global skill was not installed: $skill"
    fi
  done

  echo "Verified ${#SKILL_SPECS[@]} global skills."
}

run_setup() {
  clone_or_update_repo
  load_skill_manifest
  link_rules
  write_global_agents
  remove_stale_skills
  install_skills
  verify_skills
  write_managed_skills_state
  echo "Codex setup complete. Restart Codex to load the new global rules and skills."
}

run_update() {
  update_existing_repo
  load_skill_manifest
  link_rules
  write_global_agents
  reconcile_skills
  verify_skills
  write_managed_skills_state
  echo "Codex update complete. Restart Codex to load updated global rules and skills."
}

main() {
  require_commands

  case "${1:-setup}" in
    setup)
      [ "$#" -le 1 ] || die "Usage: $0 [setup]"
      run_setup
      ;;
    update)
      [ "$#" -eq 1 ] || die "Usage: $0 update"
      run_update
      ;;
    *)
      die "Unknown command '$1'. Usage: $0 [setup|update]"
      ;;
  esac
}

main "$@"
