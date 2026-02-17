# ADR-0017: Runtime Monolith with Modular Internals

## Status

Accepted

## Context

The ACES runtime layer encompasses multiple distinct concerns: exercise
lifecycle management, event bus (pub/sub), orchestration engine, state
management, time services, ownership management, provider coordination,
participant coordination, scoring engine, and telemetry collection.

These could be organized as:

1. **Multiple repos** — One repo per runtime service (e.g., aces-event-bus,
   aces-orchestrator, aces-scoring-engine).
2. **Single repo, modular internals** — One aces-runtime repo with clear
   internal module boundaries.

## Decision

Single repo (`aces-runtime`) with modular internal architecture.

Internal modules are designed **as if they were separate repos**: clean
interfaces between modules, no shared mutable state, explicit dependency
direction within the crate. This means future extraction into separate
repos (or separate binaries) is non-disruptive.

Internal module boundaries:

| Module | Responsibility |
|--------|---------------|
| Lifecycle manager | Create, start, pause, resume, stop, checkpoint, rollback, branch |
| Event bus | Pub/sub distribution + relevance-based routing (HLA data distribution) |
| Orchestration engine | Timeline execution, condition monitoring, inject management |
| State manager | Shared exercise state, attribute updates |
| Time services | Coordinated time across components, speed multipliers |
| Ownership manager | Transfer of control of exercise objects between participants |
| Provider coordinator | Calls providers via aces-provider-sdk interface |
| Participant coordinator | Agent/human connection management, interface generation |
| Scoring engine | OCSF-based assessment pipeline |
| Telemetry collector | OCSF events, agent decisions, state transitions |
| Runtime API | Management API consumed by CLI and external tools |

Federation support starts as an internal module and is the most likely
candidate for future extraction.

## Consequences

- Single integration test suite covers the full runtime — no cross-repo
  test coordination for runtime-internal concerns.
- One repo to build, deploy, and release. Simpler CI, simpler dependency
  management.
- Nobody is contributing to "just the event bus" on day one. When team
  size or deployment topology demands splitting, the modular boundaries
  make extraction straightforward.
- Risk: internal module boundaries degrade over time if discipline lapses.
  Mitigated by Rust's module system (pub/pub(crate) visibility) and code
  review enforcing interface contracts.
- Cargo workspace can be used to enforce compile-time module boundaries
  if the single-crate approach proves insufficient.
