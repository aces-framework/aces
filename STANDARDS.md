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

Governed by ADR-0021 (defense-in-depth). ACES is cyber range
infrastructure where agents are adversarial by design and scenarios may
involve real exploits. The security posture must exceed a typical
open-source project.

This section states security **policies and rationale**. Implementation
details remain in the sections where they originate (§2, §13, §14, §16).
§10.12 provides a cross-reference table.

### 10.1 Threat Model

ACES has four trust boundaries:

| Boundary | Untrusted Side | Trusted Side | Control |
|----------|---------------|-------------|---------|
| SDL parser input | Scenario files (user-authored) | Parsed AST | Input validation, bounded parsing, fuzz testing |
| Agent to runtime (gRPC) | Agent actions | Runtime state | Action-space validation, TLS, tokens |
| Provider to runtime (gRPC) | Provider status reports | Runtime expectations | State validation, mTLS |
| Container/VM boundary | Exercise infrastructure | Host / other exercises | Network isolation, sandboxing |

Every component on the untrusted side of a boundary must be treated as
potentially malicious. Controls at each boundary are detailed in the
subsections below.

### 10.2 Channel Security

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

### 10.3 Credential Management

- Provider credentials are the provider's responsibility, not the
  runtime's. The provider SDK contract does not pass credentials through
  the runtime.
- Agent tokens are issued by the runtime, scoped to a single exercise
  instance.
- No credential storage in ACES. ACES consumes credentials from the
  environment (see §2 for config precedence and secrets policy).
- CI publishing tokens: use OIDC trusted publishing for crates.io and
  PyPI releases. No long-lived API tokens in CI secrets. [PRE-1.0]

### 10.4 Input Validation and Trust Boundaries

- The SDL parser is a trust boundary. All scenario input is untrusted.
  Parser must not crash, hang, or consume unbounded memory on malformed
  input. Fuzz testing (`cargo-fuzz` / AFL) is appropriate.
- gRPC messages from agents are untrusted. Runtime validates all agent
  actions against the role's permitted action space.
- Provider status reports are semi-trusted. Runtime validates reported
  state against expected state.
- All parsers enforce explicit input size limits and recursion depth
  limits. These limits are configurable but have safe defaults.

### 10.5 Supply Chain Security

#### Rust

- `cargo-deny` checks licenses, duplicate crates, and known
  vulnerabilities. Configuration in `cargo-deny.toml` per repo (see
  §13 for dependency management policy).
- `cargo deny check` runs in CI after tests.
- `cargo-audit` for RUSTSEC advisory database checks. Runs in CI
  after `cargo deny check`.

#### Python

- `pip-audit` checks installed packages against the OSV database.
- `pip-audit` runs in CI after tests.

#### GitHub Actions

- All third-party actions are pinned by full commit SHA, not mutable
  tag. This prevents a compromised upstream tag from injecting code
  into ACES CI.
- Format: `uses: owner/repo@<full-sha>  # tag` — the comment preserves
  human readability.

#### General

- SBOM (Software Bill of Materials) generation for releases. [PRE-1.0]
- Dependency minimization: every dependency is a security surface. See
  §13 for the strict dependency budget (especially aces-agent-sdk).

### 10.6 Code Safety

#### Unsafe Rust

- Crates and modules that do not need `unsafe` use
  `#![forbid(unsafe_code)]` (see §16).
- All `unsafe` blocks require a preceding `// SAFETY:` annotation
  explaining why the invariants hold (see §14).
- CI audit step greps for `unsafe` blocks and asserts each has a
  `// SAFETY:` annotation (see §16).

#### Static Analysis

- Rust: `cargo clippy -- -D warnings` (all warnings are errors).
- Python: `ruff check` + `mypy --strict` on all public APIs.
- Both run in CI on every PR.

#### Fuzz Testing [PRE-1.0]

- SDL parser: `cargo-fuzz` with corpus seeded from test fixtures.
- Schema deserializer: fuzz protobuf/JSON input.
- Fuzz targets live in `fuzz/` within the relevant repo.

### 10.7 CI/CD Security

- **Minimal permissions**: All CI workflows declare
  `permissions: contents: read` at the top level. Steps that need
  additional permissions declare them explicitly at the job level.
