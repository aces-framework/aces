# ADR-0019: Formal Methods for Critical Components

## Status

Accepted

## Context

ACES contains several components where correctness is critical and
behavior is precisely specifiable: state machines, protocol sequences,
parsers, and security-boundary validation. Historically, formal methods
carried a steep cost in human effort that made them impractical for most
projects. That calculus has changed: agentic coding tools can draft,
maintain, and verify formal specifications with minimal human overhead.
TLA+ specs, design-by-contract assertions, typestate encodings, and
property-based tests derived from formal properties are all within reach
of an LLM-assisted workflow.

Without a decision, formal methods will be applied inconsistently or not
at all, and the project will rely entirely on example-based tests for
components where stronger guarantees are both achievable and valuable.

## Decision

ACES adopts formal methods at four tiers, applied based on component
criticality. The methods are not aspirational — they are expected to be
written and maintained with the assistance of agentic coding tools as
part of normal development.

### Tier 1: Design-by-Contract (all repos with application code)

Pre-conditions, post-conditions, and invariants on public API boundaries.
In Rust, expressed as `debug_assert!` and doc-comment contracts. In
Python, expressed as runtime assertions on public methods guarded by
`__debug__` (stripped by `python -O` in production).

Required for: all public trait implementations, SDK entry points, and
gRPC service handlers.

### Tier 2: Property Specifications (parser, schema, state machines)

Formally stated properties verified by property-based testing frameworks
(`proptest`/`quickcheck` in Rust, `hypothesis` in Python). Properties
are derived from specifications, not invented ad hoc. Each property
includes a comment citing the invariant it encodes.

Required for: SDL parser (roundtrip fidelity, no-crash-on-any-input,
grammar completeness), schema compatibility checker (monotonicity of
minor versions), state machine transitions (reachability, deadlock
freedom).

### Tier 3: Model Checking (protocols and concurrency)

TLA+ or PlusCal specifications for distributed protocols and concurrent
state machines. Specs live alongside the code they describe (in a `spec/`
directory within the relevant repo) and are checked by the TLC model
checker in CI.

Required for:

- **Exercise lifecycle** — The state machine governing exercise
  creation, provisioning, running, pausing, and teardown
  (`aces-runtime`).
- **Runtime-provider protocol** — The interaction sequence between the
  runtime and providers, including provision, health check, teardown,
  and failure recovery (`aces-runtime`, `aces-provider-sdk`).
- **Runtime-agent protocol** — Session establishment, action
  submission, observation delivery, and disconnection handling
  (`aces-runtime`, `aces-agent-sdk`).
- **Event bus ordering** — Guarantees about event delivery order and
  at-least-once semantics within an exercise (`aces-runtime`).

Encouraged for any new distributed protocol or concurrent subsystem.

### Tier 4: Typestate (Rust repos with lifecycle objects)

Compile-time state machine enforcement using Rust's type system. State
transitions that are invalid become unrepresentable rather than
runtime-checked.

Required for: exercise lifecycle handle in `aces-runtime`, provider
session handle in `aces-provider-sdk`.

Encouraged for any Rust type with a state machine lifecycle.

### Spec Maintenance

Formal specs are living artifacts, not one-time documents. When code
changes, the corresponding spec is updated in the same PR. Agentic tools
are expected to maintain specs — this is explicitly part of their
workflow, not a manual afterthought.

### What Is Explicitly Out of Scope

- **Full formal verification** (e.g., proving a Rust implementation
  correct against a Coq/Lean spec). The cost-benefit does not justify
  this for ACES at current scale.
- **Experiment harness** (`aces-experiment`). Research code under rapid
  iteration; property tests are sufficient.
- **CLI** (`aces-cli`). Thin wrapper over runtime APIs; integration tests
  are sufficient.
- **Content packages** (`aces-stdlib`). Data, not logic.

## Consequences

- Components at trust and protocol boundaries get stronger correctness
  guarantees than example-based tests alone can provide.
- TLA+ specs serve as precise, executable documentation of protocol
  behavior — useful for onboarding and for agents reasoning about the
  codebase.
- Typestate patterns eliminate entire classes of lifecycle bugs at
  compile time in Rust components.
- Agentic tools can use formal specs as ground truth when modifying
  code, reducing the chance of introducing protocol violations.
- Adds a `spec/` directory and TLC model checker to CI for repos with
  Tier 3 requirements. This is new infrastructure but the cost is low
  (TLC runs in seconds for the spec sizes we expect).
- Developers (human or agent) modifying protocol code must update the
  corresponding TLA+ spec. This is an intentional coupling — the spec
  and implementation must stay in sync.
