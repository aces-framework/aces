# ADR-0021: Defense-in-Depth Security Standards

## Status

Accepted

## Context

ACES is cyber range infrastructure where agents are adversarial by
design, providers instantiate real infrastructure (containers, VMs, cloud
resources), and scenarios may involve real exploits. The security posture
must exceed a typical open-source project.

The current §10 in STANDARDS.md covers gRPC channel security, credential
management, and input validation — 33 lines. This is necessary but
insufficient. Security-relevant content is fragmented across:

- §2 (secrets in config files)
- §13 (cargo-deny for license/vulnerability scanning)
- §14 (unsafe Rust policy, `// SAFETY:` annotations)
- §16 (forbid(unsafe_code), unsafe audit CI)
- ADR-0014 (signed commits, branch protection)
- ADR-0019 (formal methods at trust boundaries)
- Templates (cargo-deny.toml, CI permissions block)

No unified threat model ties these together. No SECURITY.md exists for
vulnerability disclosure. No supply chain scanning for Python
dependencies. CI actions are pinned by mutable tag, not commit SHA.
No container security policy. No documentation of agent sandboxing.

A defense-in-depth approach layers security controls so that no single
failure compromises the system. This is standard practice for
infrastructure that runs untrusted code — which is exactly what ACES
does when agents execute actions in provisioned environments.

## Decision

ACES adopts a five-layer defense-in-depth model. §10 of STANDARDS.md is
expanded to document the full security policy. Each layer addresses a
distinct attack surface.

### Layer 1: Supply Chain Security

Prevent malicious or vulnerable code from entering the dependency tree.

- **Rust**: `cargo-deny` (existing) checks licenses, duplicates, and
  known vulnerabilities. [NOW]
- **Rust**: `cargo-audit` added to CI for advisory database checks.
  [NOW]
- **Python**: `pip-audit` added to CI for known vulnerability checks.
  [NOW]
- **GitHub Actions**: All third-party actions pinned by full commit SHA,
  not mutable tag. [NOW]
- **SBOM generation**: Generate Software Bill of Materials for releases.
  [PRE-1.0]
- **Dependency minimization**: Existing policy (§13) — minimal deps,
  strict budget for agent SDK. [NOW]

### Layer 2: Code Safety

Prevent vulnerabilities in first-party code.

- **Unsafe Rust**: `#![forbid(unsafe_code)]` where possible, `// SAFETY:`
  annotations required (existing §14, §16). [NOW]
- **Static analysis**: `clippy` (Rust), `ruff` + `mypy --strict`
  (Python) — all existing. [NOW]
- **Fuzz testing**: `cargo-fuzz` / AFL for the SDL parser and other trust
  boundaries (existing §10 recommendation). [PRE-1.0]
- **Bounded parsing**: All parsers enforce input size limits and
  recursion depth limits. [NOW]

### Layer 3: CI/CD Security

Prevent the build and release pipeline from being compromised.

- **Minimal permissions**: `permissions: contents: read` default in CI
  workflows (existing). [NOW]
- **Secrets handling**: No secrets in config; env vars or mounted files
  only (existing §2). [NOW]
- **OIDC publishing**: Use OIDC trusted publishing for crates.io/PyPI
  releases — no long-lived API tokens. [PRE-1.0]
- **Signed artifacts**: Release artifacts are signed. [PRE-1.0]
- **Signed commits**: Required by branch protection (ADR-0014). [NOW]

### Layer 4: Runtime and Container Security

Prevent compromise of provisioned infrastructure from escaping the
exercise boundary.

- **Agent sandboxing**: Agents interact via gRPC only. Actions are
  validated against the role's permitted action space. No direct
  infrastructure access. [NOW — by architecture]
- **Container base images**: Prefer distroless or minimal base images.
  Pin by digest, not tag. [PRE-1.0]
- **Image scanning**: Scan container images for vulnerabilities before
  publishing. [PRE-1.0]
- **Network isolation**: Exercise infrastructure is network-isolated
  from the host and from other exercises. Provider implementations
  enforce this. [NOW — provider SDK contract]

### Layer 5: Vulnerability Disclosure

Enable responsible reporting and handling of security issues.

- **SECURITY.md**: Every ACES repo contains a SECURITY.md with
  reporting instructions. [NOW]
- **GitHub Security Advisories**: Private vulnerability reporting
  enabled on all repos. [NOW]
- **Coordinated disclosure**: 90-day window. Reporters credit in
  advisory. [NOW]
- **Scope carve-out**: Intentionally vulnerable content in aces-stdlib
  is excluded from the vulnerability scope (it is vulnerable by
  design). [NOW]

### Maturity Labels

Each control is labeled:

- **[NOW]**: Zero-effort or one-time setup. Implemented with this ADR.
- **[PRE-1.0]**: Requires tooling, infrastructure, or process that is
  not yet in place. Tracked as issues and resolved before 1.0.

### What This Changes

- §10 of STANDARDS.md expands from 3 subsections to 12 subsections.
- A `SECURITY.md` template is added to `templates/`.
- CI templates pin actions by SHA and add supply chain scanning steps.
- `github-setup.sh` enables private vulnerability reporting.
- The compliance checker validates SECURITY.md and new CI steps.
- §10 cross-references existing sections (§2, §13, §14, §16) and ADRs
  (0014, 0019) rather than duplicating their content.

### What This Does Not Change

- Existing security controls (mTLS, credential management, input
  validation, unsafe policy, cargo-deny config) remain where they are.
- No new runtime code. This ADR is about policy and CI enforcement.
- Container orchestration and image scanning tooling are deferred to
  pre-1.0 implementation work.

## Consequences

- Every ACES repo gains a SECURITY.md with disclosure instructions,
  reducing the barrier for security researchers to report issues.
- CI workflows become slightly slower due to supply chain scanning steps
  (cargo-deny, pip-audit). The cost is small relative to the value.
- SHA-pinned actions require manual updates when bumping action versions.
  This is an acceptable trade-off for supply chain integrity.
- The expanded §10 becomes the single index for all security policy,
  with cross-references to detailed sections elsewhere. Developers can
  find all security requirements from one starting point.
- Pre-1.0 items create a clear security roadmap without blocking current
  development.
