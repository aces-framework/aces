# ADR-0012: DryRun/Plan API in Provider SDK Contract

## Status

Accepted

## Context

The four-tier verification model (ADR-0002) defines Tier 3 (capability)
verification, which asks: "Can the connected backends actually provision
this scenario?" This requires checking provider capabilities against
scenario requirements before committing resources.

Terraform solves this with `terraform plan` — providers implement a planning
mode that reports what would change without actually provisioning. This
pattern is well-proven at scale.

## Decision

The provider SDK contract includes a `DryRun()` / `Plan()` API alongside
`Provision()`. Providers must implement it.

```text
DryRun(spec) -> {
    feasible: bool,
    issues: [{ severity, message, affected_resource }],
    estimated_resources: { cpu, memory, storage, network },
    estimated_duration: duration,
    capabilities_used: [capability],
    capabilities_missing: [capability],
}
```

The runtime calls `DryRun()` across all selected providers before
`Provision()`. If any provider reports infeasible, the exercise fails fast
with actionable diagnostics.

## Consequences

- Scenarios fail fast with useful errors instead of partially provisioning
  and then crashing.
- Provider implementations are more complex — they must reason about
  feasibility without actually provisioning.
- The experiment layer can use `DryRun()` results for pre-execution
  constraint checking (tier 4 pre-checks).
- Resource estimation enables capacity planning for large-scale exercises.
- Providers that cannot implement `DryRun()` (e.g., opaque hardware
  backends) can return "unknown feasibility" — the API must accommodate
  this gracefully.
