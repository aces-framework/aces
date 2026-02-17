# ACES Project Standards and Conventions

This document defines the cross-cutting conventions that apply to all ACES
repos. These are not architectural decisions (those are ADRs) but
operational standards that ensure consistency across the project.

Governed by ADR-0018.

## 1. Naming Conventions

### GitHub Organization

`aces-framework`

### Repository Naming

All repos use the prefix `aces-` within the organization. All lowercase,
hyphen-separated.

```text
aces-framework/
  aces                      # governance
  aces-schema               # semantic model + spec
  aces-sdl                  # parser / concrete syntax
  aces-provider-sdk         # provider interface
  aces-provider-docker      # Docker backend
  aces-provider-{backend}   # additional backends
  aces-agent-sdk            # agent interface
  aces-runtime              # core engine
  aces-experiment           # experiment harness
  aces-stdlib               # standard content library
  aces-cli                  # command-line interface
  aces-docs                 # documentation site
```

Rules:

1. All lowercase, hyphen-separated. `aces-provider-docker`, not
   `ACES_Provider_Docker`.
2. Prefix with `aces-` even within the org, for clarity in external
   contexts (forks, citations, dependency lists).
3. Provider repos: `aces-provider-{backend}`. Backend name matches the
   platform (docker, openstack, vsphere, aws, simulation).
4. SDK repos: `aces-{role}-sdk` (aces-provider-sdk, aces-agent-sdk).
5. No abbreviations beyond `aces` and `sdl` (both established terms).

### Package/Module Naming

Internal package names follow target language conventions:

| Language | Pattern | Example |
|----------|---------|---------|
| Rust | Hyphen-separated crate names | `aces-schema`, `aces-sdl` |
| Python | Underscore-separated | `aces_schema`, `aces_agent_sdk` |
| Protobuf | Dotted package names | `aces.schema.v1`, `aces.provider.v1` |

Scoped packages (`@aces-framework/...`) are preferred for ecosystems that
support them (npm, if applicable).

### Cross-Language Naming

| Context | Convention | Example |
|---------|-----------|---------|
| gRPC services and messages | PascalCase (protobuf standard) | `ExerciseService`, `ProvisionRequest` |
| Config file keys | snake_case | `bind_address`, `log_level` |
| Environment variables | SCREAMING_SNAKE_CASE with `ACES_` prefix | `ACES_LOG_LEVEL` |
| Rust code | Rust conventions (snake_case functions, PascalCase types) | `exercise_id`, `ExerciseState` |
| Python code | PEP 8 (snake_case functions, PascalCase classes) | `exercise_id`, `ExerciseState` |
| Identifiers (exercise, trial, agent) | UUIDv7 (time-ordered) | — |

## 2. Configuration Precedence

All ACES components follow this precedence (highest wins):

1. **Defaults** — Sensible defaults baked into the binary/package.
2. **Config file** — TOML format. Located at `./aces-{component}.toml`
   or `~/.config/aces/{component}.toml`.
3. **Environment variables** — Prefixed with `ACES_`
   (e.g., `ACES_LOG_LEVEL`, `ACES_RUNTIME_BIND_ADDRESS`).
4. **CLI flags** — Override everything. Rust components only (via clap).

### Rust

Use `config` crate (or `figment`) for layered configuration. Config struct
derives `serde::Deserialize`.

```toml
# Example: aces-runtime.toml
[runtime]
bind_address = "0.0.0.0:9090"
log_level = "info"

[providers]
docker.endpoint = "unix:///var/run/docker.sock"

[telemetry]
otlp_endpoint = "http://localhost:4317"
metrics_port = 9091
```

### Python

Use `pydantic-settings` for typed configuration with env var support.
Fail fast on invalid config at startup.

### Secrets

Credentials are NEVER stored in config files. Accepted sources:
environment variables, file paths to mounted secrets, or a secrets
manager reference. Config files may reference a secret file path, never
a secret value.

## 3. Content Package Format

Reusable scenario components (modules, templates, behavioral specs) use
a standard package layout:

```text
my-ad-environment/
  aces-package.yaml    # manifest
  README.md            # description, usage
  infrastructure/      # node, network, feature definitions
  behavior/            # attack, defense, background activity
  scoring/             # assessment criteria
  examples/            # usage examples
```

### Manifest (aces-package.yaml)

The manifest declares:

