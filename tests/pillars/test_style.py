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


def test_check_any_linter_config_python_ruff(tmp_path: Path) -> None:
    """Test detecting ruff.toml for Python."""
    (tmp_path / "main.py").touch()
    (tmp_path / "ruff.toml").touch()

    pillar = StylePillar()
    result = pillar._check_any_linter_config(tmp_path, {"python"})

    assert result.passed
    assert "ruff.toml" in result.message


def test_check_any_linter_config_python_pyproject(tmp_path: Path) -> None:
    """Test detecting pyproject.toml with ruff config."""
    (tmp_path / "main.py").touch()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.ruff]\nline-length = 100\n")

    pillar = StylePillar()
    result = pillar._check_any_linter_config(tmp_path, {"python"})

    assert result.passed
    assert "pyproject.toml" in result.message


def test_check_any_linter_config_javascript_eslint(tmp_path: Path) -> None:
    """Test detecting .eslintrc for JavaScript."""
    (tmp_path / "app.js").touch()
    (tmp_path / ".eslintrc.json").touch()

    pillar = StylePillar()
    result = pillar._check_any_linter_config(tmp_path, {"javascript"})

    assert result.passed
    assert ".eslintrc" in result.message


def test_check_any_linter_config_not_found(tmp_path: Path) -> None:
    """Test when no linter config is found."""
    (tmp_path / "main.py").touch()

    pillar = StylePillar()
    result = pillar._check_any_linter_config(tmp_path, {"python"})

    assert not result.passed
    assert "No linter" in result.message


def test_check_formatter_config_python_black(tmp_path: Path) -> None:
    """Test detecting black config in pyproject.toml."""
    (tmp_path / "main.py").touch()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.black]\nline-length = 100\n")

    pillar = StylePillar()
    result = pillar._check_formatter_config(tmp_path, {"python"})

    assert result.passed
    assert "pyproject.toml" in result.message


def test_check_formatter_config_javascript_prettier(tmp_path: Path) -> None:
    """Test detecting .prettierrc for JavaScript."""
    (tmp_path / "app.js").touch()
    (tmp_path / ".prettierrc").touch()

    pillar = StylePillar()
    result = pillar._check_formatter_config(tmp_path, {"javascript"})

    assert result.passed
    assert ".prettierrc" in result.message


def test_check_formatter_config_go_gofmt(tmp_path: Path) -> None:
    """Test Go (gofmt is built-in, always passes)."""
    (tmp_path / "main.go").touch()

    pillar = StylePillar()
    result = pillar._check_formatter_config(tmp_path, {"go"})

    assert result.passed
    assert "gofmt" in result.message.lower()


def test_check_formatter_config_not_found(tmp_path: Path) -> None:
    """Test when no formatter config is found."""
    (tmp_path / "main.py").touch()

    pillar = StylePillar()
    result = pillar._check_formatter_config(tmp_path, {"python"})

    assert not result.passed
    assert "No formatter" in result.message
