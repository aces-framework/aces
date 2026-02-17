"""Shared fixtures for governance MCP tests.

Creates a temporary governance repo structure with realistic content
for testing reference, validation, and governance tools.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture()
def governance_repo(tmp_path: Path) -> Path:
    """Create a minimal governance repo structure for testing."""
    # ADRs
    adrs = tmp_path / "adrs"
    adrs.mkdir()

    (adrs / "TEMPLATE.md").write_text("# ADR-XXXX: Title\n\n## Status\n\n")

    (adrs / "0001-rust-core-python-periphery.md").write_text(
        "# ADR-0001: Rust Core + Python Periphery\n\n"
        "## Status\n\nAccepted\n\n"
        "## Context\n\nWe need two languages.\n\n"
        "## Decision\n\nRust core + Python periphery.\n\n"
        "## Consequences\n\nTwo ecosystems to maintain.\n"
    )

    (adrs / "0019-formal-methods-for-critical-components.md").write_text(
        "# ADR-0019: Formal Methods for Critical Components\n\n"
        "## Status\n\nAccepted\n\n"
        "## Context\n\nAgentic tools make formal methods viable.\n\n"
        "## Decision\n\nFour tiers of formal methods.\n\n"
        "## Consequences\n\nStronger guarantees for critical code.\n"
    )

    # STANDARDS.md
    (tmp_path / "STANDARDS.md").write_text(
        "# ACES Project Standards\n\n"
        "## 1. Naming Conventions\n\n"
        "All repos use the prefix `aces-`.\n\n"
        "## 9. Testing Standards\n\n"
        "### Test Pyramid\n\nUnit, integration, contract, e2e.\n"
        "Tests should be written before code (TDD).\n"
        "Test behavior, not implementation.\n\n"
        "## 13. Dependency Management\n\n"
        "NEVER hand-edit dependency versions.\n"
        "Use `cargo add` for Rust, `uv add` for Python.\n\n"
        "## 15. Formal Methods\n\n"
        "Governed by ADR-0019. Four tiers.\n"
        "TLA+ specs for protocols.\n"
    )

    # ARCHITECTURE.md
    (tmp_path / "ARCHITECTURE.md").write_text(
        "# ACES Architecture\n\n"
        "## Architecture Principles\n\nParnas decomposition.\n\n"
        "## Repository Architecture\n\n"
        "Multi-repo with governance hub.\n\n"
        "## Dependency Graph\n\n"
        "aces-schema has zero upstream dependencies.\n\n"
        "## Interface Boundaries\n\n"
        "Each boundary is a contract.\n"
    )

    # Templates
    templates = tmp_path / "templates"
    templates.mkdir()

    (templates / "Cargo.toml").write_text(
        '[package]\nname = "aces-REPO_NAME"\nversion = "0.1.0"\n'
    )
    (templates / "pyproject.toml").write_text(
        '[project]\nname = "aces_REPO_NAME"\nversion = "0.1.0"\n'
    )
    (templates / "CLAUDE.md").write_text("# ACES Project Instructions\n")
    (templates / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n")
    (templates / "LICENSE").write_text("Apache License 2.0\n")
    (templates / "markdownlint.yaml").write_text("default: true\n")
    (templates / "SECURITY.md").write_text(
        "# Security Policy\n\nReport via GitHub Security Advisories.\n"
    )
    (templates / "ci-rust.yaml").write_text(
        "name: CI\njobs:\n  check:\n"
        "    steps:\n"
        "      - run: cargo fmt --check\n"
        "      - run: cargo clippy -- -D warnings\n"
        "      - run: cargo test\n"
        "      - run: cargo doc --no-deps\n"
        "      - run: cargo deny check\n"
    )
    (templates / "ci-python.yaml").write_text(
        "name: CI\njobs:\n  check:\n"
        "    steps:\n"
        "      - run: uv run ruff check .\n"
        "      - run: uv run ruff format --check .\n"
        "      - run: uv run mypy --strict .\n"
        "      - run: uv run pytest\n"
        "      - run: uv run pip-audit\n"
    )
    (templates / "ci-governance.yaml").write_text(
        "name: CI\njobs:\n  lint:\n"
        "    steps:\n      - run: pre-commit run --all-files\n"
    )
    (templates / "README.md").write_text("# ACES Repo Templates\n")

    issue_templates = templates / "ISSUE_TEMPLATE"
    issue_templates.mkdir()
    (issue_templates / "bug-report.md").write_text("---\nname: Bug Report\n---\n")
    (issue_templates / "feature-request.md").write_text(
        "---\nname: Feature Request\n---\n"
    )
    (issue_templates / "config.yml").write_text("blank_issues_enabled: true\n")

    return tmp_path


@pytest.fixture()
def compliant_rust_repo(tmp_path: Path, governance_repo: Path) -> Path:
    """Create a repo that passes all Rust compliance checks."""
    repo = tmp_path / "aces-testcrate"
    repo.mkdir()

    (repo / "LICENSE").write_text("Apache License 2.0\n")
    (repo / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n")
    (repo / "CLAUDE.md").write_text("# ACES Project Instructions\n")
    (repo / "SECURITY.md").write_text("# Security Policy\n\nReport via GitHub.\n")
    (repo / ".markdownlint.yaml").write_text("default: true\n")
    (repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    (repo / "Cargo.toml").write_text(
        '[package]\nname = "aces-testcrate"\n'
        'version = "0.1.0"\nlicense = "Apache-2.0"\n'
    )
    (repo / "cargo-deny.toml").write_text("[licenses]\n")
    (repo / "rust-toolchain.toml").write_text('[toolchain]\nchannel = "1.83"\n')
    (repo / ".gitignore").write_text("/target/\n")
    (repo / ".mcp.json").write_text(
        '{"mcpServers":{"aces-governance":{"command":"uv",'
        '"args":["run","--directory","../aces/tools/governance-mcp",'
        '"aces-governance-mcp"]}}}\n'
    )

    src = repo / "src"
    src.mkdir()
    (src / "lib.rs").write_text("#![deny(missing_docs)]\n//! Test crate.\n")

    github = repo / ".github"
    github.mkdir()
    (github / "pull_request_template.md").write_text("## Description\n")

    issue_templates = github / "ISSUE_TEMPLATE"
    issue_templates.mkdir()
    (issue_templates / "bug-report.md").write_text("---\nname: Bug\n---\n")
    (issue_templates / "config.yml").write_text("blank_issues_enabled: true\n")

    workflows = github / "workflows"
    workflows.mkdir()
    (workflows / "ci.yaml").write_text(
        "name: CI\njobs:\n  check:\n"
        "    steps:\n"
        "      - run: cargo fmt --check\n"
        "      - run: cargo clippy -- -D warnings\n"
        "      - run: cargo test\n"
        "      - run: cargo doc --no-deps\n"
        "      - run: cargo deny check\n"
    )

    return repo


@pytest.fixture()
def compliant_python_repo(tmp_path: Path, governance_repo: Path) -> Path:
    """Create a repo that passes all Python compliance checks."""
    repo = tmp_path / "aces-testpkg"
    repo.mkdir()

    (repo / "LICENSE").write_text("Apache License 2.0\n")
    (repo / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n")
    (repo / "CLAUDE.md").write_text("# ACES Project Instructions\n")
    (repo / "SECURITY.md").write_text("# Security Policy\n\nReport via GitHub.\n")
    (repo / ".markdownlint.yaml").write_text("default: true\n")
    (repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "aces_testpkg"\n'
        'version = "0.1.0"\nlicense = "Apache-2.0"\n\n'
        "[tool.mypy]\nstrict = true\n"
    )
    (repo / ".gitignore").write_text("__pycache__/\n")
    (repo / ".mcp.json").write_text(
        '{"mcpServers":{"aces-governance":{"command":"uv",'
        '"args":["run","--directory","../aces/tools/governance-mcp",'
        '"aces-governance-mcp"]}}}\n'
    )

    github = repo / ".github"
    github.mkdir()
    (github / "pull_request_template.md").write_text("## Description\n")

    issue_templates = github / "ISSUE_TEMPLATE"
    issue_templates.mkdir()
    (issue_templates / "bug-report.md").write_text("---\nname: Bug\n---\n")
    (issue_templates / "config.yml").write_text("blank_issues_enabled: true\n")

    workflows = github / "workflows"
    workflows.mkdir()
    (workflows / "ci.yaml").write_text(
        "name: CI\njobs:\n  check:\n"
        "    steps:\n"
        "      - run: uv run ruff check .\n"
        "      - run: uv run ruff format --check .\n"
        "      - run: uv run mypy --strict .\n"
        "      - run: uv run pytest\n"
        "      - run: uv run pip-audit\n"
    )

    return repo


@pytest.fixture(autouse=True)
def _set_repo_root(
    governance_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[None, None, None]:
    """Point the server at the test governance repo."""
    monkeypatch.setenv("ACES_GOVERNANCE_REPO", str(governance_repo))
    # Re-import to pick up the env var.
    import aces_governance_mcp.server as srv

    monkeypatch.setattr(srv, "REPO_ROOT", governance_repo)
    yield