- `name` — Package name (lowercase, hyphen-separated).
- `version` — SemVer version of the package.
- `aces-schema` — Compatible aces-schema version range.
- `dependencies` — Other ACES packages this package requires.
- `description` — One-line summary.
- `license` — SPDX identifier.

The manifest schema is defined in aces-schema (it is a schema type).

### Distribution

**Phase 1 (current):** Git repos tagged with the `aces-content` topic on
GitHub. Users reference packages by Git URL + version tag.

**Phase 2 (when needed):** A registry service for content discovery and
distribution. Deferred until there is enough content to justify the
infrastructure.

### Versioning

Content packages use SemVer independently of the framework repos. Each
package declares which aces-schema version it targets.

## 4. Identifier Format

Exercise, trial, agent, and provider instance identifiers use UUIDv7
(time-ordered UUIDs). This provides:

- Global uniqueness without coordination.
- Chronological ordering from the ID itself.
- Standard 128-bit format supported by every language and database.

## 5. Versioning

Governed by ADR-0016.

### All Repos: SemVer

Every ACES repo uses Semantic Versioning 2.0.0. Each repo maintains its
own independent version number.

### aces-schema: Formal Breaking-Change Rules

Schema versioning carries additional constraints:

- **Major (X.0.0)** — Removing or renaming fields, changing type
  semantics, removing types. Requires RFC and migration guide.
- **Minor (0.X.0)** — New types, new optional fields, new
  extensions/profiles. Backward compatible.
- **Patch (0.0.X)** — Documentation fixes, constraint clarifications,
  no type changes.

The extension mechanism allows the schema to grow at minor versions
without breaking anyone.

### Compatibility Declarations

Each downstream repo declares which aces-schema version(s) it supports.
Example: "aces-sdl v2.3.0 supports aces-schema >=1.2.0 <2.0.0."

A compatibility matrix is maintained in
[`COMPATIBILITY.md`](COMPATIBILITY.md).

### Release Cadence

- **aces-schema**: Deliberate, RFC-governed releases.
- **aces-sdl, aces-runtime**: Regular releases following schema updates.
- **aces-provider-***: Independent release cadence per provider.
- **aces-stdlib**: Continuous, content can be published anytime.

### Pre-1.0 Expectations

All repos start at 0.x.y. No stability promises until 1.0. Minor
versions may contain breaking changes during 0.x (per SemVer spec).

## 6. Structured Logging

All ACES components emit structured JSON logs. No unstructured text to
stdout in production mode.

### Rust Components

Use `tracing` crate with `tracing-subscriber` (JSON formatter).
Structured fields, not string interpolation:

```rust
tracing::info!(scenario_id = %id, "loaded scenario");
// NOT: info!("loaded scenario {id}");
```

Span-based context propagation: each exercise, trial, and provider
operation gets its own tracing span.

### Python Components

Use `structlog` (JSON output). Bound loggers with context:

```python
log = structlog.get_logger().bind(experiment_id=eid)
```

### Log Levels

| Level | Meaning | Example |
|-------|---------|---------|
| ERROR | Operation failed, requires attention | Provider provisioning failed, gRPC connection lost |
| WARN  | Degraded but functional, or unusual condition | Slow provider response, deprecated schema field used |
| INFO  | Significant lifecycle events | Exercise started/stopped, provider connected, agent joined |
| DEBUG | Detailed operational flow | Event bus message routing, state transitions |
| TRACE | Extremely verbose, development only | Raw gRPC messages, full OCSF event payloads |

### Correlation Fields

All log entries within an exercise context MUST carry:

- `exercise_id` — unique per exercise instance
- `trial_id` — unique per experiment trial (if under experiment harness)
- `component` — which ACES component emitted the log

## 7. Error Handling

### Rust Components

- `thiserror` for defining error types. Each crate defines its own error
  enum.
- `anyhow` only in the CLI (top-level application code). Library crates
  use typed errors.
- Errors crossing crate boundaries are converted at the boundary, not
  leaked.

Error categories (each crate should distinguish):

| Category | Meaning | Recovery |
|----------|---------|----------|
| Validation | Input does not meet schema/contract | Return error to caller with diagnostic |
| Infrastructure | External system failed (Docker, cloud API, network) | Retry or escalate |
| Internal | Bug in ACES code (invariant violation) | Panic with context |
| Protocol | Unexpected gRPC message or version mismatch | Return gRPC status code with detail |

### Python Components

