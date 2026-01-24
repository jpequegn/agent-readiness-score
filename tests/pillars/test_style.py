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


def test_check_precommit_hooks_found(tmp_path: Path) -> None:
    """Test detecting .pre-commit-config.yaml."""
    (tmp_path / ".pre-commit-config.yaml").write_text("repos:\n  - repo: https://github.com/psf/black\n")

    pillar = StylePillar()
    result = pillar._check_precommit_hooks(tmp_path)

    assert result.passed
    assert ".pre-commit-config.yaml" in result.message


def test_check_precommit_hooks_not_found(tmp_path: Path) -> None:
    """Test when no pre-commit config is found."""
    pillar = StylePillar()
    result = pillar._check_precommit_hooks(tmp_path)

    assert not result.passed
    assert "No pre-commit" in result.message


def test_check_ci_integration_github_actions(tmp_path: Path) -> None:
    """Test detecting GitHub Actions workflow."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "lint.yml").write_text("name: Lint\non: push\njobs:\n  lint:\n    runs-on: ubuntu-latest\n")

    pillar = StylePillar()
    result = pillar._check_ci_integration(tmp_path)

    assert result.passed
    assert "GitHub Actions" in result.message


def test_check_ci_integration_gitlab_ci(tmp_path: Path) -> None:
    """Test detecting GitLab CI."""
    (tmp_path / ".gitlab-ci.yml").write_text("lint:\n  script:\n    - ruff check .\n")

    pillar = StylePillar()
    result = pillar._check_ci_integration(tmp_path)

    assert result.passed
    assert "GitLab CI" in result.message


def test_check_ci_integration_not_found(tmp_path: Path) -> None:
    """Test when no CI integration is found."""
    pillar = StylePillar()
    result = pillar._check_ci_integration(tmp_path)

    assert not result.passed
    assert "No CI" in result.message


def test_check_style_guide_docs_found(tmp_path: Path) -> None:
    """Test detecting style guide documentation."""
    (tmp_path / "STYLE_GUIDE.md").write_text("# Style Guide\n\nOur coding standards.\n")

    pillar = StylePillar()
    result = pillar._check_style_guide_docs(tmp_path)

    assert result.passed
    assert "STYLE_GUIDE.md" in result.message


def test_check_style_guide_docs_in_contributing(tmp_path: Path) -> None:
    """Test detecting style guide in CONTRIBUTING.md."""
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing\n\n## Code Style\n\nWe use black.\n")

    pillar = StylePillar()
    result = pillar._check_style_guide_docs(tmp_path)

    assert result.passed
    assert "CONTRIBUTING.md" in result.message


def test_check_style_guide_docs_not_found(tmp_path: Path) -> None:
    """Test when no style guide documentation is found."""
    pillar = StylePillar()
    result = pillar._check_style_guide_docs(tmp_path)

    assert not result.passed
    assert "No style guide" in result.message


def test_evaluate_full_python_setup(tmp_path: Path) -> None:
    """Test evaluate() with a complete Python project setup."""
    # Create Python files
    (tmp_path / "main.py").touch()

    # Create linter config
    (tmp_path / "ruff.toml").touch()

    # Create formatter config
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.black]\nline-length = 100\n")

    # Create pre-commit config
    (tmp_path / ".pre-commit-config.yaml").touch()

    # Create CI config
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "lint.yml").touch()

    # Create style guide
    (tmp_path / "STYLE_GUIDE.md").touch()

    pillar = StylePillar()
    results = pillar.evaluate(tmp_path)

    # Should have 5 checks (one for each level)
    assert len(results) == 5

    # All checks should pass
    assert all(result.passed for result in results)

    # Verify check names
    check_names = [result.name for result in results]
    assert "Has linter configuration" in check_names
    assert "Has formatter configuration" in check_names
    assert "Has pre-commit hooks" in check_names
    assert "Has CI integration" in check_names
    assert "Has style guide documentation" in check_names


def test_evaluate_minimal_setup(tmp_path: Path) -> None:
    """Test evaluate() with minimal setup (only Python files)."""
    (tmp_path / "main.py").touch()

    pillar = StylePillar()
    results = pillar.evaluate(tmp_path)

    # Should still have 5 checks
    assert len(results) == 5

    # Most checks should fail (except possibly go's built-in formatter)
    failed_checks = [result for result in results if not result.passed]
    assert len(failed_checks) >= 4
