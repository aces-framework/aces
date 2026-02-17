# ADR-0016: Versioning Strategy

## Status

Accepted

## Context

ACES is a polyrepo project (ADR-0005) where multiple repos depend on a
shared schema (aces-schema). Without a versioning contract, schema changes
can silently break downstream consumers, and users have no way to know which
component versions work together.

The problem has two dimensions:

1. **Schema stability** — aces-schema is the foundation. Breaking changes
   propagate to every consumer. The schema needs formal rules about what
   constitutes a breaking change.
2. **Cross-component compatibility** — Each repo releases independently.
   Users and CI need to know which versions of sdl, runtime, provider-sdk,
   and agent-sdk are compatible with which schema version.

## Decision

### All repos: SemVer

Every ACES repo uses Semantic Versioning 2.0.0. Each repo maintains its own
independent version number.

### aces-schema: formal breaking-change rules

Schema versioning carries additional constraints:

- **Major (X.0.0)** — Removing or renaming fields, changing type semantics,
  removing types. Requires RFC (in `aces` governance repo) and a migration
  guide. Expected to be rare.
- **Minor (0.X.0)** — New types, new optional fields, new extensions/profiles.
  Backward compatible. Existing consumers are unaffected.
- **Patch (0.0.X)** — Documentation fixes, constraint clarifications, no
  type changes.

The extension mechanism (profiles, domain-specific additions) allows the
schema to grow at minor versions without breaking anyone.

### Compatibility declarations

Each downstream repo declares which aces-schema version(s) it supports.
Example: "aces-sdl v2.3.0 supports aces-schema >=1.2.0 <2.0.0."

A compatibility matrix is maintained in the `aces` governance repo
(COMPATIBILITY.md) showing tested-compatible version combinations.

### Pre-1.0 expectations

All repos start at 0.x.y. No stability promises until 1.0. Minor versions
may contain breaking changes during 0.x (per SemVer spec). This is
intentional — the pre-1.0 phase prioritizes iteration speed over stability
guarantees.

## Consequences

- Schema breaking changes require RFC, creating a deliberate speed bump
  that prevents casual breakage of the entire project.
- Independent versioning allows providers, content, and tooling to release
  at their own cadence without coordinating with core framework releases.
- The compatibility matrix adds maintenance overhead but prevents "works on
  my machine" integration failures.
- Cross-repo CI (schema release triggers downstream builds) provides fast
  feedback on compatibility without manual testing.
- Content packages (aces-stdlib, community scenarios) declare their
  aces-schema version, making it clear whether a scenario is compatible
  with a given toolchain version.
