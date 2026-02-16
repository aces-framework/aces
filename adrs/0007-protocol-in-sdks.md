# ADR-0007: Wire Protocols Defined in SDKs, Not Centralized

## Status

Accepted

## Context

ACES has three inter-component communication channels: runtime-to-provider,
runtime-to-agent, and CLI-to-runtime. The wire protocol definitions (gRPC
.proto files) could live in a central `aces-protocol` repo or be distributed
across the SDKs.

Three options were evaluated:
- Option A: Single `aces-protocol` repo (like opentelemetry-proto)
- Option B: Each SDK owns its protocol
- Option C: Protocol in SDKs, runtime implements both

## Decision

Option C. Each SDK owns the protocol it defines:

- Provider protocol defined in `aces-provider-sdk` (the contract providers
  fulfill).
- Agent protocol defined in `aces-agent-sdk` (the contract the range offers
  agents).
- Runtime implements both: calls providers via provider-sdk interface, serves
  agents via agent-sdk interface.
- CLI talks to runtime via an API defined in `aces-runtime`.

## Consequences

- Clean dependency graph with no circular dependencies:
  schema -> SDKs -> runtime -> experiment/cli.
- Each SDK is lightweight — it contains only the types and protocol for its
  domain.
- The runtime is the integration hub (depends on both SDKs).
- If many consumers need to generate from many proto sources, a centralized
  `aces-protocol` repo can be extracted later.
