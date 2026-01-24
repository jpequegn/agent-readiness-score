"""Tests for Build System pillar."""

import json
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


def test_check_package_manager_python_pyproject(tmp_path: Path) -> None:
    """Test detecting Python package manager via pyproject.toml."""
    (tmp_path / "pyproject.toml").touch()

    pillar = BuildPillar()
    results = pillar._check_package_manager_exists(tmp_path, {"python"})

    assert len(results) == 1
    assert results[0].passed
    assert "python" in results[0].message.lower()
    assert "pyproject.toml" in results[0].message


def test_check_package_manager_javascript(tmp_path: Path) -> None:
    """Test detecting JavaScript package manager via package.json."""
    (tmp_path / "package.json").touch()

    pillar = BuildPillar()
    results = pillar._check_package_manager_exists(tmp_path, {"javascript"})

    assert len(results) == 1
    assert results[0].passed
    assert "javascript" in results[0].message.lower()


def test_check_package_manager_multiple_languages(tmp_path: Path) -> None:
    """Test detecting package managers for multiple languages."""
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "package.json").touch()

    pillar = BuildPillar()
    results = pillar._check_package_manager_exists(tmp_path, {"python", "javascript"})

    assert len(results) == 2
    assert all(r.passed for r in results)


def test_check_package_manager_missing(tmp_path: Path) -> None:
    """Test package manager check fails when files missing."""
    pillar = BuildPillar()
    results = pillar._check_package_manager_exists(tmp_path, {"python"})

    assert len(results) == 1
    assert not results[0].passed


def test_check_lock_file_python(tmp_path: Path) -> None:
    """Test detecting Python lock file."""
    (tmp_path / "poetry.lock").touch()

    pillar = BuildPillar()
    results = pillar._check_lock_file_exists(tmp_path, {"python"})

    assert len(results) == 1
    assert results[0].passed
    assert "python" in results[0].message.lower()
    assert "poetry.lock" in results[0].message


def test_check_lock_file_javascript(tmp_path: Path) -> None:
    """Test detecting JavaScript lock file."""
    (tmp_path / "package-lock.json").touch()

    pillar = BuildPillar()
    results = pillar._check_lock_file_exists(tmp_path, {"javascript"})

    assert len(results) == 1
    assert results[0].passed


def test_check_lock_file_rust(tmp_path: Path) -> None:
    """Test detecting Rust lock file."""
    (tmp_path / "Cargo.lock").touch()

    pillar = BuildPillar()
    results = pillar._check_lock_file_exists(tmp_path, {"rust"})

    assert len(results) == 1
    assert results[0].passed


def test_check_lock_file_go(tmp_path: Path) -> None:
    """Test detecting Go lock file."""
    (tmp_path / "go.sum").touch()

    pillar = BuildPillar()
    results = pillar._check_lock_file_exists(tmp_path, {"go"})

    assert len(results) == 1
    assert results[0].passed


def test_check_lock_file_missing(tmp_path: Path) -> None:
    """Test lock file check fails when missing."""
    pillar = BuildPillar()
    results = pillar._check_lock_file_exists(tmp_path, {"python"})

    assert len(results) == 1
    assert not results[0].passed


def test_check_build_script_python_makefile(tmp_path: Path) -> None:
    """Test detecting Python build via Makefile."""
    makefile = tmp_path / "Makefile"
    makefile.write_text("build:\n\tpython -m build\n")

    pillar = BuildPillar()
    results = pillar._check_build_script_exists(tmp_path, {"python"})

    assert len(results) == 1
    assert results[0].passed


def test_check_build_script_javascript(tmp_path: Path) -> None:
    """Test detecting JavaScript build script in package.json."""
    package_json = tmp_path / "package.json"
    package_json.write_text(json.dumps({"scripts": {"build": "tsc"}}))

    pillar = BuildPillar()
    results = pillar._check_build_script_exists(tmp_path, {"javascript"})

    assert len(results) == 1
    assert results[0].passed


def test_check_build_script_rust_default(tmp_path: Path) -> None:
    """Test Rust always passes (cargo build is default)."""
    pillar = BuildPillar()
    results = pillar._check_build_script_exists(tmp_path, {"rust"})

    assert len(results) == 1
    assert results[0].passed
    assert "cargo build" in results[0].message


def test_check_build_script_go_default(tmp_path: Path) -> None:
    """Test Go always passes (go build is default)."""
    pillar = BuildPillar()
    results = pillar._check_build_script_exists(tmp_path, {"go"})

    assert len(results) == 1
    assert results[0].passed
    assert "go build" in results[0].message


def test_check_build_script_missing(tmp_path: Path) -> None:
    """Test build script check fails when missing."""
    pillar = BuildPillar()
    results = pillar._check_build_script_exists(tmp_path, {"python"})

    assert len(results) == 1
    assert not results[0].passed


def test_check_build_caching_github_actions(tmp_path: Path) -> None:
    """Test detecting build caching in GitHub Actions."""
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.write_text("- uses: actions/cache@v3\n")

    pillar = BuildPillar()
    result = pillar._check_build_caching(tmp_path)

    assert result.passed
    assert "cache" in result.message.lower()


def test_check_build_caching_not_found(tmp_path: Path) -> None:
    """Test build caching check fails when not configured."""
    pillar = BuildPillar()
    result = pillar._check_build_caching(tmp_path)

    assert not result.passed


def test_check_containerization_dockerfile(tmp_path: Path) -> None:
    """Test detecting Dockerfile."""
    (tmp_path / "Dockerfile").touch()

    pillar = BuildPillar()
    result = pillar._check_containerization(tmp_path)

    assert result.passed
    assert "Dockerfile" in result.message


def test_check_containerization_devcontainer(tmp_path: Path) -> None:
    """Test detecting devcontainer."""
    (tmp_path / ".devcontainer").mkdir()
    (tmp_path / ".devcontainer" / "devcontainer.json").touch()

    pillar = BuildPillar()
    result = pillar._check_containerization(tmp_path)

    assert result.passed


def test_check_containerization_not_found(tmp_path: Path) -> None:
    """Test containerization check fails when not configured."""
    pillar = BuildPillar()
    result = pillar._check_containerization(tmp_path)

    assert not result.passed
