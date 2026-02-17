# ADR-0013: Trunk-Based Development with Tags

## Status

Accepted

## Context

ACES needs a branching and release strategy. Options considered:

- **Trunk-based (main + tags)**: All work merges to main via PR. Releases
  are git tags cut from main. No release branches, no dev branch.
- **Main + release branches**: Same as trunk-based, but release branches
  (e.g., release/0.1.x) are created for hotfix support on older versions.
- **Dev + main**: A dev integration branch with main always releasable.

The project is pre-v1.0 with no external consumers. A dev branch adds merge
ceremony with zero benefit — there's nobody consuming main who'd be broken
by a bad commit.

## Decision

**Trunk-based development with tags.** All repos.

- All work merges to `main` via PR.
- Releases are git tags (`vX.Y.Z`) cut from `main`.
- CI builds and publishes artifacts (crates.io, PyPI) on tag push.
- No `dev` branch. No release branches. No long-lived branches.
- Feature branches are short-lived (days, not weeks).

**Escalation path**: When external consumers depend on released versions
and need hotfixes without upgrading (likely post-v1.0), add release branches
per-repo as needed. `aces-schema` will likely need this first (downstream
consumers pin to schema versions). Content repos (`aces-stdlib`) may never
need it.

Pre-release versions (`0.x.y`) are expected throughout the pre-v1.0 phase.
No stability promises until 1.0.

## Consequences

- Simplest possible workflow. No merge ceremony overhead.
- `main` is always the latest state of the project.
- No protection against "main is broken" other than PR review and CI.
  This is acceptable for a small team pre-v1.0.
- Release branches can be added per-repo independently when the need arises.
  This is a one-way door that's easy to walk through later.
- Different repos may adopt release branches at different times. This is
  expected and fine.
