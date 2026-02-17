# ADR-0015: gRPC as Wire Protocol

## Status

Accepted

## Context

ACES components communicate across language boundaries (Rust core, Python
periphery) and across process boundaries (runtime to providers, runtime to
agents, CLI to runtime). A wire protocol must be chosen.

Options evaluated:

1. **gRPC (with protobuf)** — Strong typing, multi-language code generation,
   streaming support, HTTP/2 transport, bidirectional streaming.
2. **REST/HTTP** — Simpler, lower barrier, broadly supported, but untyped
   without additional schema tooling (OpenAPI).
3. **Both** — gRPC for inter-component, REST for external/CLI access.

## Decision

gRPC with Protocol Buffers for all inter-component communication.

- Runtime ↔ Provider: gRPC (provider SDK defines the service contract).
- Runtime ↔ Agent: gRPC (agent SDK wraps calls into `gymnasium.Env`).
- CLI ↔ Runtime: gRPC (runtime exposes a management API).

Specific libraries per ADR-0001: `tonic` + `prost` (Rust), `grpcio` +
`protobuf` (Python).

No REST API is provided. External tools that need HTTP access can use
gRPC-Gateway or grpc-web as a translation layer, added later if demand
materializes.

## Consequences

- Proto files are the single source of truth for every inter-component
  contract. Changes to protos are visible, reviewable, and versioned.
- Multi-language stubs are generated automatically — Rust and Python always
  agree on message shapes.
- Streaming support is available from day one for agent observations and
  exercise event feeds, without switching protocols.
- Higher barrier to casual integration than REST. Mitigated by the agent SDK
  and CLI abstracting gRPC away from end users (researchers never see proto
  files).
- Debugging is slightly harder than REST (binary protocol). Mitigated by
  gRPC reflection and tooling (grpcurl, Postman gRPC support).
- Proto files live in SDKs per ADR-0007, not in a central protocol repo.
