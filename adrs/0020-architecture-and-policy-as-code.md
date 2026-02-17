# ADR-0020: Architecture and Policy as Code

## Status

Accepted

## Context

ACES repos contain architectural rules and engineering policies that are
currently expressed as prose in STANDARDS.md, ARCHITECTURE.md, and code
review conventions. Prose rules are enforced only by human (or agent)
review, which is unreliable — violations slip through, drift accumulates,
and rules become aspirational rather than enforced.

Meanwhile, the tools exist to make most of these rules machine-checkable:
Rust's module visibility system, Python's `import-linter`, architecture
test patterns, and CI fitness functions. With agentic coding tools
writing and maintaining these checks, the cost of enforcement is
negligible compared to the cost of undetected violations.

This applies both to the internal architecture of each ACES repo (module
boundaries, layer separation, dependency direction) and to cross-cutting
engineering policies (documentation coverage, unsafe usage, dependency
budgets, naming conventions).

ACES's core architecture principle — "specification as auditable
artifact" — applies to exercises. The same principle should apply
reflexively: if a constraint is worth documenting, it is worth encoding
as a check.

## Decision

ACES repos encode architectural constraints and engineering policies as
machine-checkable rules enforced in CI. Prose documentation describes
the intent; code enforces compliance.

### Principle

Every rule in STANDARDS.md that can be expressed as a check SHOULD have a
corresponding enforcement mechanism. The check is authoritative; the
prose is documentation of the check.

### Three Enforcement Layers

#### Layer 1: Language-Level Enforcement

Use the type system, module system, and compiler/interpreter to make
violations unrepresentable or uncompilable where possible.

**Rust:**

- `pub(crate)` and `pub(super)` to enforce module encapsulation. Internal
  modules of the runtime monolith (ADR-0017) are not `pub` — they
  communicate through defined internal traits.
- `#![forbid(unsafe_code)]` on modules and crates that have no business
  using unsafe. Applied at the module level, not blanket.
- `#![deny(missing_docs)]` on library crates.
- Typestate patterns for lifecycle enforcement (ADR-0019 Tier 4).
- Newtypes and marker traits for domain boundaries (e.g., a validated
  `ScenarioSpec` type that can only be constructed through the parser).

**Python:**

- `typing.Protocol` for structural contracts.
- `@final` and `@override` decorators for inheritance contracts.
- `mypy --strict` enforces type annotation coverage (already required).
- `__all__` exports to define public module surface.

#### Layer 2: Architectural Fitness Functions

Tests that assert properties of the architecture itself — not behavior,
but structure. These run in CI like any other test.

**Rust — architecture tests:**

Architecture tests are `#[test]` functions (in a dedicated
`tests/architecture.rs` or similar) that assert structural invariants.
Examples:

- Module dependency direction (parse the module graph, assert no
  backward edges).
- Public API surface audit (assert that only intended types are `pub`).
- Error type hygiene (assert every public error type implements
  `std::error::Error`).

**Rust — `cargo-modules`:**

Generate and check module dependency graphs. Can be run in CI to detect
unexpected module-to-module edges.

**Python — `import-linter`:**

Declare layer rules as configuration. Runs in CI and fails on
violations. Example for a layered Python package:

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

This enforces that `transport` does not import from `api`, `core` does
not import from `api`, etc.

**Python — architecture tests:**

`pytest` tests that assert structural properties. Same pattern as Rust:
inspect the package, assert invariants.

#### Layer 3: CI Policy Checks

Custom CI checks for policies that cross the boundary of a single
language tool.

**Within a repo:**

- Dependency budget enforcement: CI step that counts direct dependencies
  in `Cargo.toml` or `pyproject.toml` and fails if the count exceeds
  a declared budget. Critical for aces-agent-sdk.
- Unsafe audit: CI step that greps for `unsafe` blocks and asserts each
  has a `// SAFETY:` annotation.
- Documentation coverage: `cargo doc --no-deps` with warnings-as-errors
  (Rust), docstring coverage tool (Python).
- Naming convention checks: lint rules or grep-based CI checks for
  convention violations.

**Cross-repo (run from governance):**

- Dependency DAG validation: parse `Cargo.toml` / `pyproject.toml`
  across repos and assert the dependency graph matches the declared
  architecture in ARCHITECTURE.md. No tier-3 repo may depend on a
  tier-4 repo.
- Template drift detection: diff each repo's CI config,
  `.markdownlint.yaml`, and other governed files against the governance
  templates. Flag divergence.
- Schema compatibility: automated breaking-change detection between
  aces-schema versions. Verify that changes labeled as minor actually
  satisfy the minor-version rules in STANDARDS.md §5.

### Application-Code Patterns

Beyond enforcement, repos should prefer declarative constraint
expression in application code:

- **Agent action validation**: the runtime derives permitted actions from
  the scenario specification declaratively. Validation is data-driven
  (spec → rule set → check), not a hand-coded `if` cascade.
- **Provider capability matching**: the DryRun/Plan API (ADR-0012)
  checks feasibility declaratively against provider capability
  declarations.
- **Scoring rules**: scoring semantics are driven by the spec's
  assessment definitions, not hardcoded per scoring mode.
- **Schema validation**: constraints are expressed in the schema type
  system and enforced at parse/deserialization boundaries, not
  re-implemented in each consumer.

The general rule: if a constraint is data that varies per scenario, role,
or provider, express it as data (in the spec or configuration) and write
a generic engine that evaluates it. If a constraint is structural and
universal, encode it in the type system or module system.

### What This Does Not Cover

- Formal verification of code correctness — covered by ADR-0019.
- Governance process automation (RFC workflow, ADR numbering) — out of
  scope, low value relative to effort.
- Runtime policy enforcement in production (e.g., OPA for API
  authorization) — deferred until there is a multi-tenant deployment
  scenario.

## Consequences

- Architectural drift is detected automatically rather than in code
  review.
- New contributors (human or agent) get immediate CI feedback when they
  violate structural rules, rather than learning conventions through
  rejected PRs.
- The governance repo gains cross-repo CI checks (dependency DAG,
  template drift, schema compatibility). This is new infrastructure.
- Each code repo gains an architecture test file and, for Python repos,
  an `import-linter` configuration. This is a small addition per repo.
- Agent SDK's strict dependency budget becomes a CI-enforced number, not
  a prose aspiration.
- Declarative policy patterns in application code (action validation,
  capability matching, scoring) reduce the surface area for bugs and
  make the runtime's behavior auditable from the specification alone.
- Adds `cargo-modules` and `import-linter` to the toolchain. Both are
  lightweight and well-maintained.
