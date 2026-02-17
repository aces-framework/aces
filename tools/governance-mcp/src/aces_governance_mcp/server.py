"""ACES Governance MCP Server.

Provides tools for querying governance documentation, validating repo
compliance, and proposing ADRs.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_SIBLING_LAYOUT_MSG = (
    "ACES repos must be siblings in a shared parent directory:\n"
    "  parent/\n"
    "    aces/           ← governance repo\n"
    "    aces-schema/\n"
    "    aces-runtime/\n"
    "    ...\n"
    "Set ACES_GOVERNANCE_REPO to the absolute path of the governance repo "
    "if your layout differs."
)

_REQUIRED_GOVERNANCE_FILES = ("STANDARDS.md", "ARCHITECTURE.md", "adrs")


def _resolve_repo_root() -> Path:
    """Locate the governance repo root.

    Resolution order:
    1. ACES_GOVERNANCE_REPO env var (absolute path).
    2. Auto-detect from package location (server lives inside the repo).
    """
    env = os.environ.get("ACES_GOVERNANCE_REPO")
    if env:
        root = Path(env).resolve()
    else:
        # server.py is at tools/governance-mcp/src/aces_governance_mcp/server.py
        root = Path(__file__).resolve().parents[4]

    if not root.is_dir():
        msg = f"Governance repo not found at {root}\n\n{_SIBLING_LAYOUT_MSG}"
        raise RuntimeError(msg)

    missing = [f for f in _REQUIRED_GOVERNANCE_FILES if not (root / f).exists()]
    if missing:
        msg = (
            f"Directory {root} does not look like the ACES governance repo — "
            f"missing: {', '.join(missing)}\n\n{_SIBLING_LAYOUT_MSG}"
        )
        raise RuntimeError(msg)

    return root


REPO_ROOT = _resolve_repo_root()

GITHUB_ORG = "aces-framework"
GITHUB_REPO = f"{GITHUB_ORG}/aces"

mcp = FastMCP(
    "aces-governance",
    instructions=(
        "ACES Governance Agent. Provides access to project standards, "
        "architecture decisions (ADRs), templates, and compliance checks "
        "for the ACES framework. Use this to understand project conventions, "
        "validate repos against standards, and propose new ADRs.\n\n"
        "NOTE: All ACES repos must be sibling directories under a shared "
        "parent (e.g. ~/src/aces/). The governance repo ('aces') must be "
        "a sibling of the repo you are working in."
    ),
)


# ── Helpers ──────────────────────────────────────────────────────────


def _read_file(path: Path) -> str:
    """Read a file and return its content."""
    return path.read_text(encoding="utf-8")


def _parse_sections(content: str, level: int = 2) -> dict[str, str]:
    """Parse markdown into sections by heading level."""
    pattern = rf"^{'#' * level} (.+)$"
    sections: dict[str, str] = {}
    current_title = ""
    current_lines: list[str] = []

    for line in content.splitlines():
        match = re.match(pattern, line)
        if match:
            if current_title:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = match.group(1).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_title:
        sections[current_title] = "\n".join(current_lines).strip()

    return sections


def _adrs_dir() -> Path:
    return REPO_ROOT / "adrs"


def _templates_dir() -> Path:
    return REPO_ROOT / "templates"


# ── Reference Tools ──────────────────────────────────────────────────


@mcp.tool()
def list_adrs() -> str:
    """List all ADRs with their numbers, titles, and status."""
    adrs_path = _adrs_dir()
    results: list[str] = []

    for path in sorted(adrs_path.glob("[0-9]*.md")):
        content = _read_file(path)
        title_match = re.match(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else path.stem
        status_match = re.search(r"^## Status\s*\n+\s*(\w+)", content, re.MULTILINE)
        status = status_match.group(1) if status_match else "Unknown"
        results.append(f"- {path.stem}: {title} [{status}]")

    return "\n".join(results) if results else "No ADRs found."


@mcp.tool()
def get_adr(identifier: str) -> str:
    """Retrieve an ADR by number or search by keyword.

    Args:
        identifier: ADR number (e.g. '0019', '19') or keyword to search.
    """
    adrs_path = _adrs_dir()

    # Try numeric lookup first.
    num = identifier.strip().zfill(4)
    matches = list(adrs_path.glob(f"{num}-*.md"))
    if matches:
        return _read_file(matches[0])

    # Keyword search.
    query = identifier.lower()
    results: list[tuple[str, Path]] = []
    for path in sorted(adrs_path.glob("[0-9]*.md")):
        content = _read_file(path)
        if query in content.lower():
            title_match = re.match(r"^# (.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else path.stem
            results.append((f"- {path.stem}: {title}", path))

    if not results:
        return f"No ADR found matching '{identifier}'."
    if len(results) == 1:
        return _read_file(results[0][1])

    return "Multiple ADRs match:\n" + "\n".join(r[0] for r in results)


@mcp.tool()
def get_standard(section: str) -> str:
    """Retrieve a section of STANDARDS.md by number or keyword.

    Args:
        section: Section number (e.g. '15') or keyword (e.g. 'formal methods').
    """
    content = _read_file(REPO_ROOT / "STANDARDS.md")
    sections = _parse_sections(content, level=2)

    # Try exact section number match.
    for title, body in sections.items():
        num_match = re.match(r"(\d+)\.", title)
        if num_match and num_match.group(1) == section.strip():
            return body

    # Keyword search.
    query = section.lower()
    matches = [
        (title, body)
        for title, body in sections.items()
        if query in title.lower() or query in body.lower()
    ]

    if not matches:
        return f"No section found matching '{section}'."
    if len(matches) == 1:
        return matches[0][1]

    titles = "\n".join(f"- {title}" for title, _ in matches)
    return (
        f"Multiple sections match:\n{titles}\n\n"
        "Refine your query or use a section number."
    )


@mcp.tool()
def get_architecture(section: str) -> str:
    """Retrieve a section of ARCHITECTURE.md by keyword.

    Args:
        section: Keyword to search (e.g. 'dependency graph').
    """
    content = _read_file(REPO_ROOT / "ARCHITECTURE.md")
    sections = _parse_sections(content, level=2)

    query = section.lower()
    matches = [
        (title, body)
        for title, body in sections.items()
        if query in title.lower() or query in body.lower()
    ]

    if not matches:
        return f"No section found matching '{section}'."
    if len(matches) == 1:
        return matches[0][1]

    titles = "\n".join(f"- {title}" for title, _ in matches)
    return f"Multiple sections match:\n{titles}"


@mcp.tool()
def search_governance(query: str) -> str:
    """Full-text search across all governance documents.

    Args:
        query: The search term or phrase.
    """
    search_query = query.lower()
    results: list[str] = []

    search_files = [
        REPO_ROOT / "STANDARDS.md",
        REPO_ROOT / "ARCHITECTURE.md",
        REPO_ROOT / "templates" / "README.md",
    ]
    search_files.extend(sorted(_adrs_dir().glob("[0-9]*.md")))

    for path in search_files:
        if not path.exists():
            continue
        content = _read_file(path)
        if search_query not in content.lower():
            continue

        rel_path = path.relative_to(REPO_ROOT)
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if search_query in line.lower():
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                excerpt = "\n".join(lines[start:end])
                results.append(f"**{rel_path}** (line {i + 1}):\n```\n{excerpt}\n```")
                break  # One excerpt per file.

    if not results:
        return f"No results for '{query}'."

    return "\n\n".join(results)


@mcp.tool()
def get_template(name: str) -> str:
    """Retrieve a template file by name.

    Args:
        name: Template filename (e.g. 'Cargo.toml') or 'list' for all.
    """
    templates_path = _templates_dir()

    if name.lower() == "list":
        files: list[str] = []
        for path in sorted(templates_path.rglob("*")):
            if path.is_file():
                rel = path.relative_to(templates_path)
                files.append(f"- {rel}")
        return "Available templates:\n" + "\n".join(files)

    # Direct match.
    target = templates_path / name
    if target.exists() and target.is_file():
        return _read_file(target)

    # Fuzzy match.
    query = name.lower()
    matches = [
        p for p in templates_path.rglob("*") if p.is_file() and query in p.name.lower()
    ]

    if not matches:
        return (
            f"Template '{name}' not found. "
            "Use get_template('list') to see available templates."
        )
    if len(matches) == 1:
        return _read_file(matches[0])

    names = "\n".join(f"- {m.relative_to(templates_path)}" for m in matches)
    return f"Multiple templates match:\n{names}"


# ── Validation Tools ─────────────────────────────────────────────────

_COMMON_FILES = [
    "LICENSE",
    "CHANGELOG.md",
    "CLAUDE.md",
    "SECURITY.md",
    ".markdownlint.yaml",
    ".pre-commit-config.yaml",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/workflows/ci.yaml",
]

_TYPE_FILES: dict[str, list[str]] = {
    "rust": [
        "Cargo.toml",
        "cargo-deny.toml",
        "rust-toolchain.toml",
        ".gitignore",
        ".mcp.json",
        ".github/ISSUE_TEMPLATE/bug-report.md",
    ],
    "python": [
        "pyproject.toml",
        ".gitignore",
        ".mcp.json",
        ".github/ISSUE_TEMPLATE/bug-report.md",
    ],
    "governance": [
        ".github/ISSUE_TEMPLATE/adr-proposal.md",
        ".github/ISSUE_TEMPLATE/rfc-proposal.md",
    ],
}

_CI_EXPECTED_JOB: dict[str, str] = {
    "rust": "check",
    "python": "check",
    "governance": "lint",
}

_CI_EXPECTED_STEPS: dict[str, list[str]] = {
    "rust": ["cargo fmt", "cargo clippy", "cargo test", "cargo doc", "cargo deny"],
    "python": ["ruff check", "ruff format", "mypy", "pytest", "pip-audit"],
    "governance": ["pre-commit run"],
}

# Tier assignments from ARCHITECTURE.md.
_TIERS: dict[str, int] = {
    "aces": 0,
    "aces-schema": 1,
    "aces-sdl": 1,
    "aces-provider-sdk": 2,
    "aces-agent-sdk": 2,
    "aces-runtime": 3,
    "aces-experiment": 3,
    "aces-provider-docker": 4,
    "aces-cli": 5,
    "aces-stdlib": 5,
}


@mcp.tool()
def check_repo_compliance(repo_path: str, repo_type: str) -> str:
    """Check a repo's compliance with ACES governance standards.

    Args:
        repo_path: Absolute path to the repo root.
        repo_type: One of 'rust', 'python', or 'governance'.
    """
    if repo_type not in ("rust", "python", "governance"):
        return f"Invalid repo_type: {repo_type}. Must be rust, python, or governance."

    repo = Path(repo_path)
    if not repo.is_dir():
        return f"Directory not found: {repo_path}"

    findings: list[str] = []
    passes: list[str] = []

    # Check required files.
    required = _COMMON_FILES + _TYPE_FILES[repo_type]
    for fname in required:
        fpath = repo / fname
        if fpath.exists():
            passes.append(f"PASS: {fname} exists")
        else:
            findings.append(f"FAIL: {fname} missing")

    # Check repo naming.
    repo_name = repo.name
    if not repo_name.startswith("aces"):
        findings.append(f"WARN: Repo name '{repo_name}' does not start with 'aces-'")
    else:
        passes.append(f"PASS: Repo name '{repo_name}' follows naming convention")

    # Rust-specific checks.
    if repo_type == "rust":
        cargo_toml = repo / "Cargo.toml"
        if cargo_toml.exists():
            content = _read_file(cargo_toml)
            if 'license = "Apache-2.0"' in content:
                passes.append("PASS: Cargo.toml specifies Apache-2.0 license")
            else:
                findings.append("FAIL: Cargo.toml missing Apache-2.0 license")

        lib_rs = repo / "src" / "lib.rs"
        if lib_rs.exists():
            content = _read_file(lib_rs)
            if "deny(missing_docs)" in content:
                passes.append("PASS: lib.rs has deny(missing_docs)")
            else:
                findings.append(
                    "WARN: lib.rs missing #![deny(missing_docs)] (STANDARDS.md §16)"
                )

    # Python-specific checks.
    if repo_type == "python":
        pyproject = repo / "pyproject.toml"
        if pyproject.exists():
            content = _read_file(pyproject)
            if "strict = true" in content or "strict=true" in content:
                passes.append("PASS: mypy strict mode enabled")
            else:
                findings.append("FAIL: pyproject.toml missing mypy strict = true")
            if 'license = "Apache-2.0"' in content:
                passes.append("PASS: pyproject.toml specifies Apache-2.0 license")
            else:
                findings.append("FAIL: pyproject.toml missing Apache-2.0 license")

    # Template drift: markdownlint config.
    mdlint = repo / ".markdownlint.yaml"
    template_mdlint = _templates_dir() / "markdownlint.yaml"
    if mdlint.exists() and template_mdlint.exists():
        if _read_file(mdlint) == _read_file(template_mdlint):
            passes.append("PASS: .markdownlint.yaml matches governance template")
        else:
            findings.append(
                "WARN: .markdownlint.yaml differs from governance template "
                "(template drift)"
            )

    # CI workflow content checks.
    ci_path = repo / ".github" / "workflows" / "ci.yaml"
    if ci_path.exists():
        ci_content = _read_file(ci_path)
        expected_job = _CI_EXPECTED_JOB[repo_type]
        if f"  {expected_job}:" in ci_content:
            passes.append(f"PASS: CI job name is '{expected_job}'")
        else:
            findings.append(
                f"FAIL: CI workflow missing expected job name '{expected_job}'"
            )
        for step in _CI_EXPECTED_STEPS[repo_type]:
            if step in ci_content:
                passes.append(f"PASS: CI contains '{step}' step")
            else:
                findings.append(f"FAIL: CI workflow missing expected step '{step}'")

    # Build report.
    report_lines = [
        "# Compliance Report",
        f"Repo: {repo_name} ({repo_type})",
        "",
    ]
    if findings:
        report_lines.append(f"## Issues ({len(findings)})")
        report_lines.extend(findings)
        report_lines.append("")

    report_lines.append(f"## Passed ({len(passes)})")
    report_lines.extend(passes)

    return "\n".join(report_lines)


@mcp.tool()
def check_dependency_direction(
    repo_name: str,
    dependencies: list[str],
) -> str:
    """Validate that a repo's dependencies conform to the architecture DAG.

    Args:
        repo_name: The ACES repo name (e.g. 'aces-runtime').
        dependencies: List of ACES repo names this repo depends on.
    """
    repo_tier = _TIERS.get(repo_name)
    if repo_tier is None:
        return f"Unknown repo: {repo_name}. Known repos: {', '.join(sorted(_TIERS))}"

    violations: list[str] = []
    valid: list[str] = []

    for dep in dependencies:
        dep_tier = _TIERS.get(dep)
        if dep_tier is None:
            # External dependency — skip.
            continue
        if dep_tier > repo_tier:
            violations.append(
                f"VIOLATION: {repo_name} (tier {repo_tier}) depends on "
                f"{dep} (tier {dep_tier}) — higher tier dependency"
            )
        else:
            valid.append(f"OK: {dep} (tier {dep_tier})")

    if violations:
        return "Dependency direction violations found:\n" + "\n".join(violations)

    return "All ACES dependencies follow the architecture DAG.\n" + "\n".join(valid)


# ── Governance Action Tools ──────────────────────────────────────────


@mcp.tool()
def propose_adr(
    title: str,
    context: str,
    decision: str,
) -> str:
    """Propose a new ADR by creating a GitHub issue on the governance repo.

    Args:
        title: Proposed ADR title.
        context: Context/motivation for the decision.
        decision: Sketch of the proposed decision.
    """
    # Auto-detect next ADR number.
    adrs_path = _adrs_dir()
    existing = sorted(adrs_path.glob("[0-9]*.md"))
    if existing:
        last_num = int(existing[-1].name[:4])
        next_num = last_num + 1
    else:
        next_num = 1

    issue_title = f"ADR Proposal: {title}"
    issue_body = (
        f"## Proposed ADR-{next_num:04d}: {title}\n\n"
        f"### Status\n\nProposed\n\n"
        f"### Context\n\n{context}\n\n"
        f"### Decision (sketch)\n\n{decision}\n\n"
        f"---\n"
        f"*This ADR proposal was created by the ACES Governance MCP agent.\n"
        f"Discuss here, then create the formal ADR once consensus is reached.*"
    )

    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                GITHUB_REPO,
                "--title",
                issue_title,
                "--body",
                issue_body,
                "--label",
                "governance",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return f"Issue created: {result.stdout.strip()}"
    except FileNotFoundError:
        return "Error: gh CLI not found. Install from https://cli.github.com"
    except subprocess.CalledProcessError as e:
        return f"Error creating issue: {e.stderr.strip() if e.stderr else str(e)}"
    except subprocess.TimeoutExpired:
        return "Error: gh command timed out."


@mcp.tool()
def check_standards_update_needed(lesson: str) -> str:
    """Check whether a lesson learned should be promoted to a formal standard.

    Args:
        lesson: Description of the lesson or pattern observed.
    """
    standards_path = REPO_ROOT / "STANDARDS.md"
    if not standards_path.exists():
        return "Cannot check: STANDARDS.md not found."

    content = _read_file(standards_path)
    sections = _parse_sections(content, level=2)

    # Search for coverage of the lesson's key terms.
    lesson_words = set(lesson.lower().split())
    # Filter out common words.
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "should",
        "must",
        "not",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "and",
        "or",
        "with",
        "that",
        "this",
        "it",
        "all",
        "no",
        "do",
    }
    key_terms = lesson_words - stop_words

    matching_sections: list[str] = []
    for title, body in sections.items():
        body_lower = body.lower()
        matches = sum(1 for term in key_terms if term in body_lower)
        if matches >= 2:  # noqa: PLR2004
            matching_sections.append(title)

    if matching_sections:
        section_list = "\n".join(f"- {s}" for s in matching_sections)
        return (
            f"This lesson appears to be already covered in:\n{section_list}\n\n"
            "Review these sections to confirm coverage is adequate."
        )

    return (
        "This lesson is not covered by current standards. "
        "Consider promoting it to a formal standard in STANDARDS.md "
        "or proposing an ADR if it involves an architectural decision."
    )


# ── Entry Point ──────────────────────────────────────────────────────


def main() -> None:
    """Run the ACES Governance MCP server."""
    mcp.run(transport="stdio")
