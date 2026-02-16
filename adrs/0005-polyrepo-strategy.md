# ADR-0005: Polyrepo Strategy

## Status

Accepted

## Context

ACES is simultaneously an open specification, a runtime framework, a
plugin/provider ecosystem, a content ecosystem, and a research tool. Each
facet has different collaboration patterns, change rates, and communities.

A monorepo simplifies cross-repo coordination and integrated testing. A
polyrepo allows different communities to engage with just the parts they
care about, enforces clean API boundaries, and supports independent access
control.

OpenTelemetry (95 repos) is the closest organizational analogue and uses
polyrepo successfully.

## Decision

Multi-repo (polyrepo) with a shared governance hub (this repo).

Coordination mechanisms: SemVer versioning, RFC process for cross-cutting
changes, compatibility matrix, cross-repo integration tests.

Backend providers MUST be independent repos (an AWS provider shouldn't
pull in VMware dependencies). Content packages are naturally independent.
Core framework repos are separated by layer and concern.

## Consequences

- Cross-repo change coordination requires discipline: SemVer, CI that
  tests downstream consumers, compatibility matrix.
- Schema changes that affect multiple consumers require an RFC.
- Contributors can engage with a single repo without understanding the
  full stack.
- ~17+ repos at maturity. Initial working set: 7 repos (governance,
  schema, sdl, both SDKs, runtime, first provider).
