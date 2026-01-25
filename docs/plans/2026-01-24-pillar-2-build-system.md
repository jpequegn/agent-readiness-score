# Pillar 2: Build System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Implement BuildPillar to evaluate build reproducibility and dependency management across Python, JavaScript/TypeScript, Go, and Rust.

**Architecture:** BuildPillar detects languages by package manager files, runs per-language checks (Levels 1-3) for package managers, lock files, and build scripts, then repository-wide checks (Levels 4-5) for caching, containerization, dependency automation, and reproducible builds. Uses semi-cumulative scoring.

**Tech Stack:** Python 3.9+, pytest, pathlib, JSON parsing for package.json, TOML parsing for pyproject.toml/Cargo.toml

---

## Task 1: Create BuildPillar Skeleton

**Files:**
- Create: `src/agent_readiness/pillars/build.py`
- Test: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Create `tests/pillars/test_build.py`:

```python
"""Tests for Build System pillar."""

from pathlib import Path

import pytest

from agent_readiness.pillars.build import BuildPillar


def test_build_pillar_name() -> None:
    """Test BuildPillar has correct name."""
    pillar = BuildPillar()
    assert pillar.name == "Build System"


def test_build_pillar_weight() -> None:
    """Test BuildPillar has default weight."""
    pillar = BuildPillar()
    assert pillar.weight == 1.0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agent_readiness.pillars.build'"

**Step 3: Write minimal implementation**

Create `src/agent_readiness/pillars/build.py`:

```python
"""Build System pillar implementation."""

from pathlib import Path

from agent_readiness.models import CheckResult
from agent_readiness.pillar import Pillar


class BuildPillar(Pillar):
    """Evaluates build reproducibility and dependency management."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Build System"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for build system checks."""
        return []
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (2/2 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): add BuildPillar skeleton"
```

---

## Task 2: Implement Language Detection

**Files:**
- Modify: `src/agent_readiness/pillars/build.py`
- Modify: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_detect_languages_python_pyproject -v`
Expected: FAIL with "AttributeError: 'BuildPillar' object has no attribute '_detect_languages'"

**Step 3: Write minimal implementation**

Add to `src/agent_readiness/pillars/build.py` (after the `evaluate` method):

```python
    def _detect_languages(self, target_dir: Path) -> set[str]:
        """Detect programming languages by package manager files.

        Args:
            target_dir: Directory to scan

        Returns:
            Set of detected language names
        """
        languages = set()

        # Python
        if (
            (target_dir / "pyproject.toml").exists()
            or (target_dir / "setup.py").exists()
            or (target_dir / "requirements.txt").exists()
        ):
            languages.add("python")

        # JavaScript/TypeScript
        if (target_dir / "package.json").exists():
            languages.add("javascript")

        # Rust
        if (target_dir / "Cargo.toml").exists():
            languages.add("rust")

        # Go
        if (target_dir / "go.mod").exists():
            languages.add("go")

        return languages
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (9/9 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): implement language detection by package manager files"
```

---

## Task 3: Implement Level 1 - Package Manager Check

**Files:**
- Modify: `src/agent_readiness/pillars/build.py`
- Modify: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_check_package_manager_python_pyproject -v`
Expected: FAIL with "AttributeError: 'BuildPillar' object has no attribute '_check_package_manager_exists'"

**Step 3: Write minimal implementation**

Add to `src/agent_readiness/pillars/build.py`:

```python
from agent_readiness.models import CheckResult, Severity


class BuildPillar(Pillar):
    # ... existing methods ...

    def _check_package_manager_exists(
        self, target_dir: Path, languages: set[str]
    ) -> list[CheckResult]:
        """Check if each language has a package manager file.

        Args:
            target_dir: Directory to scan
            languages: Set of detected languages

        Returns:
            List of CheckResults, one per language
        """
        results = []

        package_files = {
            "python": ["pyproject.toml", "setup.py", "requirements.txt"],
            "javascript": ["package.json"],
            "rust": ["Cargo.toml"],
            "go": ["go.mod"],
        }

        for lang in sorted(languages):
            files = package_files.get(lang, [])
            found_files = [f for f in files if (target_dir / f).exists()]

            if found_files:
                results.append(
                    CheckResult(
                        name=f"{lang.capitalize()} package manager",
                        passed=True,
                        message=f"Found {', '.join(found_files)}",
                        severity=Severity.REQUIRED,
                        level=1,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        name=f"{lang.capitalize()} package manager",
                        passed=False,
                        message=f"No package manager file found (expected: {', '.join(files)})",
                        severity=Severity.REQUIRED,
                        level=1,
                    )
                )

        return results
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (13/13 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): implement Level 1 package manager check"
```

---

## Task 4: Implement Level 2 - Lock File Check

**Files:**
- Modify: `src/agent_readiness/pillars/build.py`
- Modify: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_check_lock_file_python -v`
Expected: FAIL with "AttributeError: 'BuildPillar' object has no attribute '_check_lock_file_exists'"

