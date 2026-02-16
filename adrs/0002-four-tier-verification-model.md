# ADR-0002: Four-Tier Verification Model

## Status

Accepted

## Context

The paper identifies verification as an open question: "Whether formal
verification is complementary to the specification layer or to the runtime
layer is an open design question" (Section 9).

Initial analysis identified two verification domains (specification-level
and instantiation-level). Cross-referencing against Terraform's
validate/plan/postcondition model and the GTDL/LangAFDL formal verification
work reveals four distinct domains that should not be conflated.

## Decision

ACES adopts a four-tier verification model:

| Tier | Domain | Question | Where | Analogy |
|------|--------|----------|-------|---------|
| 1. Static | Syntax + structure | Well-formed? Type errors? Missing refs? | aces-sdl | `terraform validate` |
| 2. Semantic | Formal/logical | Do detection rules cover attack paths? | aces-sdl | GTDL/LangAFDL proofs |
| 3. Capability | Infrastructure | Can backends provision this spec? | Provider SDK `DryRun()` + runtime | `terraform plan` |
| 4. Constraint | Experimental | Does the environment meet research constraints? | aces-experiment | Terraform postconditions |

Tier 3 requires a `DryRun()` / `Plan()` API in the provider SDK contract.
Tier 4 requires both pre-execution rejection (impossible constraints) and
post-provisioning validation (actual environment state).

## Consequences

- Provider SDK contract is larger: providers must implement `DryRun()` in
  addition to `Provision()`.
- Semantic verification (tier 2) depends on the external automata crate
  (ADR-0004) for LTS/language inclusion operations.
- The experiment layer is not just a wrapper around the runtime — it has
  authority to reject executions that violate methodology constraints.
- Clear separation prevents conflating "is this YAML valid?" with "will
  this detection rule actually catch this attack?"