- **Secrets handling**: No secrets in config files (§2). CI uses GitHub
  encrypted secrets or OIDC tokens.
- **Signed commits**: Required by branch protection (ADR-0014).
- **Signed artifacts**: Release artifacts are signed. [PRE-1.0]
- **Hash-pinned actions**: See §10.5.

### 10.8 Container and Image Security

Applies to aces-provider-docker and any future container-based
providers.

- **Base images**: Prefer distroless or minimal base images. Pin by
  digest (`@sha256:...`), not tag. [PRE-1.0]
- **Image scanning**: Scan container images for vulnerabilities before
  publishing (e.g., Trivy, Grype). [PRE-1.0]
- **No secrets in images**: Container images must not contain secrets,
  credentials, or private keys. Secrets are injected at runtime via
  environment variables or mounted files.
- **Exemption process**: If a provider image must include known-
  vulnerable software (e.g., intentionally vulnerable exercise targets
  in aces-stdlib), document the exemption in the image's README and
  exclude it from automated scanning.

### 10.9 Agent Sandboxing

Agents interact with the ACES runtime exclusively via gRPC. The
sandboxing model has two layers:

- **Logical isolation**: The runtime validates every agent action against
  the role's permitted action space (derived from the scenario spec).
  An agent cannot perform actions outside its role definition.
- **Infrastructure isolation**: Exercise infrastructure (containers, VMs,
  networks) is isolated from the host and from other exercises. Provider
  implementations enforce network boundaries and resource limits.

Agents have no direct access to provider infrastructure, host
filesystems, or other exercises. The gRPC API is the only interface.

### 10.10 Vulnerability Disclosure

- Every ACES repo contains a `SECURITY.md` with reporting instructions.
- Preferred reporting channel: GitHub Security Advisories (private).
- Fallback: security email address listed in SECURITY.md.
- Response timeline: 3-day acknowledgment, 7-day assessment, 30-day fix
  target for critical/high severity.
- 90-day coordinated disclosure window.
- Reporters are credited in the advisory unless they prefer anonymity.
- **Scope carve-out**: Intentionally vulnerable content in aces-stdlib
  is excluded from the vulnerability scope. It is vulnerable by design.

### 10.11 Security Review Gates

PRs that touch the following require explicit security review:

| Change | Review Requirement |
|--------|-------------------|
| Trust boundary code (parser, gRPC handlers, action validation) | Security-focused review; consider threat model impact |
| Cryptographic code or TLS configuration | Review by someone with crypto experience |
| `unsafe` Rust code | `// SAFETY:` annotation; architectural justification |
| CI workflow changes | Verify permissions are minimal; actions are SHA-pinned |
| New dependencies | Check advisory databases; evaluate maintenance status |
| Container/image changes | Verify no embedded secrets; base image policy compliance |

### 10.12 Cross-References

Security policy is distributed across several sections and ADRs. This
table maps each concern to its authoritative location.

| Concern | Policy (§10) | Detail |
|---------|-------------|--------|
| Secrets in config | §10.3 | §2 (Configuration Precedence) |
| Dependency scanning (Rust) | §10.5 | §13 (Dependency Management), `cargo-deny.toml` |
| `// SAFETY:` annotations | §10.6 | §14 (Code Style) |
| `#![forbid(unsafe_code)]` | §10.6 | §16 (Architecture and Policy as Code) |
| Unsafe audit CI step | §10.6 | §16 (CI Policy Checks) |
| Signed commits | §10.7 | ADR-0014 (Branch Protection and CI) |
| Formal methods at trust boundaries | §10.4 | ADR-0019 (Formal Methods) |
| Architecture as code enforcement | §10.11 | ADR-0020 (Architecture and Policy as Code) |
| Defense-in-depth rationale | §10 (all) | ADR-0021 (Defense-in-Depth Security) |

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

### General Rules (all languages)

- NEVER hand-edit dependency versions in manifest files (`Cargo.toml`,
  `pyproject.toml`, `package.json`, etc.). Always use the package
  manager's CLI to add, remove, or update dependencies. Hand-editing
  bypasses constraint resolution and lock file updates.
