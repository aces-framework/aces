# ACES — Agentic Cyber Environment System

ACES is an open reference architecture for declarative, reproducible cyber
range environments designed for autonomous AI agent research and evaluation.

This repository is the governance hub for the ACES project. It contains
architectural decision records, RFCs for cross-cutting changes, engineering
standards, and cross-repo coordination infrastructure.

**This repo does NOT contain application code.**

## Project Repositories

| Repo | Layer | Language | Purpose |
|------|-------|----------|---------|
| **aces** (this repo) | Governance | — | RFCs, ADRs, community docs, cross-repo CI |
| **aces-schema** | Specification | Protobuf/JSON Schema | Semantic model, type definitions, OCSF mappings |
| **aces-sdl** | Specification | Rust | Parser, validator, verification (tiers 1-2) |
| **aces-provider-sdk** | Instantiation | Rust | Provider contract, conformance tests, gRPC protocol |
| **aces-agent-sdk** | Instantiation | Python | Gymnasium/PettingZoo agent interface |
| **aces-runtime** | Runtime | Rust | Core engine, orchestration, event bus, scoring |
| **aces-experiment** | Experimentation | Python | Experiment harness, trial management, data collection |
| **aces-provider-docker** | Instantiation | Rust | Docker container backend |
| **aces-stdlib** | Content | ACES SDL | Reusable scenario components |
| **aces-cli** | Tooling | Rust | Command-line interface |
| **aces-docs** | Tooling | — | Documentation website |

## Architecture

ACES decomposes cyber range concerns into four layers: Specification (what
the scenario expresses), Runtime (what services coordinate during
execution), Instantiation (how specs bind to backends and participants),
and Experimentation (how experimental controls enable reproducible
research). See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full
architecture reference including dependency graph, interface boundaries,
and build order.

## Standards

Cross-cutting engineering conventions (logging, errors, observability,
testing, security, CI/CD, code style) are defined in
[`STANDARDS.md`](STANDARDS.md).

## Governance

- **ADRs**: Architectural decisions are recorded in [`adrs/`](adrs/).
- **RFCs**: Cross-cutting changes require an RFC in [`rfcs/`](rfcs/).
- **Compatibility matrix**: Tested-compatible versions across repos are
  tracked in [`COMPATIBILITY.md`](COMPATIBILITY.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
