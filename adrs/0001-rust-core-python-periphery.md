# ADR-0001: Rust Core + Python Periphery

## Status

Accepted

## Context

ACES requires a primary implementation language for its core framework (sdl,
runtime, cli, provider-sdk) and a language for its research-facing components
(agent-sdk, experiment). The paper does not prescribe a language. Candidates
evaluated: Rust, Go, Java, Python, TypeScript.

Key factors: AI-assisted development (Opus 4.6+) reduces the weight of
contributor pool size and learning curve. Type system expressiveness and
safety guarantees become more important when AI generates significant code,
as stronger type systems catch AI-introduced errors at compile time.

Go's advantages (infrastructure ecosystem, fast development, large community)
are primarily human-ergonomic and carry less weight in an AI-assisted workflow.
Java's formal verification tooling advantage is real but narrow — ACES's
verification needs (graph analysis, automata operations, SMT solving) are
available in Rust via z3 crate and petgraph. The missing automata theory
library will be built as an independent crate (see ADR-0004).

The agent SDK and experiment harness must be Python regardless of core
language choice (Gymnasium, PyTorch, MLflow ecosystems).

## Decision

- **Rust** for: aces-sdl, aces-runtime, aces-cli, aces-provider-sdk,
  aces-provider-docker.
- **Python** for: aces-agent-sdk, aces-experiment.
- **Language-agnostic** for: aces-schema (protobuf or JSON Schema).
- gRPC (tonic/prost in Rust, grpcio in Python) as the wire protocol
  between Rust and Python components.

## Consequences

- Two-language project. Simpler than three (the Java/Kotlin split-core
  alternative) while still using the best tool per domain.
- Rust's ownership model prevents concurrency bugs in the runtime — critical
  for a long-running service managing time-sensitive operations.
- Single binary deployment for all Rust components.
- OCR Ranger (Rust) patterns become directly study-able.
- The Rust formal methods ecosystem is thinner than Java's. The automata
  theory gap must be filled (ADR-0004).
- Provider implementations can be any language (gRPC contract), but the
  first provider and SDK are Rust.
