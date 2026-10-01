#!/usr/bin/env bash
# One-time setup after creating a repo from this template.
# Usage: ./scripts/init-project.sh "RoleSync" [--skip-plugin]
set -euo pipefail
NAME="${1:?Usage: init-project.sh <ProjectName> [--skip-plugin]}"
SKIP_PLUGIN="${2:-}"
cd "$(dirname "$0")/.."
TODAY="$(date +%Y-%m-%d)"

echo "Filling placeholders for '$NAME'..."
for f in CLAUDE.md docs/prd.md docs/architecture.md docs/state.md \
         docs/adr/README.md docs/adr/0001-record-architecture-decisions.md \
         .specify/memory/constitution.md; do
  python3 - "$f" "$NAME" "$TODAY" <<'PY'
import sys, pathlib
p, name, today = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
t = p.read_text(encoding="utf-8")
for k, v in {"[PROJECT_NAME]": name, "[DATE]": today,
             "[RATIFICATION_DATE]": today, "[LAST_AMENDED_DATE]": today}.items():
    t = t.replace(k, v)
p.write_text(t, encoding="utf-8")
PY
done

echo "Checking tools..."
for tool in git claude specify python3; do
  command -v "$tool" >/dev/null 2>&1 || echo "WARNING: $tool not found on PATH."
done

if [[ "$SKIP_PLUGIN" != "--skip-plugin" ]] && command -v claude >/dev/null 2>&1; then
  echo "Installing Superpowers plugin (user scope)..."
  claude plugin install superpowers@claude-plugins-official
fi

cat <<'MSG'

Done. Next:
  1. Fill in docs/prd.md (problem, users, goals, non-goals)
  2. Open Claude Code and run /speckit-constitution to tailor the constitution
  3. Fill in the Commands and Stack sections of CLAUDE.md
  4. First feature: /speckit-specify
MSG
