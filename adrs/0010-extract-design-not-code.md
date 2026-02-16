# ADR-0010: Extract Design Decisions from Existing Projects, Not Code

## Status

Accepted

## Context

Several existing projects provide relevant foundations: OCR SDL (semantic
model), OCR Ranger (runtime), OCR Deputy (content library), Crucible
(exercise platform), CybORG (agent interface), HLA/TENA (federation model).

The question for each: fork, wrap, or learn from?

## Decision

For every existing project: extract the design decisions, not the code.

| Project | Disposition |
|---------|------------|
| OCR SDL semantic model | Learn from, redesign. Domain concepts transfer; type system must be rebuilt. |
| OCR SDL-parser | Don't use. New schema needs new parser. |
| OCR Ranger | Study architecture. Internal module boundaries and orchestration patterns. |
| OCR Deputy | Study concept. Content library packaging approach. |
| OCR Handlers | Future reference for cloud API integration patterns. |
| CybORG | Learn interface pattern. Gymnasium-compatible agent interface design. |
| HLA/TENA | Conceptual blueprint. Six runtime service categories, time management model. |

The only external projects consumed as direct dependencies are **OCSF**
(event vocabulary) and eventually **SISO standards** (federation data model).

## Consequences

- Clean-slate implementation unconstrained by others' design choices.
- Higher upfront engineering cost than forking.
- No inherited technical debt, licensing complications, or API constraints.
- Each existing project becomes a source of validated design patterns
  rather than a codebase dependency.