- ALWAYS use the package manager's scaffolding commands to create new
  projects (`cargo init`, `uv init`, etc.). Do not write manifest files
  from scratch.
- ALWAYS use virtual environments for Python. No global installs.
- Minimize dependency count. Every dependency is a maintenance burden,
  a security surface, and a build-time cost.

### Rust

- Use `cargo add` to add dependencies, `cargo rm` to remove them.
- Use `cargo init` or `cargo new` to scaffold new crates.
- Use `cargo-deny` to enforce: no duplicate crate versions, no
  licenses incompatible with Apache-2.0, no known vulnerabilities.
- Prefer the Rust standard library over trivial utility crates.

### Python

- Use `uv` for all dependency and environment management.
- Use `uv init` to scaffold new projects.
- Use `uv add` to add dependencies, `uv remove` to remove them.
- Use `uv venv` for virtual environments. Every Python project has a
  `.venv/` — no exceptions.
- Pin exact versions in lock files (`uv lock`) for reproducible builds.
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

## 15. Formal Methods

Governed by ADR-0019. ACES uses formal methods for critical components
where behavior is precisely specifiable. Agentic coding tools are
expected to write and maintain specs as part of normal development.

### Tier 1: Design-by-Contract

Pre/post-conditions and invariants on public API boundaries.

**Rust:**

```rust
/// Transition the exercise to the Running state.
///
/// # Contract
/// - Pre: `self.state == ExerciseState::Provisioned`
/// - Post: `self.state == ExerciseState::Running`
/// - Invariant: `self.id` is unchanged
pub fn start(&mut self) -> Result<(), ExerciseError> {
    debug_assert!(self.state == ExerciseState::Provisioned);
    // ...
}
```

**Python:**

```python
def submit_action(self, action: Action) -> Observation:
    """Submit an agent action.

    Contract:
        Pre: self.is_connected and action in self.action_space
        Post: returned observation in self.observation_space
    """
    assert self.is_connected, "must be connected"
    assert action in self.action_space, f"invalid action: {action}"
    # ...
```

Required for: public trait/protocol implementations, SDK entry points,
gRPC service handlers.

### Tier 2: Property Specifications

Formally stated properties verified by property-based testing. Each
property cites the invariant it encodes.

```rust
proptest! {
    /// Grammar completeness: every valid token sequence parses.
    /// (SDL grammar §3.2)
    #[test]
    fn parse_roundtrip(input in valid_sdl_strategy()) {
        let ast = parse(&input).unwrap();
        let output = emit(&ast);
        assert_eq!(parse(&output).unwrap(), ast);
    }
}
```

Required for: SDL parser, schema compatibility checker, state machine
transitions.

### Tier 3: Model Checking (TLA+)

TLA+ or PlusCal specs for protocols and concurrent state machines. Specs
live in a `spec/` directory within the relevant repo and are checked by
TLC in CI.

```text
aces-runtime/
  spec/
    ExerciseLifecycle.tla    # exercise state machine
    ProviderProtocol.tla     # runtime <-> provider interaction
    AgentProtocol.tla        # runtime <-> agent interaction
    EventBusOrdering.tla     # delivery guarantees
```

Required for: exercise lifecycle, runtime-provider protocol,
runtime-agent protocol, event bus ordering.

Specs are updated in the same PR as the code they describe.

### Tier 4: Typestate (Rust)

Compile-time state machine enforcement. Invalid transitions are
unrepresentable.

```rust
struct Exercise<S: ExerciseState> { /* ... */ }

impl Exercise<Created> {
    fn provision(self) -> Result<Exercise<Provisioned>, Error> { /* ... */ }
}
impl Exercise<Provisioned> {
    fn start(self) -> Result<Exercise<Running>, Error> { /* ... */ }
}
// Exercise<Created> has no start() — won't compile.
```

Required for: exercise lifecycle handle (`aces-runtime`), provider
session handle (`aces-provider-sdk`).

### Applicability by Repo

