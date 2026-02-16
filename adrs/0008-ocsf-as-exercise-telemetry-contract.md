# ADR-0008: OCSF as Exercise Telemetry Contract

## Status

Accepted

## Context

Exercise observation, scoring, and assessment require a common event format
that works across heterogeneous backends (Docker containers, VMs, cloud,
simulation). Without a shared format, scoring logic must be rewritten per
backend, and experimental datasets are structurally incomparable.

OCSF (Open Cybersecurity Schema Framework) is a Linux Foundation project
with 200+ participating organizations and 900+ contributors (v1.4.0, Jan
2025). It defines a normalized taxonomy of cybersecurity events.

## Decision

All exercise observation flows through OCSF-formatted events regardless of
backend. OCSF is the lingua franca for:

- Scoring criteria (reference OCSF event classes, not backend-specific logs)
- Agent observation spaces (OCSF events are the raw observation stream)
- Experimental datasets (structurally comparable across instantiations)
- Provider health reporting (OCSF-formatted status events)

ACES consumes OCSF as an external dependency. OCSF vocabulary mappings are
built into aces-schema (not optional).

## Consequences

- Scoring logic is backend-independent. An AI agent trained on a simulated
  network can be evaluated on a real one using the same scoring pipeline.
- Experimental datasets from different backends are structurally comparable.
- Providers must translate their native events to OCSF. This is work, but
  it's bounded and well-defined.
- ACES is coupled to OCSF's evolution. Mitigated by OCSF's stability (Linux
  Foundation governance, wide industry adoption).
