# ADR-0014: Branch Protection and CI Standards

## Status

Accepted

## Context

ACES repos need consistent branch protection rules and CI checks across
the project. Standards must cover three repo types: governance (markdown),
Rust, and Python.

## Decision

### Branch Protection (all repos, applied to `main`)

- Require pull request before merging (no direct push to main).
- Require at least 1 review approval.
- Require status checks to pass before merge.
- Require signed commits.
- No force push to main.
- No deletion of main.

### Pre-Commit Hooks

All repos use pre-commit. Hooks vary by repo type:

**Governance (markdown-only):**

- trailing-whitespace, end-of-file-fixer, check-yaml, check-merge-conflict
- check-added-large-files (500KB limit)
- markdownlint

**Rust repos (sdl, runtime, cli, provider-sdk, provider-docker):**

- trailing-whitespace, end-of-file-fixer, check-yaml, check-merge-conflict
- check-added-large-files (500KB limit)
- cargo fmt --check
- cargo clippy -- -D warnings

**Python repos (agent-sdk, experiment):**

- trailing-whitespace, end-of-file-fixer, check-yaml, check-merge-conflict
- check-added-large-files (500KB limit)
- ruff check + ruff format --check
- mypy --strict

### CI (GitHub Actions)

CI runs on push to main and on pull requests to main.

**Governance:** pre-commit (markdownlint).

**Rust:** cargo fmt --check, cargo clippy -- -D warnings, cargo test,
cargo doc --no-deps.

**Python:** ruff check, ruff format --check, mypy --strict, pytest.

### GitHub Issue and PR Templates (all repos)

- Every repo MUST have a `.github/pull_request_template.md`.
- Every repo MUST have a `.github/ISSUE_TEMPLATE/` directory with at least
  one issue template relevant to the repo's domain.
- Blank issues MUST be enabled (`config.yml` with `blank_issues_enabled: true`)
  so that contributors are not forced into a template that doesn't fit.

### What Is Explicitly Not Required

- Conventional commits / commitlint (overhead for a small team).
- Multiple reviewers (1 is sufficient pre-v1.0).
- Code coverage gates (premature, would create perverse incentives).
- Signed tags (only signed commits required; tags are cut by CI).

## Consequences

- Consistent quality bar across all repos.
- Signed commits ensure authorship integrity.
- Pre-commit catches issues locally before CI, reducing feedback loop time.
- Single reviewer requirement keeps velocity high while maintaining a
  second pair of eyes.
- Standards can be tightened (more reviewers, coverage gates) as the
  project matures and the team grows.