- Define exception hierarchies per package. `AcesAgentError` base class
  in agent-sdk, `AcesExperimentError` in experiment.
- Never catch bare `Exception`. Catch specific types.
- gRPC errors from the runtime are translated into typed Python
  exceptions in the SDK.

### Across the gRPC Boundary

gRPC status codes are the error contract between Rust and Python:

| Situation | gRPC Status | Detail |
|-----------|------------|--------|
| Invalid scenario spec | `INVALID_ARGUMENT` | Validation error message |
| Provider cannot provision | `FAILED_PRECONDITION` | Which capability is missing |
| Exercise not found | `NOT_FOUND` | Exercise ID |
| Internal runtime error | `INTERNAL` | Sanitized message (no stack traces over the wire) |
| Agent action rejected | `PERMISSION_DENIED` | Which action, which constraint |
| Resource exhaustion | `RESOURCE_EXHAUSTED` | What limit was hit |

Stack traces and internal details stay on the server side (in structured
logs). Clients get actionable error messages.

## 8. Observability

ACES uses OpenTelemetry for its own operational telemetry (ADR-0011).
This is distinct from OCSF, which is the exercise telemetry contract
(ADR-0008).

### Three Pillars

**Logs**: See section 6. `tracing` (Rust) and `structlog` (Python) with
JSON output.

**Metrics**: Expose Prometheus-compatible metrics from long-running
components.

| Component | Key Metrics |
|-----------|------------|
| aces-runtime | Active exercises, connected providers, connected agents, event bus throughput, scoring pipeline latency, checkpoint/restore duration |
| aces-provider-docker | Container count, provision latency, failure rate per operation |
| aces-experiment | Active trials, trial completion rate, trial duration distribution |

Rust: `metrics` crate with `metrics-exporter-prometheus`.
Python: `prometheus-client` library.

**Traces**: Distributed tracing across the runtime/provider/agent call
chain. Propagate trace context via gRPC metadata (W3C Trace Context
headers).

- Rust: `tracing-opentelemetry` bridge.
- Python: `opentelemetry-sdk` with gRPC instrumentation.
- Each exercise is a trace root. Provider calls and agent interactions
  are child spans.

## 9. Testing Standards

### Test Pyramid

| Level | What | Where | Runner |
|-------|------|-------|--------|
| Unit | Single function/module, no I/O | Each crate/package, `tests/` or inline `#[cfg(test)]` | `cargo test` / `pytest` |
| Integration | Cross-module, may use test doubles | Each crate/package, `tests/integration/` | `cargo test --test` / `pytest -m integration` |
| Contract | Provider SDK conformance, agent SDK conformance | SDK repos, `tests/conformance/` | Custom test harness (part of SDK) |
| End-to-end | Full stack: sdl to runtime to provider to agent | `aces` governance repo or dedicated test repo | CI workflow, Docker Compose |

### Rust

- `#[cfg(test)]` for unit tests alongside code.
- `proptest` or `quickcheck` for property-based testing — especially
  valuable for the SDL parser and automata crate.
- `insta` for snapshot testing of parser output and error messages.
- `mockall` for trait-based test doubles when needed.

### Python

- `pytest` as test runner. No unittest.
- `pytest-asyncio` for async gRPC tests.
- `hypothesis` for property-based testing.
- Agent SDK conformance tests verify `gymnasium.Env` contract (valid
  spaces, step/reset behavior, reward signals).

### What to Test

Test behavior, not implementation. Do not test private functions
directly, trivial getters/setters, or generated code.

Do test: error paths, boundary conditions, cross-crate contracts, and
verification correctness.

## 10. Security

### gRPC Channel Security

- **Runtime to Provider**: mTLS. Providers authenticate to the runtime
  with client certificates; the runtime authenticates to providers with
  its server certificate. No plaintext gRPC in production.
- **Runtime to Agent**: TLS (server-side). Agents authenticate via
  tokens (exercise-scoped, short-lived). mTLS optional for
  high-security deployments.
- **CLI to Runtime**: TLS. CLI authenticates via token or client cert.
- **Local development**: Plaintext gRPC acceptable, enabled via config
  flag (`ACES_INSECURE=true` or `--insecure`). Logged as WARNING at
  startup.

### Credential Management

- Provider credentials are the provider's responsibility, not the
  runtime's. The provider SDK contract does not pass credentials through
  the runtime.
