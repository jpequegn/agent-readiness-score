"""Tests for Testing pillar."""

from pathlib import Path

from agent_readiness.pillars.testing import TestingPillar


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
