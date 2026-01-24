"""Tests for Style & Validation pillar."""

from pathlib import Path
from agent_readiness.pillars.style import StylePillar


def test_detect_languages_python_only(tmp_path: Path) -> None:
    """Test detecting Python files."""
    (tmp_path / "main.py").touch()
    (tmp_path / "utils.py").touch()

    pillar = StylePillar()
    languages = pillar._detect_languages(tmp_path)

    assert "python" in languages
    assert len(languages) == 1


def test_detect_languages_javascript_only(tmp_path: Path) -> None:
    """Test detecting JavaScript files."""
    (tmp_path / "app.js").touch()
    (tmp_path / "utils.ts").touch()

    pillar = StylePillar()
    languages = pillar._detect_languages(tmp_path)

    assert "javascript" in languages
    assert len(languages) == 1


def test_detect_languages_multiple(tmp_path: Path) -> None:
    """Test detecting multiple languages."""
    (tmp_path / "main.py").touch()
    (tmp_path / "app.js").touch()
    (tmp_path / "main.go").touch()

    pillar = StylePillar()
    languages = pillar._detect_languages(tmp_path)

    assert "python" in languages
    assert "javascript" in languages
    assert "go" in languages
    assert len(languages) == 3
