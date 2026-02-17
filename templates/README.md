# ACES Repo Templates

Base templates for bootstrapping new ACES repos. Copy and customize for
each repo — sections marked `REPO-SPECIFIC` need to be replaced.

## Quick Start

Create a new repo with a single command:

```bash
# Rust repo (local only)
./templates/bootstrap.sh aces-myrepo rust

# Python repo with GitHub setup
./templates/bootstrap.sh aces-myrepo python --github --description "My new repo"

# Configure an existing GitHub repo
./templates/github-setup.sh aces-framework/aces-myrepo rust
```

The bootstrap script copies templates, replaces placeholders, initializes
git, and optionally creates and configures the GitHub repo. See the manual
checklist below for what the script does under the hood.

## File Inventory

| Template | Purpose | Used By | Destination |
|----------|---------|---------|-------------|
| `bootstrap.sh` | Create a new ACES repo | Scripts | N/A (run from templates/) |
| `github-setup.sh` | Configure GitHub repo per ADR-0014 | Scripts | N/A (run from templates/) |
| `CLAUDE.md` | Agent instructions | All repos | `CLAUDE.md` |
| `CHANGELOG.md` | Changelog scaffold | All repos | `CHANGELOG.md` |
| `LICENSE` | Apache-2.0 full text | All repos | `LICENSE` |
| `SECURITY.md` | Vulnerability disclosure policy | All repos | `SECURITY.md` |
| `markdownlint.yaml` | Markdownlint config | All repos | `.markdownlint.yaml` |
| `pull_request_template.md` | PR template | All repos | `.github/pull_request_template.md` |
| `ISSUE_TEMPLATE/bug-report.md` | Bug report | All repos | `.github/ISSUE_TEMPLATE/bug-report.md` |
| `ISSUE_TEMPLATE/feature-request.md` | Feature request | All repos | `.github/ISSUE_TEMPLATE/feature-request.md` |
| `ISSUE_TEMPLATE/config.yml` | Blank issues | All repos | `.github/ISSUE_TEMPLATE/config.yml` |
| `rust-toolchain.toml` | Pin Rust MSRV | Rust repos | `rust-toolchain.toml` |
| `Cargo.toml` | Crate manifest skeleton | Rust repos | `Cargo.toml` |
| `cargo-deny.toml` | Dependency policy | Rust repos | `cargo-deny.toml` |
| `gitignore-rust` | Git ignores | Rust repos | `.gitignore` |
| `ci-rust.yaml` | GitHub Actions CI | Rust repos | `.github/workflows/ci.yaml` |
| `pre-commit-config-rust.yaml` | Pre-commit hooks | Rust repos | `.pre-commit-config.yaml` |
| `pyproject.toml` | Python project manifest | Python repos | `pyproject.toml` |
| `gitignore-python` | Git ignores | Python repos | `.gitignore` |
| `ci-python.yaml` | GitHub Actions CI | Python repos | `.github/workflows/ci.yaml` |
| `pre-commit-config-python.yaml` | Pre-commit hooks | Python repos | `.pre-commit-config.yaml` |
| `ci-governance.yaml` | GitHub Actions CI | Markdown-only repos | `.github/workflows/ci.yaml` |
| `pre-commit-config-governance.yaml` | Pre-commit hooks | Markdown-only repos | `.pre-commit-config.yaml` |

## Setup Checklist

### All Repos

1. Copy `LICENSE` to repo root.
2. Copy `CHANGELOG.md` to repo root.
3. Copy `CLAUDE.md` to repo root, fill in `REPO-SPECIFIC` sections.
4. Copy `SECURITY.md` to repo root (placeholders replaced by bootstrap).
5. Copy `markdownlint.yaml` as `.markdownlint.yaml`.
6. Copy `pull_request_template.md` to `.github/pull_request_template.md`
   and customize the type checkboxes and checklist.
7. Copy `ISSUE_TEMPLATE/` contents to `.github/ISSUE_TEMPLATE/` and add
   any repo-specific issue templates.
8. Enable branch protection on `main` per ADR-0014.

### Rust Repos (additional steps)

1. Copy `gitignore-rust` as `.gitignore`. For binary crates, remove the
   `Cargo.lock` line so the lock file is committed.
2. Copy `rust-toolchain.toml` to repo root.
3. Copy `Cargo.toml` to repo root. Replace `REPO_NAME` and
   `REPO-SPECIFIC` placeholders.
4. Copy `cargo-deny.toml` to repo root.
5. Copy `pre-commit-config-rust.yaml` as `.pre-commit-config.yaml`.
6. Copy `ci-rust.yaml` to `.github/workflows/ci.yaml`.

### Python Repos (additional steps)

1. Copy `gitignore-python` as `.gitignore`.
2. Copy `pyproject.toml` to repo root. Replace `REPO_NAME` and
   `REPO-SPECIFIC` placeholders.
3. Copy `pre-commit-config-python.yaml` as `.pre-commit-config.yaml`.
4. Copy `ci-python.yaml` to `.github/workflows/ci.yaml`.
