"""Tests for governance action tools: propose_adr, check_standards_update_needed."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from aces_governance_mcp.server import (
    check_standards_update_needed,
    propose_adr,
)


class TestProposeAdr:
    """Tests for propose_adr tool."""

    def test_calls_gh_with_correct_args(self, governance_repo: Path) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(
                stdout="https://github.com/aces-framework/aces/issues/42\n"
            )
            propose_adr(
                title="Use TLA+ for Protocols",
                context="Agentic tools make formal methods viable.",
                decision="Require TLA+ specs for all protocols.",
            )

            mock_run.assert_called_once()
            args = mock_run.call_args
            cmd = args[0][0] if args[0] else args[1]["args"]
            assert "gh" in cmd
            assert "issue" in cmd
            assert "create" in cmd
            assert "aces-framework/aces" in " ".join(cmd)

    def test_returns_issue_url(self, governance_repo: Path) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(
                stdout="https://github.com/aces-framework/aces/issues/42\n"
            )
            result = propose_adr(
                title="Test ADR",
                context="Testing.",
                decision="Decide something.",
            )
            assert "https://github.com/aces-framework/aces/issues/42" in result

    def test_auto_detects_next_adr_number(self, governance_repo: Path) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(
                stdout="https://github.com/aces-framework/aces/issues/1\n"
            )
            propose_adr(
                title="Next ADR",
                context="Context.",
                decision="Decision.",
            )

            # The governance_repo fixture has ADRs 0001 and 0019.
            # Next number should be 0020.
            call_args = mock_run.call_args
            cmd = call_args[0][0] if call_args[0] else call_args[1]["args"]
            body_idx = cmd.index("--body") + 1 if "--body" in cmd else -1
            if body_idx > 0:
                assert "0020" in cmd[body_idx]

    def test_error_when_gh_not_found(self, governance_repo: Path) -> None:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = propose_adr(
                title="Test",
                context="Context.",
                decision="Decision.",
            )
            assert "error" in result.lower() or "not found" in result.lower()

    def test_error_on_gh_failure(self, governance_repo: Path) -> None:
        import subprocess

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "gh", stderr="auth required"
            )
            result = propose_adr(
                title="Test",
                context="Context.",
                decision="Decision.",
            )
            assert "error" in result.lower()

    def test_includes_governance_label(self, governance_repo: Path) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(
                stdout="https://github.com/aces-framework/aces/issues/1\n"
            )
            propose_adr(
                title="Test",
                context="Context.",
                decision="Decision.",
            )

            cmd = mock_run.call_args[0][0]
            assert "governance" in " ".join(cmd)


class TestCheckStandardsUpdateNeeded:
    """Tests for check_standards_update_needed tool."""

    def test_already_covered(self, governance_repo: Path) -> None:
        result = check_standards_update_needed(
            "Dependencies should not be hand-edited in manifest files."
        )
        # This is already in STANDARDS.md §13.
        assert "covered" in result.lower() or "already" in result.lower()

    def test_not_covered_suggests_promotion(self, governance_repo: Path) -> None:
        result = check_standards_update_needed(
            "All MCP servers should include a health check endpoint."
        )
        # Not in standards — should suggest adding it.
        assert (
            "not covered" in result.lower()
            or "promote" in result.lower()
            or "consider" in result.lower()
        )

    def test_returns_relevant_sections(self, governance_repo: Path) -> None:
        result = check_standards_update_needed(
            "Tests should always be written before code."
        )
        # Should reference testing standards.
        assert "9" in result or "test" in result.lower()


def _make_completed_process(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> Any:
    """Create a mock CompletedProcess."""
    import subprocess

    return subprocess.CompletedProcess(
        args=["gh"], returncode=returncode, stdout=stdout, stderr=stderr
    )
