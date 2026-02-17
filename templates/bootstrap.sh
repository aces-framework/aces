#!/usr/bin/env bash
# bootstrap.sh — Create a new ACES repo from templates.
#
# Usage: bootstrap.sh <repo-name> <type> [options]
#   type: rust | python | governance
#   --description "..."   Repo description (used in GitHub if --github)
#   --github              Create the GitHub repo and configure it

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORG="aces-framework"

# ── Helpers ──────────────────────────────────────────────────────────
die() { printf 'error: %s\n' "$1" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: bootstrap.sh <repo-name> <type> [options]

  repo-name   Must start with "aces-" (e.g. aces-sdl)
  type        One of: rust | python | governance

Options:
  --description "..."   Repo description
  --github              Also create GitHub repo and configure it
  -h, --help            Show this help
EOF
  exit 0
}

# Copy a template file to the target directory.
# Usage: copy_template <src-filename> [<dest-path>]
# If dest-path is omitted, the file is copied with the same name.
copy_template() {
  local src="$SCRIPT_DIR/$1"
  local dest="$TARGET_DIR/${2:-$1}"
  local dest_dir
  dest_dir="$(dirname "$dest")"
  mkdir -p "$dest_dir"
  cp "$src" "$dest"
}

# ── Parse arguments ──────────────────────────────────────────────────
REPO_NAME=""
TYPE=""
DESCRIPTION=""
DO_GITHUB=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)      usage ;;
    --description)  DESCRIPTION="$2"; shift 2 ;;
    --github)       DO_GITHUB=true; shift ;;
    -*)             die "unknown option: $1" ;;
    *)
      if [[ -z "$REPO_NAME" ]]; then
        REPO_NAME="$1"
      elif [[ -z "$TYPE" ]]; then
        TYPE="$1"
      else
        die "unexpected argument: $1"
      fi
      shift
      ;;
  esac
done

[[ -n "$REPO_NAME" ]] || die "missing required argument: repo-name"
[[ -n "$TYPE" ]]      || die "missing required argument: type"
[[ "$REPO_NAME" == aces-* ]] || die "repo name must start with 'aces-' (got: $REPO_NAME)"
[[ "$TYPE" =~ ^(rust|python|governance)$ ]] || die "invalid type: $TYPE (must be rust, python, or governance)"

if $DO_GITHUB; then
  command -v gh >/dev/null 2>&1 || die "gh CLI not found — install from https://cli.github.com"
fi

# Derived names.
SHORT_NAME="${REPO_NAME#aces-}"           # e.g. "sdl"
UNDERSCORE_NAME="${REPO_NAME//-/_}"       # e.g. "aces_sdl"
TARGET_DIR="$(pwd)/$REPO_NAME"

[[ ! -d "$TARGET_DIR" ]] || die "directory already exists: $TARGET_DIR"

echo "Creating $REPO_NAME (type: $TYPE) in $TARGET_DIR..."
mkdir -p "$TARGET_DIR"

# ── Common templates (all repo types) ────────────────────────────────
echo "  Copying common templates..."
copy_template LICENSE
copy_template CHANGELOG.md
copy_template CLAUDE.md
copy_template SECURITY.md
copy_template markdownlint.yaml .markdownlint.yaml
copy_template pull_request_template.md .github/pull_request_template.md
copy_template ISSUE_TEMPLATE/bug-report.md .github/ISSUE_TEMPLATE/bug-report.md
copy_template ISSUE_TEMPLATE/feature-request.md .github/ISSUE_TEMPLATE/feature-request.md
copy_template ISSUE_TEMPLATE/config.yml .github/ISSUE_TEMPLATE/config.yml

# ── Type-specific templates ──────────────────────────────────────────
echo "  Copying $TYPE templates..."
case "$TYPE" in
  rust)
    copy_template rust-toolchain.toml
    copy_template Cargo.toml
    copy_template cargo-deny.toml
    copy_template gitignore-rust .gitignore
    copy_template pre-commit-config-rust.yaml .pre-commit-config.yaml
    copy_template ci-rust.yaml .github/workflows/ci.yaml
    ;;
  python)
    copy_template pyproject.toml
    copy_template gitignore-python .gitignore
    copy_template pre-commit-config-python.yaml .pre-commit-config.yaml
    copy_template ci-python.yaml .github/workflows/ci.yaml
    ;;
  governance)
    copy_template pre-commit-config-governance.yaml .pre-commit-config.yaml
    copy_template ci-governance.yaml .github/workflows/ci.yaml
    ;;
esac

# ── Replace placeholders ────────────────────────────────────────────
echo "  Replacing placeholders..."

# Order matters: replace the most specific patterns first so that
# "aces-REPO_NAME" is matched before bare "REPO_NAME".
find "$TARGET_DIR" -type f | while IFS= read -r file; do
  # Skip binary files.
  if file --brief --mime-encoding "$file" | grep -q binary; then
    continue
  fi
  sed -i "s|aces_REPO_NAME|$UNDERSCORE_NAME|g" "$file"
  sed -i "s|aces-REPO_NAME|$REPO_NAME|g" "$file"
  sed -i "s|REPO_NAME|$SHORT_NAME|g" "$file"
done

# ── MCP config ──────────────────────────────────────────────────────
echo "  Creating .mcp.json (governance MCP → sibling aces/ repo)..."
cat > "$TARGET_DIR/.mcp.json" <<'MCPEOF'
{
  "mcpServers": {
    "aces-governance": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "../aces/tools/governance-mcp",
        "aces-governance-mcp"
      ]
    }
  }
}
MCPEOF

# ── Git init ─────────────────────────────────────────────────────────
echo "  Initializing git..."
git -C "$TARGET_DIR" init --initial-branch=main -q
git -C "$TARGET_DIR" add -A
git -C "$TARGET_DIR" commit -q -m "Initial commit from ACES bootstrap"

echo "  Local repo ready at $TARGET_DIR"

# ── GitHub (optional) ────────────────────────────────────────────────
if $DO_GITHUB; then
  echo "  Creating GitHub repo $ORG/$REPO_NAME..."

  gh_create_args=(
    "$ORG/$REPO_NAME"
    --public
    --source "$TARGET_DIR"
    --push
  )
  if [[ -n "$DESCRIPTION" ]]; then
    gh_create_args+=(--description "$DESCRIPTION")
  fi

  gh repo create "${gh_create_args[@]}"

  echo "  Running github-setup.sh..."
  gh_setup_args=("$ORG/$REPO_NAME" "$TYPE")
  if [[ -n "$DESCRIPTION" ]]; then
    gh_setup_args+=(--description "$DESCRIPTION")
  fi
  bash "$SCRIPT_DIR/github-setup.sh" "${gh_setup_args[@]}"
fi

echo ""
echo "Done. $REPO_NAME is ready."
