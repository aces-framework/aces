# ADR-0018: Project Standards and Conventions

## Status

Accepted

## Context

ACES is a polyrepo project (ADR-0005) spanning two languages (ADR-0001)
with communication over gRPC (ADR-0015). Without explicit cross-cutting
conventions, repos will diverge on naming, configuration patterns, package
formats, and identifier schemes. This divergence is invisible early but
becomes expensive to fix once multiple repos are in active development.

These conventions are individually small but collectively define whether
the project feels like one coherent system or a loose collection of repos
that share a name.

## Decision

Adopt and maintain a `STANDARDS.md` document in the governance repo that
defines cross-cutting conventions for:

1. **Naming conventions** — GitHub org (`aces-framework`), repo naming
   (`aces-*`, lowercase, hyphen-separated), provider pattern
   (`aces-provider-{backend}`), SDK pattern (`aces-{role}-sdk`),
   per-language package naming.

2. **Configuration precedence** — Uniform four-level precedence across all
   components: defaults < config file (TOML) < env vars (`ACES_` prefix) <
   CLI flags. Secrets never in config files.

3. **Content package format** — Standard directory layout with
   `aces-package.yaml` manifest declaring name, version, schema
   compatibility, and dependencies. Git-based distribution initially,
   registry deferred.

4. **Identifier format** — UUIDv7 for all runtime identifiers (exercises,
   trials, agents, provider instances).

5. **Cross-language naming** — PascalCase for protobuf, snake_case for
   config keys, SCREAMING_SNAKE_CASE with `ACES_` prefix for env vars.

These conventions are binding for all repos under the `aces-framework`
organization. Changes to STANDARDS.md follow the normal PR review process
(no RFC required unless the change is breaking).

## Consequences

- New repos can be bootstrapped with known conventions from day one. The
  `templates/` directory in the governance repo instantiates these
  standards.
- Contributors moving between repos encounter consistent patterns.
- The config precedence standard means every component is debuggable the
  same way — check the env var, check the config file, check the default.
- The content package format enables tooling (CLI `aces package` commands)
  before a registry exists.
- Naming conventions prevent the org from accumulating inconsistent repo
  names that are awkward to rename once published.
- STANDARDS.md is a living document. Conventions can be added or revised
  as the project matures, without the overhead of a full ADR for each
  minor convention.
