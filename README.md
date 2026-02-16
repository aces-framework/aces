# ACES — Agentic Cyber Environment System

ACES is an open reference architecture for declarative, reproducible cyber
range environments designed for autonomous AI agent research and evaluation.

This repository is the governance hub for the ACES project. It contains
community guidelines, architectural decision records, RFCs for cross-cutting
changes, and cross-repo coordination infrastructure.

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

ACES decomposes cyber range concerns into four layers:

1. **Specification** — What the scenario expresses (schema + SDL)
2. **Runtime** — What services coordinate during execution
3. **Instantiation** — How specs bind to backends and participants
4. **Experimentation** — How experimental controls enable reproducible research

See the [ACES paper](https://github.com/aces-framework/aces-research-docs)
(private) for the full architectural rationale.

## Governance

- **ADRs**: Architectural decisions are recorded in [`adrs/`](adrs/).
- **RFCs**: Cross-cutting changes require an RFC in [`rfcs/`](rfcs/).
- **Compatibility matrix**: Tested-compatible versions across repos are
  tracked in [`COMPATIBILITY.md`](COMPATIBILITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
