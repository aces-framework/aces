# ADR-0009: Apache-2.0 Licensing for Core Framework

## Status

Accepted

## Context

ACES aims for open community development (paper Section 10). The license
must be compatible with academic use, commercial use, and integration with
existing open-source projects (OCSF uses Apache-2.0, OpenTelemetry uses
Apache-2.0).

## Decision

- **Core framework** (schema, sdl, runtime, SDKs, CLI): Apache-2.0.
- **Content packages**: Author's choice, Apache-2.0 recommended for
  community-contributed content.
- **Research docs**: Private.

## Consequences

- Permissive license enables adoption across academic, government, and
  commercial environments.
- Compatible with OCSF (Apache-2.0) and most open-source dependencies.
- No copyleft obligations that would deter enterprise adoption.
- Content authors retain licensing flexibility for their own scenarios.
