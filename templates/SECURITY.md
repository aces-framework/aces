# Security Policy — aces-REPO_NAME

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report
it responsibly. **Do not open a public issue.**

### Preferred: GitHub Security Advisories

Report via GitHub's private vulnerability reporting:

1. Go to the **Security** tab of this repository.
2. Click **Report a vulnerability**.
3. Fill in the details and submit.

This keeps the report private until a fix is available.

### Alternative: Email

Send an email to **security@aces-framework.org** with:

- Description of the vulnerability.
- Steps to reproduce.
- Affected version(s).
- Any suggested fix (optional).

Use our PGP key (published on the Security tab) if you want to encrypt
the report.

## Response Timeline

| Milestone | Target |
|-----------|--------|
| Acknowledgment | 3 business days |
| Initial assessment | 7 business days |
| Fix target | 30 days for critical/high severity |
| Public disclosure | 90 days (coordinated) |

We follow a **90-day coordinated disclosure** policy. If a fix is not
ready within 90 days, we will work with the reporter to agree on an
extended timeline or a partial disclosure.

## Scope

This policy covers the `aces-REPO_NAME` codebase and its official
releases.

### In Scope

- Vulnerabilities in the code, dependencies, or build pipeline.
- Configuration issues that could lead to security exposure.
- Authentication or authorization bypasses.

### Out of Scope

- **Intentionally vulnerable content**: The `aces-stdlib` repository
  contains scenario content that is *vulnerable by design* (e.g.,
  deliberately misconfigured services, known-exploitable software).
  These are not security bugs — they are the point of the project.
- Vulnerabilities in third-party dependencies that are already publicly
  disclosed (report these upstream; we track advisories via automated
  scanning).
- Social engineering or phishing attacks against project maintainers.

## Credit

We credit reporters in the GitHub Security Advisory unless they prefer
to remain anonymous. Let us know your preference when reporting.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | Yes |
| Previous minor | Best effort |
| Pre-release / main | Best effort |

During the pre-1.0 phase, only the latest release receives security
fixes. Post-1.0, the support policy will be updated.
