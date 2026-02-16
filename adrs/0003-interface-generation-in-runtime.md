# ADR-0003: Interface Generation in Runtime, Not Agent SDK

## Status

Accepted

## Context

ACES agents interact with exercises through observation/action/reward
interfaces derived from the scenario specification and the agent's assigned
role. The question is where this derivation logic lives.

The initial design placed interface generation in the agent SDK. This would
require the Python SDK to depend on the scenario parser, understand the full
semantic model, and process raw OCSF telemetry — making it a heavy library
that ML researchers would avoid.

## Decision

Interface generation lives in the runtime's Participant Coordinator module.
The runtime reads the specification, determines what each agent can see and
do based on their role, and serves the derived interface over gRPC.

The agent SDK is a thin client that wraps gRPC calls into an idiomatic
Python `gymnasium.Env` (or PettingZoo parallel env) class. It has no
dependency on the parser or semantic model.

## Consequences

- Agent SDK is lightweight and `pip`-installable with minimal dependencies
  (grpcio, protobuf, gymnasium, numpy).
- ML researchers interact with a familiar Gymnasium API without needing to
  understand ACES internals.
- The runtime bears more complexity — it must generate and serve interfaces
  per-role.
- Agent SDK development is decoupled from parser/schema evolution — the
  gRPC contract is the only interface.
- Adding a new agent language SDK (e.g., Julia for scientific computing)
  requires only implementing the gRPC client, not reimplementing interface
  generation.
