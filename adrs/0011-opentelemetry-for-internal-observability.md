# ADR-0011: OpenTelemetry for ACES Internal Observability

## Status

Accepted

## Context

ACES uses OCSF as the telemetry contract for exercise events. But ACES's
own components (runtime, providers, experiment harness) also need
observability: logs, metrics, and distributed traces for operational
monitoring and debugging.

OpenTelemetry is already cited as an organizational parallel for ACES
(polyrepo structure, spec/SDK/collector pattern). Using it for ACES's own
internal observability is a natural fit.

## Decision

ACES components use OpenTelemetry for their own operational telemetry:

- **Logs**: `tracing` (Rust) + `structlog` (Python) with JSON output.
  Structured fields, span-based context, correlation IDs per
  exercise/trial.
- **Metrics**: Prometheus-compatible exposition. Key metrics: active
  exercises, provider latency, agent connections, event bus throughput.
  Rust: `metrics` + `metrics-exporter-prometheus`. Python:
  `prometheus-client`.
- **Traces**: Distributed tracing across runtime-provider-agent call
  chains. W3C Trace Context propagated via gRPC metadata. Rust:
  `tracing-opentelemetry`. Python: `opentelemetry-sdk`.

This is distinct from OCSF, which is the exercise-level telemetry contract.
OpenTelemetry observes ACES itself; OCSF observes the exercise.

## Consequences

- Consistent observability across Rust and Python components.
- Standard tooling (Grafana, Jaeger, Prometheus) works out of the box.
- Each exercise is a trace root, enabling end-to-end visibility across
  the runtime-provider-agent boundary.
- Small additional dependency footprint (OpenTelemetry crates/packages).
