#!/usr/bin/env bash
# github-setup.sh — Configure a GitHub repo per ADR-0014 conventions.
# Idempotent: safe to re-run on an already-configured repo.
#
# Usage: github-setup.sh <org/repo> <type> [--description "..."]
#   type: rust | python | governance

set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────
die() { printf 'error: %s\n' "$1" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: github-setup.sh <org/repo> <type> [--description "..."]

  org/repo    GitHub repository (e.g. aces-framework/aces-sdl)
  type        One of: rust | python | governance

Options:
  --description "..."   Set repo description
  -h, --help            Show this help
EOF
  exit 0
}

# ── Parse arguments ──────────────────────────────────────────────────
REPO=""
TYPE=""
DESCRIPTION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage ;;
    --description) DESCRIPTION="$2"; shift 2 ;;
    -*)          die "unknown option: $1" ;;
    *)
      if [[ -z "$REPO" ]]; then
        REPO="$1"
      elif [[ -z "$TYPE" ]]; then
        TYPE="$1"
      else
        die "unexpected argument: $1"
      fi
      shift
      ;;
  esac
done

[[ -n "$REPO" ]] || die "missing required argument: org/repo"
[[ -n "$TYPE" ]] || die "missing required argument: type"
[[ "$TYPE" =~ ^(rust|python|governance)$ ]] || die "invalid type: $TYPE (must be rust, python, or governance)"

command -v gh >/dev/null 2>&1 || die "gh CLI not found — install from https://cli.github.com"

echo "Configuring $REPO (type: $TYPE)..."

# ── Repo settings ────────────────────────────────────────────────────
# Squash-merge only, delete branch on merge, auto-merge, disable wiki + projects.
repo_settings=(
  --field allow_squash_merge=true
  --field allow_merge_commit=false
  --field allow_rebase_merge=false
  --field delete_branch_on_merge=true
  --field allow_auto_merge=true
  --field has_wiki=false
  --field has_projects=false
)

if [[ -n "$DESCRIPTION" ]]; then
  repo_settings+=(--field "description=$DESCRIPTION")
fi

echo "  Setting repo options..."
gh api --method PATCH "repos/$REPO" "${repo_settings[@]}" --silent

# ── Topics ───────────────────────────────────────────────────────────
echo "  Setting topics..."
case "$TYPE" in
  rust)       topics='{"names":["aces","rust","cyber-range"]}' ;;
  python)     topics='{"names":["aces","python","cyber-range"]}' ;;
  governance) topics='{"names":["aces","governance","cyber-range"]}' ;;
esac
gh api --method PUT "repos/$REPO/topics" --input - <<< "$topics" --silent

# ── Labels ───────────────────────────────────────────────────────────
echo "  Creating labels..."
# Create label (ignore error if it already exists).
create_label() {
  gh api --method POST "repos/$REPO/labels" \
    --field "name=$1" --field "color=$2" --field "description=$3" \
    --silent 2>/dev/null || true
}

create_label "governance" "0075ca" "ADRs, RFCs, and process"

# ── Branch protection ────────────────────────────────────────────────
# Determine the required status check name from CI templates.
case "$TYPE" in
  governance) required_check="lint" ;;
  rust)       required_check="check" ;;
  python)     required_check="check" ;;
esac

echo "  Configuring branch protection on main..."
# NOTE: required_approving_review_count is 0 for now. Bump to 1 when the
# team grows beyond a single contributor.
gh api --method PUT "repos/$REPO/branches/main/protection" \
  --input - <<EOF --silent
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["$required_check"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0
  },
  "required_signatures": true,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

# ── Vulnerability reporting ──────────────────────────────────────────
echo "  Enabling private vulnerability reporting..."
gh api --method PUT "repos/$REPO/vulnerability-alerts" --silent 2>/dev/null || true
gh api --method PUT "repos/$REPO/private-vulnerability-reporting" --silent 2>/dev/null || true

echo "Done. $REPO is configured per ADR-0014 and ADR-0021."
echo ""
echo "NOTE: required_approving_review_count is 0 (solo contributor)."
echo "      Bump to 1 when the team grows: re-run this script or update manually."
