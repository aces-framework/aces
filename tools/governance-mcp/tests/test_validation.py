"""Tests for validation tools: check_repo_compliance, check_dependency_direction."""

from __future__ import annotations

from pathlib import Path

from aces_governance_mcp.server import (
    check_dependency_direction,
    check_repo_compliance,
)


class TestCheckRepoCompliance:
    """Tests for check_repo_compliance tool."""

    def test_compliant_rust_repo_all_pass(
        self, compliant_rust_repo: Path, governance_repo: Path
    ) -> None:
        result = check_repo_compliance(str(compliant_rust_repo), "rust")
        assert "FAIL" not in result

    def test_compliant_python_repo_all_pass(
        self, compliant_python_repo: Path, governance_repo: Path
    ) -> None:
        result = check_repo_compliance(str(compliant_python_repo), "python")
        assert "FAIL" not in result

    def test_missing_license(self, tmp_path: Path, governance_repo: Path) -> None:
        repo = tmp_path / "aces-barebones"
        repo.mkdir()
        result = check_repo_compliance(str(repo), "governance")
        assert "FAIL" in result
        assert "LICENSE" in result

    def test_missing_rust_specific_files(
        self, tmp_path: Path, governance_repo: Path
    ) -> None:
        repo = tmp_path / "aces-incomplete"
        repo.mkdir()
        (repo / "LICENSE").write_text("Apache License 2.0\n")
        result = check_repo_compliance(str(repo), "rust")
        assert "Cargo.toml" in result
        assert "FAIL" in result

    def test_missing_python_specific_files(
        self, tmp_path: Path, governance_repo: Path
    ) -> None:
        repo = tmp_path / "aces-incomplete"
        repo.mkdir()
        (repo / "LICENSE").write_text("Apache License 2.0\n")
        result = check_repo_compliance(str(repo), "python")
        assert "pyproject.toml" in result
        assert "FAIL" in result

    def test_naming_convention_warning(
        self, tmp_path: Path, governance_repo: Path
    ) -> None:
        repo = tmp_path / "bad-name"
        repo.mkdir()
        result = check_repo_compliance(str(repo), "governance")
        assert "WARN" in result
        assert "bad-name" in result

    def test_rust_missing_deny_missing_docs(
        self, compliant_rust_repo: Path, governance_repo: Path
    ) -> None:
        lib_rs = compliant_rust_repo / "src" / "lib.rs"
        lib_rs.write_text("// no deny missing docs\n")
        result = check_repo_compliance(str(compliant_rust_repo), "rust")
        assert "missing_docs" in result

    def test_rust_missing_apache_license(
        self, compliant_rust_repo: Path, governance_repo: Path
    ) -> None:
        cargo = compliant_rust_repo / "Cargo.toml"
        cargo.write_text('[package]\nname = "aces-test"\nversion = "0.1.0"\n')
        result = check_repo_compliance(str(compliant_rust_repo), "rust")
        assert "Apache-2.0" in result

    def test_python_missing_mypy_strict(
        self, compliant_python_repo: Path, governance_repo: Path
    ) -> None:
        pyproject = compliant_python_repo / "pyproject.toml"
        pyproject.write_text('[project]\nname = "aces_test"\nversion = "0.1.0"\n')
        result = check_repo_compliance(str(compliant_python_repo), "python")
        assert "mypy" in result.lower()

    def test_python_missing_apache_license(
        self, compliant_python_repo: Path, governance_repo: Path
    ) -> None:
        pyproject = compliant_python_repo / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "aces_test"\nversion = "0.1.0"\n\n'
            "[tool.mypy]\nstrict = true\n"
        )
        result = check_repo_compliance(str(compliant_python_repo), "python")
        assert "Apache-2.0" in result

    def test_template_drift_detected(
        self, compliant_rust_repo: Path, governance_repo: Path
    ) -> None:
        mdlint = compliant_rust_repo / ".markdownlint.yaml"
        mdlint.write_text("default: false\ncustomized: true\n")
        result = check_repo_compliance(str(compliant_rust_repo), "rust")
        assert "drift" in result.lower() or "differs" in result.lower()

    def test_invalid_repo_type(self, tmp_path: Path, governance_repo: Path) -> None:
        result = check_repo_compliance(str(tmp_path), "invalid")
        assert "invalid" in result.lower() or "Invalid" in result

    def test_nonexistent_directory(self, governance_repo: Path) -> None:
        result = check_repo_compliance("/nonexistent/path", "rust")
        assert "not found" in result.lower() or "Directory" in result

    def test_ci_workflow_content_rust(
        self, compliant_rust_repo: Path, governance_repo: Path
    ) -> None:
        ci = compliant_rust_repo / ".github" / "workflows" / "ci.yaml"
        ci.write_text("name: CI\njobs:\n  build:\n    steps:\n      - run: echo hi\n")
        result = check_repo_compliance(str(compliant_rust_repo), "rust")
        # Should flag missing expected CI steps or wrong job name.
        assert "FAIL" in result or "WARN" in result

    def test_ci_workflow_content_python(
        self, compliant_python_repo: Path, governance_repo: Path
    ) -> None:
        ci = compliant_python_repo / ".github" / "workflows" / "ci.yaml"
        ci.write_text("name: CI\njobs:\n  build:\n    steps:\n      - run: echo hi\n")
        result = check_repo_compliance(str(compliant_python_repo), "python")
        assert "FAIL" in result or "WARN" in result


class TestCheckDependencyDirection:
    """Tests for check_dependency_direction tool."""

    def test_valid_dependencies(self, governance_repo: Path) -> None:
        result = check_dependency_direction(
            "aces-runtime", ["aces-schema", "aces-sdl", "aces-provider-sdk"]
        )
        assert "violation" not in result.lower()

    def test_upward_tier_violation(self, governance_repo: Path) -> None:
        result = check_dependency_direction("aces-schema", ["aces-runtime"])
        assert "violation" in result.lower() or "VIOLATION" in result

    def test_same_tier_allowed(self, governance_repo: Path) -> None:
        result = check_dependency_direction("aces-experiment", ["aces-runtime"])
        assert "violation" not in result.lower()

    def test_ignores_non_aces_deps(self, governance_repo: Path) -> None:
        result = check_dependency_direction(
            "aces-runtime", ["tokio", "tonic", "aces-schema"]
        )
        assert "violation" not in result.lower()

    def test_unknown_repo_name(self, governance_repo: Path) -> None:
        result = check_dependency_direction("unknown-repo", ["aces-schema"])
        assert "unknown" in result.lower() or "Unknown" in result
