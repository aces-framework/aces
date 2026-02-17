# ACES Project Instructions for Claude Code

## Critical Rules

- NEVER include `Co-Authored-By` lines in commit messages. Ever.
- NEVER commit directly. Provide the full `git commit -S` command for the
  user to run (commits must be GPG-signed).
- NEVER push without explicit user approval.
- NEVER create documentation files unless explicitly asked.
- NEVER hand-edit dependency versions in manifest files. Use the package
  manager CLI: `cargo add`/`cargo rm` for Rust, `uv add`/`uv remove`
  for Python.
- ALWAYS scaffold new projects with `cargo init`/`uv init`. Do not write
  manifest files from scratch.
- ALWAYS use virtual environments for Python (`uv venv`). No global
  installs.
- ALWAYS write a design/spec before implementing non-trivial components.
  No code without an approved design.
- ALWAYS write tests before implementation (TDD). Tests must fail first,
  then write the code to make them pass.

## Project

ACES (Agentic Cyber Environment System) is an open reference architecture
for declarative, reproducible cyber range environments for autonomous AI
agent research. It decomposes cyber range concerns into four layers:
Specification, Runtime, Instantiation, and Experimentation. See
`ARCHITECTURE.md` in the `aces-framework/aces` governance repo for the
full architecture reference.

GitHub org: `aces-framework`.

## Repo Map

| Repo | Language | Layer |
|------|----------|-------|
| aces | — | Governance |
| aces-schema | Protobuf/JSON Schema | Specification |
| aces-sdl | Rust | Specification |
| aces-provider-sdk | Rust | Instantiation |
| aces-agent-sdk | Python | Instantiation |
| aces-runtime | Rust | Runtime |
| aces-experiment | Python | Experimentation |
| aces-provider-docker | Rust | Instantiation |
| aces-stdlib | ACES SDL | Content |
| aces-cli | Rust | Tooling |

## Language and Toolchain

ADR-0001: Rust core + Python periphery (two languages).

<!-- REPO-SPECIFIC: Keep only the section relevant to this repo's language -->

### Rust (sdl, runtime, cli, provider-sdk, provider-docker)

- `cargo fmt` (default rustfmt, no custom overrides)
- `cargo clippy -- -D warnings`
- `thiserror` for library error types, `anyhow` only in CLI
- `tracing` crate for structured logging (JSON output)
- `tokio` for async, `tonic` for gRPC, `prost` for protobuf
- All public items have rustdoc comments
- No `unsafe` without `// SAFETY:` annotation

### Python (agent-sdk, experiment)

- `ruff` for linting and formatting
- `mypy --strict` on all public APIs
- `structlog` for structured logging (JSON output)
- `uv` for dependency management
- Google-style docstrings
- Minimum Python 3.11
- Agent SDK has strict dependency budget

### All

- Structured JSON logs with exercise_id/trial_id correlation
- gRPC status codes as error contract across Rust/Python boundary
- OpenTelemetry for internal observability (distinct from OCSF)
- Pre-commit hooks required (`.pre-commit-config.yaml` per repo)
- Config precedence: defaults < TOML file < env vars (ACES_ prefix) < CLI flags
- Secrets never in config files

Full detail: `STANDARDS.md` in the `aces-framework/aces` governance repo.

## Branching (ADR-0013)

- Trunk-based development. All work merges to `main` via PR.
- Releases are git tags (`vX.Y.Z`). No dev branch. No release branches (yet).
- Feature branches are short-lived.

## This Repo

<!-- REPO-SPECIFIC: Replace with this repo's details -->
This repo is: **REPO_NAME** — REPO_DESCRIPTION

### What This Repo Contains

<!-- Describe the repo's contents and structure -->

### Key Dependencies

<!-- List upstream/downstream ACES repos this repo depends on or feeds -->

### Repo-Specific Conventions

<!-- Any conventions unique to this repo beyond the project-wide standards -->

## Lessons Learned

<!-- Add lessons as they're discovered during development. Format:
- **[Topic]**: What happened and what to do instead. 1-2 sentences.
Promote recurring lessons to Critical Rules. Prune when obsolete. -->

## Key References

- Governance repo: `aces-framework/aces` (ADRs, RFCs, templates)
- Architecture: `ARCHITECTURE.md` in the governance repo
- Standards: `STANDARDS.md` in the governance repo
