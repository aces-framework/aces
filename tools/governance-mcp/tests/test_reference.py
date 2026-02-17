"""Tests for reference tools: list_adrs, get_adr, get_standard, etc."""

from __future__ import annotations

from pathlib import Path

from aces_governance_mcp.server import (
    get_adr,
    get_architecture,
    get_standard,
    get_template,
    list_adrs,
    search_governance,
)


class TestListAdrs:
    """Tests for list_adrs tool."""

    def test_returns_all_adrs(self, governance_repo: Path) -> None:
        result = list_adrs()
        assert "0001" in result
        assert "0019" in result

    def test_includes_titles(self, governance_repo: Path) -> None:
        result = list_adrs()
        assert "Rust Core" in result
        assert "Formal Methods" in result

    def test_includes_status(self, governance_repo: Path) -> None:
        result = list_adrs()
        assert "Accepted" in result

    def test_excludes_template(self, governance_repo: Path) -> None:
        result = list_adrs()
        assert "TEMPLATE" not in result


class TestGetAdr:
    """Tests for get_adr tool."""

    def test_by_number_padded(self, governance_repo: Path) -> None:
        result = get_adr("0001")
        assert "Rust Core + Python Periphery" in result
        assert "## Decision" in result

    def test_by_number_unpadded(self, governance_repo: Path) -> None:
        result = get_adr("1")
        assert "Rust Core + Python Periphery" in result

    def test_by_keyword_single_match(self, governance_repo: Path) -> None:
        result = get_adr("formal methods")
        assert "ADR-0019" in result

    def test_by_keyword_multiple_matches(self, governance_repo: Path) -> None:
        # Both ADRs mention "Rust" or similar terms.
        result = get_adr("Accepted")
        # Should return either full content (single) or a list.
        assert "0001" in result or "0019" in result

    def test_no_match(self, governance_repo: Path) -> None:
        result = get_adr("nonexistent-topic-xyz")
        assert "No ADR found" in result or "not found" in result.lower()


class TestGetStandard:
    """Tests for get_standard tool."""

    def test_by_section_number(self, governance_repo: Path) -> None:
        result = get_standard("1")
        assert "Naming Conventions" in result

    def test_by_keyword(self, governance_repo: Path) -> None:
        result = get_standard("formal methods")
        assert "ADR-0019" in result or "TLA+" in result

    def test_by_keyword_in_body(self, governance_repo: Path) -> None:
        result = get_standard("hand-edit")
        assert "dependency" in result.lower() or "cargo add" in result.lower()

    def test_no_match(self, governance_repo: Path) -> None:
        result = get_standard("nonexistent-section-xyz")
        assert "No section found" in result or "not found" in result.lower()

    def test_multiple_matches_returns_titles(self, governance_repo: Path) -> None:
        # "aces" appears in multiple sections.
        result = get_standard("aces")
        # Should either return content or list of matching sections.
        assert len(result) > 0


class TestGetArchitecture:
    """Tests for get_architecture tool."""

    def test_by_keyword(self, governance_repo: Path) -> None:
        result = get_architecture("dependency")
        assert "upstream" in result.lower() or "dependencies" in result.lower()

    def test_by_section_name(self, governance_repo: Path) -> None:
        result = get_architecture("principles")
        assert "Parnas" in result

    def test_no_match(self, governance_repo: Path) -> None:
        result = get_architecture("nonexistent-section-xyz")
        assert "No section found" in result or "not found" in result.lower()


class TestSearchGovernance:
    """Tests for search_governance tool."""

    def test_finds_match_in_standards(self, governance_repo: Path) -> None:
        result = search_governance("hand-edit")
        assert "STANDARDS.md" in result

    def test_finds_match_in_adr(self, governance_repo: Path) -> None:
        result = search_governance("formal methods")
        assert "0019" in result

    def test_finds_match_across_files(self, governance_repo: Path) -> None:
        result = search_governance("aces")
        # Should match in multiple files.
        assert "STANDARDS.md" in result or "ARCHITECTURE.md" in result

    def test_no_match(self, governance_repo: Path) -> None:
        result = search_governance("xyzzy-not-a-real-term")
        assert "No results" in result or "no results" in result.lower()


class TestGetTemplate:
    """Tests for get_template tool."""

    def test_exact_name(self, governance_repo: Path) -> None:
        result = get_template("Cargo.toml")
        assert "aces-REPO_NAME" in result

    def test_list_mode(self, governance_repo: Path) -> None:
        result = get_template("list")
        assert "Cargo.toml" in result
        assert "pyproject.toml" in result
        assert "CLAUDE.md" in result

    def test_fuzzy_match(self, governance_repo: Path) -> None:
        result = get_template("cargo")
        assert "aces-REPO_NAME" in result

    def test_not_found(self, governance_repo: Path) -> None:
        result = get_template("nonexistent-file.xyz")
        assert "not found" in result.lower()
