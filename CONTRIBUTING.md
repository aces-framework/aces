# Contributing to ACES

Thank you for your interest in contributing to ACES.

## How to Contribute

### Reporting Issues

- Use this repo for cross-cutting issues that affect multiple ACES components.
- Use the specific component repo for issues scoped to a single component.

### Code Contributions

Each ACES repo has its own development setup. See the README in the relevant
repo for build instructions and contribution guidelines.

### Architectural Changes

Changes that affect multiple repos or alter the project's architecture require
an RFC:

1. Copy `rfcs/TEMPLATE.md` to `rfcs/000X-short-title.md`.
2. Fill in the template: context, proposal, alternatives considered,
   consequences.
3. Open a PR. Discussion period: minimum 2 weeks for breaking changes.
4. Approval by maintainers of all affected repos.
5. Implementation PRs in affected repos reference the RFC.

**Triggers for RFC**: Any schema breaking change. Any new interface boundary.
Any new repo creation. Any architectural decision affecting multiple teams.

### ADRs

Significant technical decisions are recorded as Architecture Decision Records
in `adrs/`. ADRs are immutable once accepted — superseded decisions get a new
ADR that references the original.

## Code Standards

### Rust Components (sdl, runtime, cli, provider-sdk)

- Toolchain pinned via `rust-toolchain.toml`.
- CI enforces: `cargo fmt --check`, `cargo clippy -- -D warnings`,
  `cargo test`, `cargo doc --no-deps`.
- Error handling: `thiserror` for library crates, `anyhow` for CLI only.
- All public items have rustdoc comments.

### Python Components (agent-sdk, experiment)

- Minimum Python 3.11.
- CI enforces: `ruff check`, `ruff format --check`, `mypy --strict`,
  `pytest`.
- Dependency management via `uv`.
- Type annotations required on all public APIs.
- Google-style docstrings.

### All Components

- Structured JSON logging (`tracing` for Rust, `structlog` for Python).
- gRPC status codes as the error contract across language boundaries.
- Apache-2.0 license.

## Versioning

- **aces-schema**: SemVer with RFC-governed breaking changes.
- **All other repos**: Independent SemVer, declaring compatible
  aces-schema version range.
- Compatibility matrix maintained in this repo.

## Code of Conduct

Be respectful, constructive, and collaborative. Detailed code of conduct
to be adopted as the community grows.