| Repo | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|------|--------|--------|--------|--------|
| aces-sdl | Yes | Yes (parser) | — | — |
| aces-runtime | Yes | Yes (state machines) | Yes (all four specs) | Yes (exercise lifecycle) |
| aces-provider-sdk | Yes | Yes (contract) | Yes (provider protocol) | Yes (session handle) |
| aces-provider-docker | Yes | — | — | — |
| aces-agent-sdk | Yes | Yes (contract) | Yes (agent protocol) | — |
| aces-schema | — | Yes (compatibility) | — | — |
| aces-experiment | — | — | — | — |
| aces-cli | — | — | — | — |

## 16. Architecture and Policy as Code

Governed by ADR-0020. If a constraint is worth documenting, it is worth
encoding as a check. Prose describes intent; code enforces compliance.

### Language-Level Enforcement

**Rust:**

- `pub(crate)` / `pub(super)` to enforce module encapsulation. Internal
  modules are not `pub` — they communicate through defined traits.
- `#![forbid(unsafe_code)]` on modules and crates that must not use
  unsafe.
- `#![deny(missing_docs)]` on library crates.
- Newtypes for domain boundaries: a validated `ScenarioSpec` can only be
  constructed through the parser, not assembled from raw fields.

```rust
// In lib.rs of a library crate:
#![deny(missing_docs)]

// In a module that must not use unsafe:
#![forbid(unsafe_code)]
```

**Python:**

- `typing.Protocol` for structural contracts between modules.
- `@final` / `@override` for inheritance contracts.
- `__all__` in `__init__.py` to define public surface.

### Architectural Fitness Functions

Tests that assert structural properties, not behavior. Located in
`tests/architecture.rs` (Rust) or `tests/test_architecture.py` (Python).

**Rust — architecture tests:**

```rust
#[test]
fn public_error_types_implement_std_error() {
    // Assert every pub error enum implements std::error::Error.
    // Implementation: compile-time trait bound checks or
    // reflection via inventory crate.
}

#[test]
fn unsafe_blocks_have_safety_comments() {
    // Grep source for `unsafe` blocks, assert each has // SAFETY:
}
```

**Rust — `cargo-modules`:**

Run `cargo modules generate tree` in CI to generate the module
dependency graph. Assert no unexpected edges (e.g., no backward
dependency from a lower module to a higher one within the runtime
monolith).

**Python — `import-linter`:**

Declare layer contracts in `pyproject.toml` or `.importlinter`:

```ini
[importlinter]
root_package = aces_agent_sdk

[importlinter:contract:layers]
name = SDK layer enforcement
type = layers
layers =
    aces_agent_sdk.api
    aces_agent_sdk.core
    aces_agent_sdk.transport
```

Runs in CI: `lint-imports`. Fails if `transport` imports from `api`,
etc.

**Python — architecture tests:**

```python
def test_no_runtime_dependency_in_agent_sdk():
    """Agent SDK must not import from aces-runtime."""
    import importlib
    import pkgutil

    for importer, modname, ispkg in pkgutil.walk_packages(
        aces_agent_sdk.__path__, prefix="aces_agent_sdk."
    ):
        mod = importlib.import_module(modname)
        source = inspect.getsource(mod)
        assert "aces_runtime" not in source, f"{modname} imports aces_runtime"
```

### CI Policy Checks

Automated checks for policies that cross individual tool boundaries.

**Dependency budget (aces-agent-sdk):**

CI step counts direct dependencies in `pyproject.toml` and fails if the
count exceeds the declared budget. The agent SDK has a strict dependency
budget — this makes it enforceable, not aspirational.

**Unsafe audit (Rust repos):**

CI step greps for `unsafe` blocks and asserts each has a preceding
`// SAFETY:` annotation.

**Cross-repo dependency DAG (governance repo):**

CI job parses `Cargo.toml` / `pyproject.toml` across repos and asserts
the dependency graph matches the declared architecture. No tier-3 repo
may depend on a tier-4 repo.

**Template drift detection (governance repo):**

CI job diffs each repo's governed files (CI config, markdownlint config,
pre-commit config) against governance templates. Flags divergence.

### Declarative Policy in Application Code

Prefer declarative constraint expression over imperative checks:

