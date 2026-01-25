"""Tests for Testing pillar."""

from pathlib import Path

from agent_readiness.pillars.testing import TestingPillar
from agent_readiness.models import Severity


def test_testing_pillar_name() -> None:
    """Test TestingPillar has correct name."""
    pillar = TestingPillar()
    assert pillar.name == "Testing"


def test_testing_pillar_weight() -> None:
    """Test TestingPillar has default weight."""
    pillar = TestingPillar()
    assert pillar.weight == 1.0


def test_detect_test_infrastructure_python(tmp_path: Path) -> None:
    """Test detecting Python test infrastructure."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_example.py").touch()
    (test_dir / "test_utils.py").touch()

    pillar = TestingPillar()
    test_info = pillar._detect_test_infrastructure(tmp_path)

    assert "python" in test_info["languages"]
    assert len(test_info["test_dirs"]) == 1
    assert len(test_info["test_files"]["python"]) == 2


def test_detect_test_infrastructure_javascript(tmp_path: Path) -> None:
    """Test detecting JavaScript test infrastructure."""
    test_dir = tmp_path / "__tests__"
    test_dir.mkdir()
    (test_dir / "example.test.js").touch()
    (test_dir / "utils.spec.ts").touch()

    pillar = TestingPillar()
    test_info = pillar._detect_test_infrastructure(tmp_path)

    assert "javascript" in test_info["languages"]
    assert len(test_info["test_files"]["javascript"]) == 2


def test_detect_test_infrastructure_multiple_languages(tmp_path: Path) -> None:
    """Test detecting multiple languages."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_api.py").touch()
    (tmp_path / "tests" / "api.test.js").touch()

    pillar = TestingPillar()
    test_info = pillar._detect_test_infrastructure(tmp_path)

    assert test_info["languages"] == {"python", "javascript"}


def test_detect_test_infrastructure_none(tmp_path: Path) -> None:
    """Test detecting no test infrastructure."""
    pillar = TestingPillar()
    test_info = pillar._detect_test_infrastructure(tmp_path)

    assert test_info["languages"] == set()
    assert test_info["test_dirs"] == []


def test_detect_test_infrastructure_no_duplicates(tmp_path: Path) -> None:
    """Test files matching multiple patterns are not duplicated."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    # File matches both test_*.py and *_test.py patterns
    (test_dir / "test_test.py").touch()

    pillar = TestingPillar()
    test_info = pillar._detect_test_infrastructure(tmp_path)

    # Should only appear once in the list
    assert len(test_info["test_files"]["python"]) == 1


def test_check_tests_exist_found(tmp_path: Path) -> None:
    """Test tests exist check passes when tests found."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").touch()

    pillar = TestingPillar()
    result = pillar._check_tests_exist(tmp_path)

    assert result.passed
    assert "1 test file" in result.message
    assert result.severity == Severity.REQUIRED
    assert result.level == 1


def test_check_tests_exist_not_found(tmp_path: Path) -> None:
    """Test tests exist check fails when no tests found."""
    pillar = TestingPillar()
    result = pillar._check_tests_exist(tmp_path)

    assert not result.passed
    assert "No test" in result.message


def test_check_test_directory_structure_organized(tmp_path: Path) -> None:
    """Test directory structure check passes when organized."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_1.py").touch()
    (test_dir / "test_2.py").touch()

    pillar = TestingPillar()
    result = pillar._check_test_directory_structure(tmp_path)

    assert result.passed
    assert result.level == 2


def test_check_test_directory_structure_scattered(tmp_path: Path) -> None:
    """Test directory structure check fails when scattered."""
    (tmp_path / "test_scattered.py").touch()  # Not in test directory

    pillar = TestingPillar()
    result = pillar._check_test_directory_structure(tmp_path)

    assert not result.passed


def test_check_test_command_documented_found(tmp_path: Path) -> None:
    """Test command documentation check passes when found."""
    readme = tmp_path / "README.md"
    readme.write_text("## Testing\n\nRun tests with:\n```bash\npytest\n```")

    pillar = TestingPillar()
    result = pillar._check_test_command_documented(tmp_path)

    assert result.passed
    assert "pytest" in result.message


def test_check_test_command_documented_not_found(tmp_path: Path) -> None:
    """Test command documentation check fails when not found."""
    readme = tmp_path / "README.md"
    readme.write_text("# Project\n\nSome content")

    pillar = TestingPillar()
    result = pillar._check_test_command_documented(tmp_path)

    assert not result.passed


def test_check_tests_in_ci_github_actions(tmp_path: Path) -> None:
    """Test CI check passes when tests run in GitHub Actions."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    ci_file = workflows_dir / "ci.yml"
    ci_file.write_text("""
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
""")

    pillar = TestingPillar()
    result = pillar._check_tests_in_ci(tmp_path)

    assert result.passed
    assert "GitHub Actions" in result.message
    assert result.level == 3


def test_check_tests_in_ci_not_found(tmp_path: Path) -> None:
    """Test CI check fails when no CI configuration found."""
    pillar = TestingPillar()
    result = pillar._check_tests_in_ci(tmp_path)

    assert not result.passed
    assert "No CI configuration" in result.message


def test_check_coverage_measured_python(tmp_path: Path) -> None:
    """Test coverage measured check for Python with pytest-cov."""
    # Create Python test infrastructure
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").touch()

    # Create pyproject.toml with pytest-cov
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[tool.pytest.ini_options]
addopts = "--cov=myapp --cov-report=xml"

[tool.coverage.run]
source = ["src"]
""")

    pillar = TestingPillar()
    results = pillar._check_coverage_measured(tmp_path)

    # Should return one CheckResult for Python
    assert len(results) == 1
    assert results[0].name == "Coverage measured (python)"
    assert results[0].passed
    assert "pytest-cov" in results[0].message.lower()
    assert results[0].severity == Severity.RECOMMENDED
    assert results[0].level == 3


def test_check_coverage_measured_not_configured(tmp_path: Path) -> None:
    """Test coverage measured check fails when not configured."""
    # Create Python test infrastructure without coverage config
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").touch()

    # Create pyproject.toml without coverage config
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[tool.pytest.ini_options]
testpaths = ["tests"]
""")

    pillar = TestingPillar()
    results = pillar._check_coverage_measured(tmp_path)

    # Should return one CheckResult for Python
    assert len(results) == 1
    assert results[0].name == "Coverage measured (python)"
    assert not results[0].passed
    assert "not configured" in results[0].message.lower()