**Step 3: Write minimal implementation**

Add to `src/agent_readiness/pillars/build.py`:

```python
    def _check_lock_file_exists(
        self, target_dir: Path, languages: set[str]
    ) -> list[CheckResult]:
        """Check if each language has a lock file for reproducibility.

        Args:
            target_dir: Directory to scan
            languages: Set of detected languages

        Returns:
            List of CheckResults, one per language
        """
        results = []

        lock_files = {
            "python": ["poetry.lock", "Pipfile.lock", "requirements.lock"],
            "javascript": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
            "rust": ["Cargo.lock"],
            "go": ["go.sum"],
        }

        for lang in sorted(languages):
            files = lock_files.get(lang, [])
            found_files = [f for f in files if (target_dir / f).exists()]

            if found_files:
                results.append(
                    CheckResult(
                        name=f"{lang.capitalize()} lock file",
                        passed=True,
                        message=f"Found {', '.join(found_files)}",
                        severity=Severity.RECOMMENDED,
                        level=2,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        name=f"{lang.capitalize()} lock file",
                        passed=False,
                        message=f"No lock file found (expected: {', '.join(files)})",
                        severity=Severity.RECOMMENDED,
                        level=2,
                    )
                )

        return results
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (18/18 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): implement Level 2 lock file check"
```

---

## Task 5: Implement Level 3 - Build Script Check

**Files:**
- Modify: `src/agent_readiness/pillars/build.py`
- Modify: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
import json


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_check_build_script_python_makefile -v`
Expected: FAIL with "AttributeError: 'BuildPillar' object has no attribute '_check_build_script_exists'"

**Step 3: Write minimal implementation**

Add to `src/agent_readiness/pillars/build.py`:

```python
import json


