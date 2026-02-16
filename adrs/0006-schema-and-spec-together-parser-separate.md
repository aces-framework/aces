# ADR-0006: Schema + Spec in Same Repo, Parser Separate

## Status

Accepted

## Context

The ACES specification has two artifacts: a formal prose specification
(requirements, rationale, conformance criteria) and a machine-readable
schema (semantic model, type definitions). These could live together or
in separate repos. The parser (concrete syntax) could live with the schema
or separately.

## Decision

**Schema + prose spec in one repo** (`aces-schema`). They describe the same
thing — a schema change requires a spec change. Single PR for a type change
plus its rationale. OCSF uses this pattern (ocsf-schema contains types +
docs + metaschema).

**Parser in a separate repo** (`aces-sdl`). This is a core architectural
principle from the paper: "Define the semantic model first, independently
of any concrete syntax" (Section 8, citing Fowler). Multiple concrete
syntaxes are planned. Consumers that don't parse files (runtime, providers,
agents) shouldn't depend on parser code.

## Consequences

- aces-schema has zero dependency on any parser. It is the stable foundation.
- Multiple parsers can target the same schema (YAML, CUE, custom grammar).
- Schema changes and parser changes can evolve at different rates.
- When aces-schema adds a new type, aces-sdl needs a corresponding syntax
  addition — but this can lag.
