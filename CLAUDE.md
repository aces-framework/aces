# ACES Project Instructions for Claude Code

## Critical Rules

- NEVER include `Co-Authored-By` lines in commit messages. Ever.
- NEVER commit directly. Provide the full `git commit -S` command for the
  user to run (commits must be GPG-signed).
- NEVER push without explicit user approval.
- NEVER create documentation files unless explicitly asked.

## Project

ACES (Agentic Cyber Environment System) is an open reference architecture
for declarative, reproducible cyber range environments for autonomous AI
agent research. It decomposes cyber range concerns into four layers:
Specification, Runtime, Instantiation, and Experimentation. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the full architecture reference.

GitHub org: `aces-framework`.

## Repo Map

| Repo | Language | Layer |
|------|----------|-------|
| aces | — | Governance (this repo) |
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

Full detail: [`STANDARDS.md`](STANDARDS.md)

## Branching (ADR-0013)

- Trunk-based development. All work merges to `main` via PR.
- Releases are git tags (`vX.Y.Z`). No dev branch. No release branches (yet).
- Feature branches are short-lived.

## This Repo

This repo is: **aces** — Governance hub for the ACES project.

### What This Repo Contains

This repo contains NO application code. Only:

- ADRs (`adrs/`)
- RFCs (`rfcs/`)
- Architecture reference (`ARCHITECTURE.md`)
- Engineering standards (`STANDARDS.md`)
- Community docs (README, COMPATIBILITY)
- Repo templates (`templates/`) — base files for bootstrapping new ACES repos
- Issue and PR templates (`.github/`)

### Key Dependencies

None. This is the root governance repo. All other repos reference it.

### Repo-Specific Conventions

- Markdown-only. No application code, no build system.
- ADRs follow the template in `adrs/TEMPLATE.md`. Next ADR: 0019.
- RFCs follow the template in `rfcs/TEMPLATE.md`.
- New repo templates go in `templates/` (see `templates/README.md`).

## Key References

- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Standards: [`STANDARDS.md`](STANDARDS.md)
- ADRs: [`adrs/`](adrs/)
- Base template: [`templates/CLAUDE.md`](templates/CLAUDE.md)