class BuildPillar(Pillar):
    # ... existing methods ...

    def _check_build_script_exists(
        self, target_dir: Path, languages: set[str]
    ) -> list[CheckResult]:
        """Check if each language has a build script documented.

        Args:
            target_dir: Directory to scan
            languages: Set of detected languages

        Returns:
            List of CheckResults, one per language
        """
        results = []

        for lang in sorted(languages):
            if lang == "python":
                # Check for Makefile with build target or pyproject.toml with scripts
                has_makefile = (target_dir / "Makefile").exists()
                has_pyproject_scripts = False

                if (target_dir / "pyproject.toml").exists():
                    try:
                        import tomllib
                    except ImportError:
                        import tomli as tomllib

                    content = (target_dir / "pyproject.toml").read_text(
                        encoding="utf-8", errors="ignore"
                    )
                    try:
                        data = tomllib.loads(content)
                        has_pyproject_scripts = "scripts" in data.get("tool", {}).get("poetry", {})
                    except Exception:
                        pass

                if has_makefile or has_pyproject_scripts:
                    results.append(
                        CheckResult(
                            name="Python build script",
                            passed=True,
                            message="Found build configuration",
                            severity=Severity.RECOMMENDED,
                            level=3,
                        )
                    )
                else:
                    results.append(
                        CheckResult(
                            name="Python build script",
                            passed=False,
                            message="No build script found (expected Makefile or [tool.poetry.scripts])",
                            severity=Severity.RECOMMENDED,
                            level=3,
                        )
                    )

            elif lang == "javascript":
                # Check for build script in package.json
                has_build_script = False
                if (target_dir / "package.json").exists():
                    try:
                        content = (target_dir / "package.json").read_text(
                            encoding="utf-8", errors="ignore"
                        )
                        data = json.loads(content)
                        has_build_script = "build" in data.get("scripts", {})
                    except Exception:
                        pass

                if has_build_script:
                    results.append(
                        CheckResult(
                            name="JavaScript build script",
                            passed=True,
                            message="Found build script in package.json",
                            severity=Severity.RECOMMENDED,
                            level=3,
                        )
                    )
                else:
                    results.append(
                        CheckResult(
                            name="JavaScript build script",
                            passed=False,
                            message='No build script found (expected "build" in package.json scripts)',
                            severity=Severity.RECOMMENDED,
                            level=3,
                        )
                    )

            elif lang == "rust":
                # Rust always passes - cargo build is default
                results.append(
                    CheckResult(
                        name="Rust build script",
                        passed=True,
                        message="Default cargo build available",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
                )

            elif lang == "go":
                # Go always passes - go build is default
                results.append(
                    CheckResult(
                        name="Go build script",
                        passed=True,
                        message="Default go build available",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
                )

        return results
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (23/23 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): implement Level 3 build script check"
```

---

## Task 6: Implement Level 4 - Build Caching and Containerization

**Files:**
- Modify: `src/agent_readiness/pillars/build.py`
- Modify: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_check_build_caching_github_actions -v`
Expected: FAIL with "AttributeError: 'BuildPillar' object has no attribute '_check_build_caching'"

**Step 3: Write minimal implementation**

Add to `src/agent_readiness/pillars/build.py`:

```python
    def _check_build_caching(self, target_dir: Path) -> CheckResult:
        """Check if build caching is configured (repository-wide).

        Args:
            target_dir: Directory to scan

        Returns:
            Single CheckResult for the repository
        """
        found = []

        # Check GitHub Actions
        gh_workflows = target_dir / ".github" / "workflows"
        if gh_workflows.exists():
            for workflow_file in gh_workflows.glob("*.yml"):
                try:
                    content = workflow_file.read_text(encoding="utf-8", errors="ignore")
                    if "actions/cache" in content or "cache:" in content:
                        found.append(f"GitHub Actions ({workflow_file.name})")
                        break
                except Exception:
                    pass

        # Check GitLab CI
        gitlab_ci = target_dir / ".gitlab-ci.yml"
        if gitlab_ci.exists():
            try:
                content = gitlab_ci.read_text(encoding="utf-8", errors="ignore")
                if "cache:" in content:
                    found.append("GitLab CI")
            except Exception:
                pass

        # Check CircleCI
        circleci_config = target_dir / ".circleci" / "config.yml"
        if circleci_config.exists():
            try:
                content = circleci_config.read_text(encoding="utf-8", errors="ignore")
                if "save_cache" in content or "restore_cache" in content:
                    found.append("CircleCI")
            except Exception:
                pass

        if found:
            return CheckResult(
                name="Build caching",
                passed=True,
                message=f"Build caching configured in {', '.join(found)}",
                severity=Severity.OPTIONAL,
                level=4,
            )
        else:
            return CheckResult(
                name="Build caching",
                passed=False,
                message="No build caching detected in CI configuration",
                severity=Severity.OPTIONAL,
                level=4,
            )

    def _check_containerization(self, target_dir: Path) -> CheckResult:
        """Check if containerization is configured (repository-wide).

        Args:
            target_dir: Directory to scan

        Returns:
            Single CheckResult for the repository
        """
        found = []

        if (target_dir / "Dockerfile").exists():
            found.append("Dockerfile")

        if (target_dir / "Containerfile").exists():
            found.append("Containerfile")

        if (target_dir / ".devcontainer" / "devcontainer.json").exists():
            found.append("devcontainer")

        if (target_dir / "docker-compose.yml").exists():
            found.append("docker-compose.yml")

        if found:
            return CheckResult(
                name="Containerization",
                passed=True,
                message=f"Found {', '.join(found)}",
                severity=Severity.OPTIONAL,
                level=4,
            )
        else:
            return CheckResult(
                name="Containerization",
                passed=False,
                message="No containerization configuration found",
                severity=Severity.OPTIONAL,
                level=4,
            )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (28/28 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): implement Level 4 caching and containerization checks"
```

---

## Task 7: Implement Level 5 - Dependency Automation and Reproducible Builds

**Files:**
- Modify: `src/agent_readiness/pillars/build.py`
- Modify: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
def test_check_dependency_automation_dependabot(tmp_path: Path) -> None:
    """Test detecting Dependabot configuration."""
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "dependabot.yml").touch()

    pillar = BuildPillar()
    result = pillar._check_dependency_automation(tmp_path)

    assert result.passed
    assert "dependabot" in result.message.lower()


def test_check_dependency_automation_renovate(tmp_path: Path) -> None:
    """Test detecting Renovate configuration."""
    (tmp_path / "renovate.json").touch()

    pillar = BuildPillar()
    result = pillar._check_dependency_automation(tmp_path)

    assert result.passed
    assert "renovate" in result.message.lower()


def test_check_dependency_automation_not_found(tmp_path: Path) -> None:
    """Test dependency automation check fails when not configured."""
    pillar = BuildPillar()
    result = pillar._check_dependency_automation(tmp_path)

    assert not result.passed


def test_check_reproducible_builds_with_lock_files(tmp_path: Path) -> None:
    """Test reproducible builds check passes with lock files."""
    (tmp_path / "poetry.lock").touch()
    readme = tmp_path / "README.md"
    readme.write_text("We use lock files for reproducible builds.")

    pillar = BuildPillar()
    # Need to pass languages that have lock files
    result = pillar._check_reproducible_builds(tmp_path, {"python"})

    assert result.passed


def test_check_reproducible_builds_missing_lock_files(tmp_path: Path) -> None:
    """Test reproducible builds check fails without lock files."""
    pillar = BuildPillar()
    result = pillar._check_reproducible_builds(tmp_path, {"python"})

    assert not result.passed
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_check_dependency_automation_dependabot -v`
Expected: FAIL with "AttributeError: 'BuildPillar' object has no attribute '_check_dependency_automation'"

**Step 3: Write minimal implementation**

Add to `src/agent_readiness/pillars/build.py`:

```python
    def _check_dependency_automation(self, target_dir: Path) -> CheckResult:
        """Check if automatic dependency updates are configured (repository-wide).

        Args:
            target_dir: Directory to scan

        Returns:
            Single CheckResult for the repository
        """
        found = []

        if (target_dir / ".github" / "dependabot.yml").exists():
            found.append("Dependabot")

        if (target_dir / "renovate.json").exists() or (
            target_dir / ".renovaterc"
        ).exists():
            found.append("Renovate")

        if (target_dir / ".github" / "renovate.json").exists():
            found.append("Renovate")

        if found:
            return CheckResult(
                name="Dependency automation",
                passed=True,
                message=f"Found {', '.join(found)} configuration",
                severity=Severity.OPTIONAL,
                level=5,
            )
        else:
            return CheckResult(
                name="Dependency automation",
                passed=False,
                message="No dependency automation configured",
                severity=Severity.OPTIONAL,
                level=5,
            )

    def _check_reproducible_builds(
        self, target_dir: Path, languages: set[str]
    ) -> CheckResult:
        """Check if reproducible builds are configured (repository-wide).

        Args:
            target_dir: Directory to scan
            languages: Set of detected languages

        Returns:
            Single CheckResult for the repository
        """
        criteria = []

        # Check if all languages have lock files
        lock_files = {
            "python": ["poetry.lock", "Pipfile.lock", "requirements.lock"],
            "javascript": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
            "rust": ["Cargo.lock"],
            "go": ["go.sum"],
        }

        all_have_locks = True
        for lang in languages:
            files = lock_files.get(lang, [])
            if not any((target_dir / f).exists() for f in files):
                all_have_locks = False
                break

        if all_have_locks and languages:
            criteria.append("all languages have lock files")

        # Check for reproducibility mentions in documentation
        doc_files = ["README.md", "CONTRIBUTING.md", "BUILD.md"]
        reproducibility_keywords = ["reproducible", "hermetic", "deterministic"]

        for doc in doc_files:
            doc_path = target_dir / doc
            if doc_path.exists():
                try:
                    content = doc_path.read_text(encoding="utf-8", errors="ignore").lower()
                    if any(keyword in content for keyword in reproducibility_keywords):
                        criteria.append(f"reproducibility mentioned in {doc}")
                        break
                except Exception:
                    pass

        if criteria:
            return CheckResult(
                name="Reproducible builds",
                passed=True,
                message=f"Reproducible builds configured: {', '.join(criteria)}",
                severity=Severity.OPTIONAL,
                level=5,
            )
        else:
            return CheckResult(
                name="Reproducible builds",
                passed=False,
                message="No reproducible build configuration detected",
                severity=Severity.OPTIONAL,
                level=5,
            )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (33/33 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): implement Level 5 dependency automation and reproducible builds"
```

---

## Task 8: Wire Up evaluate() Method

**Files:**
- Modify: `src/agent_readiness/pillars/build.py`
- Modify: `tests/pillars/test_build.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
def test_evaluate_full_python_setup(tmp_path: Path) -> None:
    """Test evaluation of Python project with all features."""
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "poetry.lock").touch()
    makefile = tmp_path / "Makefile"
    makefile.write_text("build:\n\tpython -m build\n")

    pillar = BuildPillar()
    results = pillar.evaluate(tmp_path)

    # Should have: package manager, lock file, build script, caching (fail), containerization (fail),
    # dependency automation (fail), reproducible builds (partial)
    assert len(results) >= 3  # At least the per-language checks
    assert any(r.passed and "package manager" in r.name.lower() for r in results)
    assert any(r.passed and "lock file" in r.name.lower() for r in results)
    assert any(r.passed and "build script" in r.name.lower() for r in results)


