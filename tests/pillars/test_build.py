"""Tests for Build System pillar."""

from pathlib import Path

from agent_readiness.pillars.build import BuildPillar


def test_build_pillar_name() -> None:
    """Test BuildPillar has correct name."""
    pillar = BuildPillar()
    assert pillar.name == "Build System"


def test_build_pillar_weight() -> None:
    """Test BuildPillar has default weight."""
    pillar = BuildPillar()
    assert pillar.weight == 1.0


def test_detect_languages_python_pyproject(tmp_path: Path) -> None:
    """Test detecting Python via pyproject.toml."""
    (tmp_path / "pyproject.toml").touch()

    pillar = BuildPillar()
    languages = pillar._detect_languages(tmp_path)

    assert "python" in languages


def test_detect_languages_python_setup(tmp_path: Path) -> None:
    """Test detecting Python via setup.py."""
    (tmp_path / "setup.py").touch()

    pillar = BuildPillar()
    languages = pillar._detect_languages(tmp_path)

    assert "python" in languages


def test_detect_languages_javascript(tmp_path: Path) -> None:
    """Test detecting JavaScript via package.json."""
    (tmp_path / "package.json").touch()

    pillar = BuildPillar()
    languages = pillar._detect_languages(tmp_path)

    assert "javascript" in languages


def test_detect_languages_rust(tmp_path: Path) -> None:
    """Test detecting Rust via Cargo.toml."""
    (tmp_path / "Cargo.toml").touch()

    pillar = BuildPillar()
    languages = pillar._detect_languages(tmp_path)

    assert "rust" in languages


def test_detect_languages_go(tmp_path: Path) -> None:
    """Test detecting Go via go.mod."""
    (tmp_path / "go.mod").touch()

    pillar = BuildPillar()
    languages = pillar._detect_languages(tmp_path)

    assert "go" in languages


def test_detect_languages_multiple(tmp_path: Path) -> None:
    """Test detecting multiple languages."""
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "package.json").touch()

    pillar = BuildPillar()
    languages = pillar._detect_languages(tmp_path)

    assert languages == {"python", "javascript"}


def test_detect_languages_none(tmp_path: Path) -> None:
    """Test detecting no languages."""
    pillar = BuildPillar()
    languages = pillar._detect_languages(tmp_path)

    assert languages == set()