| Domain | Pattern | Anti-Pattern |
|--------|---------|-------------|
| Agent action validation | Spec → rule set → generic evaluator | Hand-coded `if` per action type |
| Provider capability matching | Capability declaration → DryRun check | Hardcoded provider-specific branches |
| Scoring | Assessment definition → scoring engine | Per-mode scoring functions |
| Schema validation | Typed deserialization with constraints | Manual field-by-field validation |

The general rule: if a constraint varies per scenario, role, or
provider, express it as data and write a generic engine. If a constraint
is structural and universal, encode it in the type system or module
system.

### Applicability

| Check | Where | When |
|-------|-------|------|
| `#![deny(missing_docs)]` | Rust library crates | Always |
| `#![forbid(unsafe_code)]` | Modules with no unsafe need | Always |
| `import-linter` | Python repos with internal layers | Always |
| Architecture tests | Repos with module boundary invariants | Always |
| Dependency budget | aces-agent-sdk | Always |
| Unsafe audit | All Rust repos | Always |
| Cross-repo DAG check | Governance CI | On dependency changes |
| Template drift | Governance CI | Periodic / on template changes |

## 17. Development Workflow

### Design First

Non-trivial work requires a written design before implementation begins.
"Non-trivial" means: new components, new repos, new protocols, changes
to interface boundaries, or anything touching more than one repo.

| Scope | Design Artifact | Where |
|-------|----------------|-------|
| Cross-cutting (affects multiple repos) | RFC | `rfcs/` in governance repo |
| Architectural decision | ADR | `adrs/` in governance repo |
| New component or repo | Component spec | Issue on governance repo, or `specs/` in target repo |
| Feature within a repo | Design section in PR description or issue | The repo's issue tracker |

A design must include:

1. **Purpose** — What problem does this solve and for whom.
2. **Interface** — Public API, tool surface, or user-facing behavior.
3. **Scope** — What is in, what is explicitly out.
4. **Dependencies** — What it uses, what uses it.
5. **Verification** — How you know it works (feeds into TDD).

No code is written until the design is reviewed and approved. For
agent-driven development, the agent writes the design, the human
approves, then the agent proceeds.

### Test-Driven Development

ACES uses TDD for all application code. The workflow is:

1. **Design/spec** — Write or receive an approved design.
2. **Tests** — Write tests that verify the design's requirements. Tests
   must fail (red) because the implementation does not exist yet.
3. **Implementation** — Write the minimum code to make the tests pass
   (green).
4. **Refactor** — Clean up while keeping tests green.

This applies to both human and agent development. An agent asked to
implement a feature writes the test file first and confirms it fails
before writing production code.

**What TDD covers:**

- All public API functions and methods.
- Error paths and edge cases identified in the design.
- Contract conformance (SDK tests, protocol tests).
- Property-based tests for formally specified invariants (ADR-0019).

**What TDD does not require:**

- Tests for trivial code (simple structs, re-exports, generated code).
- Tests written before exploratory prototyping — but prototypes are not
  merged without tests.

### Workflow Summary

```text
Design/Spec → Review → Tests (red) → Code (green) → Refactor → PR
```

This is not optional. PRs that introduce new functionality without
corresponding tests or without a traceable design are incomplete.

### Lessons Learned

Every repo's `CLAUDE.md` includes a `## Lessons Learned` section that
records mistakes, pitfalls, and hard-won knowledge discovered during
development. This section is loaded into every agent session
automatically, preventing the same mistake from being made twice.

**When to add a lesson:**

- A bug was caused by a non-obvious pitfall.
- An approach was tried and failed for a reason worth remembering.
- A tool or API behaved unexpectedly.
- A convention was violated because it wasn't obvious.
- A debugging session revealed something about the codebase that would
  save time next time.

**Format:**

```markdown
## Lessons Learned

- **[Topic]**: What happened and what to do instead. Keep it to 1-2
  sentences — enough for an agent to understand and avoid the mistake.
```

**Rules:**

- Add lessons as they're discovered, in the same PR that fixes the
  issue.
- Lessons that become formal rules should be promoted to the Critical
  Rules section or to STANDARDS.md, then removed from Lessons Learned.
- Keep entries concise. This section is loaded into context on every
  session — bloat wastes tokens.
- Review periodically and prune entries that are no longer relevant
  (e.g., a workaround for a bug that has been fixed upstream).