def test_evaluate_minimal_setup(tmp_path: Path) -> None:
    """Test evaluation of minimal project."""
    (tmp_path / "package.json").touch()

    pillar = BuildPillar()
    results = pillar.evaluate(tmp_path)

    # Should have checks for JavaScript
    assert len(results) >= 1
    assert any("javascript" in r.name.lower() for r in results)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_evaluate_full_python_setup -v`
Expected: FAIL with assertion error (evaluate returns empty list)

**Step 3: Write minimal implementation**

Update the `evaluate` method in `src/agent_readiness/pillars/build.py`:

```python
    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for build system checks."""
        results = []

        # Detect languages first
        languages = self._detect_languages(target_dir)

        # Level 1: Package manager exists (per-language)
        results.extend(self._check_package_manager_exists(target_dir, languages))

        # Level 2: Lock file exists (per-language)
        results.extend(self._check_lock_file_exists(target_dir, languages))

        # Level 3: Build script exists (per-language)
        results.extend(self._check_build_script_exists(target_dir, languages))

        # Level 4: Build caching (repository-wide)
        results.append(self._check_build_caching(target_dir))

        # Level 4: Containerization (repository-wide)
        results.append(self._check_containerization(target_dir))

        # Level 5: Dependency automation (repository-wide)
        results.append(self._check_dependency_automation(target_dir))

        # Level 5: Reproducible builds (repository-wide)
        results.append(self._check_reproducible_builds(target_dir, languages))

        return results
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py -v`
Expected: PASS (35/35 tests)

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/build.py tests/pillars/test_build.py
git commit -m "feat(build): wire up evaluate() method with all checks"
```

---

## Task 9: Update pillars/__init__.py

**Files:**
- Modify: `src/agent_readiness/pillars/__init__.py`

**Step 1: Write the failing test**

Add to `tests/pillars/test_build.py`:

```python
def test_build_pillar_importable() -> None:
    """Test BuildPillar can be imported from pillars package."""
    from agent_readiness.pillars import BuildPillar

    pillar = BuildPillar()
    assert pillar.name == "Build System"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_build.py::test_build_pillar_importable -v`
Expected: FAIL with "ImportError: cannot import name 'BuildPillar'"

**Step 3: Write minimal implementation**

Update `src/agent_readiness/pillars/__init__.py`:

```python
"""Pillar implementations for agent readiness evaluation."""

from .build import BuildPillar
from .style import StylePillar

__all__ = ["BuildPillar", "StylePillar"]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pillars/test_build.py::test_build_pillar_importable -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/__init__.py tests/pillars/test_build.py
git commit -m "feat(build): export BuildPillar from pillars package"
```

---

## Task 10: Add Integration Test

**Files:**
- Modify: `tests/test_integration.py`

**Step 1: Write the failing test**

Add to `tests/test_integration.py`:

```python
from agent_readiness.pillars import BuildPillar


def test_scanner_with_build_pillar(tmp_path: Path) -> None:
    """Test Scanner integration with BuildPillar."""
    # Setup: Python project with some features
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "poetry.lock").touch()

    scanner = Scanner()
    scanner.register_pillar(BuildPillar())
    result = scanner.scan(tmp_path)

    assert result.target_directory == str(tmp_path.resolve())
    assert len(result.pillars) == 1
    assert result.pillars[0].name == "Build System"
    assert result.pillars[0].score > 0  # Should have some passing checks


def test_scanner_with_multiple_pillars(tmp_path: Path) -> None:
    """Test Scanner with both StylePillar and BuildPillar."""
    # Setup: Python project with style and build config
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\nline-length = 100\n")
    (tmp_path / "poetry.lock").touch()
    (tmp_path / "main.py").touch()

    scanner = Scanner()
    scanner.register_pillars([StylePillar(), BuildPillar()])
    result = scanner.scan(tmp_path)

    assert len(result.pillars) == 2
    assert {p.name for p in result.pillars} == {"Style & Validation", "Build System"}
    assert result.overall_score > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_integration.py::test_scanner_with_build_pillar -v`
Expected: FAIL (test doesn't exist yet or imports missing)

**Step 3: Run test to verify it passes**

Run: `pytest tests/test_integration.py -v`
Expected: PASS (all integration tests)

**Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test(build): add integration tests for BuildPillar"
```

---

## Task 11: Run Full Test Suite and Check Coverage

**Files:**
- None (verification only)

**Step 1: Run full test suite**

Run: `pytest -v --cov=agent_readiness --cov-report=term-missing`
Expected: All tests pass with >90% coverage on build.py

**Step 2: Verify all tests pass**

Check output for:
- All tests in `tests/pillars/test_build.py` passing
- All integration tests passing
- Coverage for `src/agent_readiness/pillars/build.py` >90%

**Step 3: Fix any issues found**

If tests fail or coverage is low, fix issues and re-run.

**Step 4: Document results**

Note final test count and coverage percentage for commit message.

---

## Task 12: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`

**Step 1: Update README.md**

Mark Pillar 2 as complete in the roadmap:

```markdown
- [x] Pillar 2: Build System
```

**Step 2: Update AGENTS.md**

Add BuildPillar documentation:

```markdown
### Pillar 2: Build System (`pillars/build.py`)

Checks for:
- **Level 1**: Package manager files (pyproject.toml, package.json, Cargo.toml, go.mod)
- **Level 2**: Lock files for reproducibility (poetry.lock, package-lock.json, etc.)
- **Level 3**: Build scripts documented (Makefile, package.json scripts, cargo/go defaults)
- **Level 4**: Build caching in CI, containerization (Dockerfile, devcontainer)
- **Level 5**: Dependency automation (Dependabot/Renovate), reproducible builds

**Language Support**: Python, JavaScript/TypeScript, Go, Rust
**Check Granularity**: Per-language (Levels 1-3), Repository-wide (Levels 4-5)
```

**Step 3: Commit**

```bash
git add README.md AGENTS.md
git commit -m "docs: update README and AGENTS.md for Pillar 2"
```

---

## Task 13: Push and Create Pull Request

**Files:**
- None (git operations only)

**Step 1: Push branch to remote**

Run: `git push -u origin pillar-2-build-system`
Expected: Branch pushed successfully

**Step 2: Create pull request**

Run:
```bash
gh pr create --title "feat: Implement Pillar 2 - Build System" --body "Implements Issue #3

## Summary
- Implements BuildPillar with language detection by package manager files
- Per-language checks (Levels 1-3): package managers, lock files, build scripts
- Repository-wide checks (Levels 4-5): caching, containerization, dependency automation, reproducible builds
- Supports Python, JavaScript/TypeScript, Go, Rust
- 36 tests, >90% coverage

## Testing
- All tests passing (36/36)
- Coverage: XX% on build.py
- Integration tests with Scanner

Closes #3"
```

Expected: PR created successfully

**Step 3: Verify PR**

Check that PR is created and linked to issue #3.

---

## Success Criteria

- [ ] All 36+ tests passing
- [ ] >90% coverage on build.py
- [ ] BuildPillar works with Scanner
- [ ] Supports Python, JavaScript/TypeScript, Go, Rust
- [ ] Documentation updated
- [ ] PR created and linked to issue #3