- Agent tokens are issued by the runtime, scoped to a single exercise
  instance.
- No credential storage in ACES. ACES consumes credentials from the
  environment.

### Input Validation

- The SDL parser is a trust boundary. All scenario input is untrusted.
  Parser must not crash, hang, or consume unbounded memory on malformed
  input. Fuzz testing (`cargo-fuzz` / AFL) is appropriate.
- gRPC messages from agents are untrusted. Runtime validates all agent
  actions against the role's permitted action space.
- Provider status reports are semi-trusted. Runtime validates reported
  state against expected state.

## 11. CI/CD Standards

### Rust Toolchain

- Pin Rust version in `rust-toolchain.toml` per repo.
- CI runs: `cargo fmt --check`, `cargo clippy -- -D warnings`,
  `cargo test`, `cargo doc --no-deps`.
- MSRV policy: latest stable minus one. No nightly features.

### Python Toolchain

- Pin Python version in `pyproject.toml`. Minimum: 3.11.
- CI runs: `ruff check`, `ruff format --check`, `mypy`, `pytest`.
- Use `uv` for dependency management and virtual environments.
- `mypy --strict` on SDK and experiment packages.

### Release Process

- All releases tagged (`vX.Y.Z`) and built by CI. No manual releases.
- Rust: publish to crates.io via CI on tag push.
- Python: publish to PyPI via CI on tag push.
- Changelogs maintained per repo (CHANGELOG.md, keep-a-changelog
  format).
- Pre-release versions (`0.x.y`) expected for the entire pre-1.0 phase.

### Cross-Repo CI

When `aces-schema` cuts a release, it triggers downstream CI in sdl,
runtime, and both SDKs to verify compatibility. This is the schema
bottleneck mitigation — fast feedback on whether a schema change breaks
consumers.

## 12. Documentation Standards

### Code Documentation

**Rust:**

- All public items have rustdoc comments (`///`).
- Module-level documentation (`//!`) for each module.
- Examples in doc comments where the API is not obvious (tested by
  `cargo test`).
- No doc comments on private items unless logic is non-obvious.

**Python:**

- Google-style docstrings on all public classes and functions.
- Type annotations serve as primary documentation for argument and
  return types.
- Module-level docstrings.

### API Reference

- Rust: generated by `cargo doc`, published to docs.rs on crates.io
  release.
- Python: generated by `mkdocstrings` or `sphinx-autodoc`, published
  to aces-docs site.
- gRPC: protobuf files are self-documenting via comments. Generate
  human-readable API reference from proto files (protoc-gen-doc or buf).

## 13. Dependency Management

### Rust

- Use `cargo-deny` to enforce: no duplicate crate versions, no
  licenses incompatible with Apache-2.0, no known vulnerabilities.
- Minimize dependency count. Prefer the Rust standard library over
  trivial utility crates.

### Python

- Use `uv` with `pyproject.toml` for dependency declaration.
- Pin exact versions in lock files for reproducible builds.
- Agent SDK has a strict dependency budget: `grpcio`, `protobuf`,
  `gymnasium`, `numpy`. Every additional dependency is a barrier to
  adoption.
- Experiment harness is more relaxed (research users expect scipy,
  pandas, etc.).

### Shared Dependencies

| Dependency | Rust Crate | Python Package | Purpose |
|-----------|-----------|----------------|---------|
| gRPC | `tonic` + `prost` | `grpcio` + `protobuf` | Wire protocol |
| Protobuf | `prost` | `protobuf` | Schema serialization |
| OpenTelemetry | `opentelemetry` + `tracing-opentelemetry` | `opentelemetry-sdk` | Internal observability |
| JSON | `serde_json` | `json` (stdlib) | Structured logging, config |

## 14. Code Style

### Rust

- `rustfmt` with default settings. No custom `rustfmt.toml` overrides.
- `clippy` with all warnings treated as errors in CI.
- No `unsafe` without a `// SAFETY:` annotation explaining necessity.
  Prefer safe abstractions.
- Naming: Rust conventions (snake_case for functions/variables,
  PascalCase for types, SCREAMING_SNAKE_CASE for constants).

### Python

- `ruff` for both linting and formatting (replaces black, isort, flake8).
- Line length: 88 (ruff default).
- Type annotations: required for all public APIs, encouraged for
  internals.
- Naming: PEP 8 (snake_case for functions/variables, PascalCase for
  classes).
