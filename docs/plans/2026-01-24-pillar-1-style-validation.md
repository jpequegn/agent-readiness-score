# Pillar 1: Style & Validation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the Style & Validation pillar to evaluate code style enforcement and validation tooling across multiple languages.

**Architecture:** Create a StylePillar class that detects languages in the repository, runs level-based checks (1-5), and uses semi-cumulative scoring. The pillar will check for linter/formatter configs, pre-commit hooks, CI integration, and agent-optimized features.

**Tech Stack:** Python 3.9+, pathlib for file detection, YAML parsing for CI configs, pytest for testing

---

## Task 1: Create Directory Structure

**Files:**
- Create: `src/agent_readiness/pillars/__init__.py`
- Create: `tests/pillars/__init__.py`

**Step 1: Create pillars package directory**

```bash
cd /Users/julienmika/Code/agent-readiness-score/.worktrees/pillar-1-style-validation
mkdir -p src/agent_readiness/pillars
mkdir -p tests/pillars
```

**Step 2: Create __init__.py files**

Create `src/agent_readiness/pillars/__init__.py`:
```python
"""Pillar implementations for agent readiness evaluation."""

from .style import StylePillar

__all__ = ["StylePillar"]
```

Create `tests/pillars/__init__.py`:
```python
"""Tests for pillar implementations."""
```

**Step 3: Verify structure**

Run: `ls -R src/agent_readiness/pillars tests/pillars`
Expected: Both directories exist with __init__.py files

**Step 4: Commit**

```bash
git add src/agent_readiness/pillars/__init__.py tests/pillars/__init__.py
git commit -m "chore: create pillars directory structure

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Language Detection Helper

**Files:**
- Create: `src/agent_readiness/pillars/style.py`
- Create: `tests/pillars/test_style.py`

**Step 1: Write failing test for language detection**

Create `tests/pillars/test_style.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pillars/test_style.py::test_detect_languages_python_only -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agent_readiness.pillars.style'"

**Step 3: Create StylePillar skeleton**

Create `src/agent_readiness/pillars/style.py`:
```python
"""Style & Validation pillar implementation."""

from pathlib import Path
from agent_readiness.models import CheckResult
from agent_readiness.pillar import Pillar


class StylePillar(Pillar):
    """Evaluates code style enforcement and validation tooling."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Style & Validation"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for style and validation checks."""
        return []

    def _detect_languages(self, target_dir: Path) -> set[str]:
        """Detect programming languages in the repository.

        Args:
            target_dir: Directory to scan

        Returns:
            Set of detected language names
        """
        languages = set()

        # Extension to language mapping
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".jsx": "javascript",
            ".tsx": "javascript",
            ".go": "go",
            ".rs": "rust",
        }

        # Scan files (limit depth to avoid node_modules, venv, etc.)
        for ext, lang in ext_map.items():
            # Check if any files with this extension exist
            files = list(target_dir.glob(f"**/*{ext}"))
            # Filter out common ignore patterns
            files = [
                f for f in files
                if not any(
                    part in f.parts
                    for part in ["node_modules", "venv", ".venv", "env", ".git", "dist", "build"]
                )
            ]
            if files:
                languages.add(lang)

        return languages
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -v`
Expected: 3 tests PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: add language detection for StylePillar

Detects Python, JavaScript/TypeScript, Go, and Rust by file extensions.
Filters out common dependency/virtual environment directories.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Level 1 - Check for Any Linter Config

**Files:**
- Modify: `tests/pillars/test_style.py`
- Modify: `src/agent_readiness/pillars/style.py`

**Step 1: Write failing test**

Add to `tests/pillars/test_style.py`:
```python
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
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_check_any_linter_config_python_ruff -v`
Expected: FAIL with "AttributeError: 'StylePillar' object has no attribute '_check_any_linter_config'"

**Step 3: Implement _check_any_linter_config**

Add to `src/agent_readiness/pillars/style.py`:
```python
from agent_readiness.models import CheckResult, Severity

class StylePillar(Pillar):
    # ... existing code ...

    def _check_any_linter_config(self, target_dir: Path, languages: set[str]) -> CheckResult:
        """Check if any linter configuration exists.

        Args:
            target_dir: Directory to scan
            languages: Set of detected languages

        Returns:
            CheckResult indicating if linter config was found
        """
        # Language-specific linter config files
        linter_configs = {
            "python": [
                "ruff.toml",
                ".ruff.toml",
                ".flake8",
                ".pylintrc",
                "pylint.rc",
                "pyproject.toml",  # Check content later
            ],
            "javascript": [
                ".eslintrc",
                ".eslintrc.json",
                ".eslintrc.js",
                ".eslintrc.yml",
                ".eslintrc.yaml",
                "eslint.config.js",
            ],
            "go": [
                ".golangci.yml",
                ".golangci.yaml",
            ],
            "rust": [
                "rustfmt.toml",
                ".rustfmt.toml",
            ],
        }

        found_configs = []

        for lang in languages:
            if lang not in linter_configs:
                continue

            for config_file in linter_configs[lang]:
                config_path = target_dir / config_file
                if config_path.exists():
                    # For pyproject.toml, check if it has linter config
                    if config_file == "pyproject.toml":
                        content = config_path.read_text()
                        if "[tool.ruff]" in content or "[tool.pylint]" in content or "[tool.flake8]" in content:
                            found_configs.append(config_file)
                            break
                    else:
                        found_configs.append(config_file)
                        break

        if found_configs:
            return CheckResult(
                name="Has linter configuration",
                passed=True,
                message=f"Found linter config: {', '.join(found_configs)}",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Has linter configuration",
                passed=False,
                message="No linter configuration found for detected languages",
                severity=Severity.WARNING,
            )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_check_any_linter_config -v`
Expected: 4 tests PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: implement Level 1 check for linter config

Checks for Python (ruff, flake8, pylint), JavaScript (eslint),
Go (golangci), and Rust (rustfmt) linter configurations.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Level 2 - Check Formatter Config

**Files:**
- Modify: `tests/pillars/test_style.py`
- Modify: `src/agent_readiness/pillars/style.py`

**Step 1: Write failing test**

Add to `tests/pillars/test_style.py`:
```python
def test_check_formatter_config_python_black(tmp_path: Path) -> None:
    """Test detecting black config in pyproject.toml."""
    (tmp_path / "main.py").touch()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.black]\nline-length = 100\n")

    pillar = StylePillar()
    result = pillar._check_formatter_config(tmp_path, {"python"})

    assert result.passed
    assert "black" in result.message.lower()


def test_check_formatter_config_javascript_prettier(tmp_path: Path) -> None:
    """Test detecting .prettierrc for JavaScript."""
    (tmp_path / "app.js").touch()
    (tmp_path / ".prettierrc").touch()

    pillar = StylePillar()
    result = pillar._check_formatter_config(tmp_path, {"javascript"})

    assert result.passed
    assert "prettier" in result.message.lower()


def test_check_formatter_config_go_always_passes(tmp_path: Path) -> None:
    """Test that Go always passes (gofmt is built-in)."""
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
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_check_formatter_config_python_black -v`
Expected: FAIL with "AttributeError: 'StylePillar' object has no attribute '_check_formatter_config'"

**Step 3: Implement _check_formatter_config**

Add to `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    # ... existing code ...

    def _check_formatter_config(self, target_dir: Path, languages: set[str]) -> CheckResult:
        """Check if formatter configuration exists.

        Args:
            target_dir: Directory to scan
            languages: Set of detected languages

        Returns:
            CheckResult indicating if formatter config was found
        """
        formatter_configs = {
            "python": [
                ("pyproject.toml", "[tool.black]"),
                ("ruff.toml", None),  # ruff can format
                (".black", None),
            ],
            "javascript": [
                (".prettierrc", None),
                (".prettierrc.json", None),
                (".prettierrc.js", None),
                (".prettierrc.yml", None),
                ("prettier.config.js", None),
            ],
            "go": [
                ("", None)  # gofmt is built-in, always available
            ],
            "rust": [
                ("rustfmt.toml", None),
                (".rustfmt.toml", None),
            ],
        }

        found_configs = []

        for lang in languages:
            if lang not in formatter_configs:
                continue

            # Special case for Go - always has gofmt
            if lang == "go":
                found_configs.append("gofmt (built-in)")
                continue

            for config_item in formatter_configs[lang]:
                if isinstance(config_item, tuple):
                    config_file, required_content = config_item
                else:
                    config_file = config_item
                    required_content = None

                if not config_file:
                    continue

                config_path = target_dir / config_file
                if config_path.exists():
                    # If specific content required, check for it
                    if required_content:
                        content = config_path.read_text()
                        if required_content in content:
                            found_configs.append(config_file)
                            break
                    else:
                        found_configs.append(config_file)
                        break

        if found_configs:
            return CheckResult(
                name="Has formatter configuration",
                passed=True,
                message=f"Found formatter config: {', '.join(found_configs)}",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Has formatter configuration",
                passed=False,
                message="No formatter configuration found for detected languages",
                severity=Severity.WARNING,
            )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_check_formatter_config -v`
Expected: 4 tests PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: implement Level 2 check for formatter config

Checks for Python (black, ruff), JavaScript (prettier),
Go (gofmt built-in), and Rust (rustfmt) formatter configurations.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Level 3 - Check Pre-commit Hooks

**Files:**
- Modify: `tests/pillars/test_style.py`
- Modify: `src/agent_readiness/pillars/style.py`

**Step 1: Write failing test**

Add to `tests/pillars/test_style.py`:
```python
def test_check_precommit_hooks_exists(tmp_path: Path) -> None:
    """Test detecting .pre-commit-config.yaml."""
    (tmp_path / ".pre-commit-config.yaml").touch()

    pillar = StylePillar()
    result = pillar._check_precommit_hooks(tmp_path)

    assert result.passed
    assert "pre-commit" in result.message.lower()


def test_check_precommit_hooks_not_found(tmp_path: Path) -> None:
    """Test when .pre-commit-config.yaml is missing."""
    pillar = StylePillar()
    result = pillar._check_precommit_hooks(tmp_path)

    assert not result.passed
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_check_precommit_hooks_exists -v`
Expected: FAIL with "AttributeError: 'StylePillar' object has no attribute '_check_precommit_hooks'"

**Step 3: Implement _check_precommit_hooks**

Add to `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    # ... existing code ...

    def _check_precommit_hooks(self, target_dir: Path) -> CheckResult:
        """Check if pre-commit hooks are configured.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult indicating if pre-commit hooks are configured
        """
        precommit_file = target_dir / ".pre-commit-config.yaml"

        if precommit_file.exists():
            return CheckResult(
                name="Pre-commit hooks configured",
                passed=True,
                message="Found .pre-commit-config.yaml",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Pre-commit hooks configured",
                passed=False,
                message="No .pre-commit-config.yaml found",
                severity=Severity.WARNING,
            )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_check_precommit_hooks -v`
Expected: 2 tests PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: implement Level 3 check for pre-commit hooks

Checks for .pre-commit-config.yaml file.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Level 3 - Check Linting in CI

**Files:**
- Modify: `tests/pillars/test_style.py`
- Modify: `src/agent_readiness/pillars/style.py`

**Step 1: Write failing test**

Add to `tests/pillars/test_style.py`:
```python
def test_check_linting_in_ci_github_actions(tmp_path: Path) -> None:
    """Test detecting lint in GitHub Actions."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    ci_file = workflows_dir / "ci.yml"
    ci_file.write_text("""
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run linter
        run: ruff check .
""")

    pillar = StylePillar()
    result = pillar._check_linting_in_ci(tmp_path)

    assert result.passed
    assert "GitHub Actions" in result.message


def test_check_linting_in_ci_gitlab(tmp_path: Path) -> None:
    """Test detecting lint in GitLab CI."""
    ci_file = tmp_path / ".gitlab-ci.yml"
    ci_file.write_text("""
lint:
  script:
    - eslint src/
""")

    pillar = StylePillar()
    result = pillar._check_linting_in_ci(tmp_path)

    assert result.passed
    assert "GitLab CI" in result.message


def test_check_linting_in_ci_not_found(tmp_path: Path) -> None:
    """Test when no CI linting is found."""
    pillar = StylePillar()
    result = pillar._check_linting_in_ci(tmp_path)

    assert not result.passed
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_check_linting_in_ci_github_actions -v`
Expected: FAIL with "AttributeError: 'StylePillar' object has no attribute '_check_linting_in_ci'"

**Step 3: Implement _check_linting_in_ci**

Add to `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    # ... existing code ...

    def _check_linting_in_ci(self, target_dir: Path) -> CheckResult:
        """Check if linting runs in CI pipeline.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult indicating if linting is configured in CI
        """
        ci_configs = {
            "GitHub Actions": target_dir / ".github" / "workflows",
            "GitLab CI": target_dir / ".gitlab-ci.yml",
            "CircleCI": target_dir / ".circleci" / "config.yml",
            "Travis CI": target_dir / ".travis.yml",
            "Jenkins": target_dir / "Jenkinsfile",
        }

        # Keywords that indicate linting
        lint_keywords = [
            "lint", "ruff", "eslint", "flake8", "pylint", "golangci-lint",
            "clippy",  # Rust linter
        ]

        found_in = []

        for ci_name, ci_path in ci_configs.items():
            if not ci_path.exists():
                continue

            # For directories (like GitHub Actions), check all YAML files
            if ci_path.is_dir():
                yaml_files = list(ci_path.glob("*.yml")) + list(ci_path.glob("*.yaml"))
                for yaml_file in yaml_files:
                    content = yaml_file.read_text().lower()
                    if any(keyword in content for keyword in lint_keywords):
                        found_in.append(ci_name)
                        break
            # For single files, check content
            else:
                content = ci_path.read_text().lower()
                if any(keyword in content for keyword in lint_keywords):
                    found_in.append(ci_name)

        if found_in:
            return CheckResult(
                name="Linting runs in CI",
                passed=True,
                message=f"Found linting in: {', '.join(found_in)}",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Linting runs in CI",
                passed=False,
                message="No linting found in CI configuration",
                severity=Severity.WARNING,
            )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_check_linting_in_ci -v`
Expected: 3 tests PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: implement Level 3 check for linting in CI

Checks for lint commands in GitHub Actions, GitLab CI, CircleCI,
Travis CI, and Jenkins configurations.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Level 3 - Check Formatting in CI

**Files:**
- Modify: `tests/pillars/test_style.py`
- Modify: `src/agent_readiness/pillars/style.py`

**Step 1: Write failing test**

Add to `tests/pillars/test_style.py`:
```python
def test_check_formatting_in_ci_github_actions(tmp_path: Path) -> None:
    """Test detecting format check in GitHub Actions."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    ci_file = workflows_dir / "ci.yml"
    ci_file.write_text("""
name: CI
on: [push]
jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check formatting
        run: black --check .
""")

    pillar = StylePillar()
    result = pillar._check_formatting_in_ci(tmp_path)

    assert result.passed
    assert "GitHub Actions" in result.message


def test_check_formatting_in_ci_not_found(tmp_path: Path) -> None:
    """Test when no CI formatting is found."""
    pillar = StylePillar()
    result = pillar._check_formatting_in_ci(tmp_path)

    assert not result.passed
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_check_formatting_in_ci_github_actions -v`
Expected: FAIL with "AttributeError: 'StylePillar' object has no attribute '_check_formatting_in_ci'"

**Step 3: Implement _check_formatting_in_ci**

Add to `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    # ... existing code ...

    def _check_formatting_in_ci(self, target_dir: Path) -> CheckResult:
        """Check if formatting runs in CI pipeline.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult indicating if formatting is configured in CI
        """
        ci_configs = {
            "GitHub Actions": target_dir / ".github" / "workflows",
            "GitLab CI": target_dir / ".gitlab-ci.yml",
            "CircleCI": target_dir / ".circleci" / "config.yml",
            "Travis CI": target_dir / ".travis.yml",
            "Jenkins": target_dir / "Jenkinsfile",
        }

        # Keywords that indicate formatting
        format_keywords = [
            "format", "black", "prettier", "rustfmt", "gofmt",
            "ruff format",  # ruff's formatter
        ]

        found_in = []

        for ci_name, ci_path in ci_configs.items():
            if not ci_path.exists():
                continue

            # For directories (like GitHub Actions), check all YAML files
            if ci_path.is_dir():
                yaml_files = list(ci_path.glob("*.yml")) + list(ci_path.glob("*.yaml"))
                for yaml_file in yaml_files:
                    content = yaml_file.read_text().lower()
                    if any(keyword in content for keyword in format_keywords):
                        found_in.append(ci_name)
                        break
            # For single files, check content
            else:
                content = ci_path.read_text().lower()
                if any(keyword in content for keyword in format_keywords):
                    found_in.append(ci_name)

        if found_in:
            return CheckResult(
                name="Formatting runs in CI",
                passed=True,
                message=f"Found formatting in: {', '.join(found_in)}",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Formatting runs in CI",
                passed=False,
                message="No formatting found in CI configuration",
                severity=Severity.WARNING,
            )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_check_formatting_in_ci -v`
Expected: 2 tests PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: implement Level 3 check for formatting in CI

Checks for format commands in GitHub Actions, GitLab CI, CircleCI,
Travis CI, and Jenkins configurations.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Wire Up evaluate() Method with Level 1-3 Checks

**Files:**
- Modify: `src/agent_readiness/pillars/style.py`
- Modify: `tests/pillars/test_style.py`

**Step 1: Write integration test**

Add to `tests/pillars/test_style.py`:
```python
def test_evaluate_full_level_3(tmp_path: Path) -> None:
    """Test full evaluation with Level 1-3 checks."""
    # Setup: Python project with all Level 3 features
    (tmp_path / "main.py").touch()
    (tmp_path / "ruff.toml").touch()

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.black]\nline-length = 100\n")

    (tmp_path / ".pre-commit-config.yaml").touch()

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    ci_file = workflows_dir / "ci.yml"
    ci_file.write_text("run: ruff check . && black --check .")

    pillar = StylePillar()
    results = pillar.evaluate(tmp_path)

    # Should have 5 checks: linter, formatter, precommit, lint in CI, format in CI
    assert len(results) == 5
    assert all(r.passed for r in results)


def test_evaluate_minimal(tmp_path: Path) -> None:
    """Test evaluation with minimal setup."""
    (tmp_path / "main.py").touch()

    pillar = StylePillar()
    results = pillar.evaluate(tmp_path)

    # Should still run all checks, but most will fail
    assert len(results) == 5
    assert sum(1 for r in results if r.passed) == 0
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_evaluate_full_level_3 -v`
Expected: FAIL with "AssertionError: assert 0 == 5" (evaluate returns empty list)

**Step 3: Implement evaluate() method**

Update `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    # ... existing code ...

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for style and validation checks.

        Args:
            target_dir: Directory to evaluate

        Returns:
            List of CheckResult objects for all checks
        """
        checks = []

        # Detect languages first
        languages = self._detect_languages(target_dir)

        # Level 1: Basic linting exists
        checks.append(self._check_any_linter_config(target_dir, languages))

        # Level 2: Explicit configs
        checks.append(self._check_formatter_config(target_dir, languages))

        # Level 3: Automation
        checks.append(self._check_precommit_hooks(target_dir))
        checks.append(self._check_linting_in_ci(target_dir))
        checks.append(self._check_formatting_in_ci(target_dir))

        return checks
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_evaluate -v`
Expected: 2 tests PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: wire up evaluate() with Level 1-3 checks

Implements full evaluation flow for basic checks.
Level 4-5 checks will be added in subsequent commits.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Level 4 - Check Editor Integration Documentation

**Files:**
- Modify: `tests/pillars/test_style.py`
- Modify: `src/agent_readiness/pillars/style.py`

**Step 1: Write failing test**

Add to `tests/pillars/test_style.py`:
```python
def test_check_editor_integration_vscode(tmp_path: Path) -> None:
    """Test detecting VSCode settings."""
    vscode_dir = tmp_path / ".vscode"
    vscode_dir.mkdir()
    settings = vscode_dir / "settings.json"
    settings.write_text('{"editor.formatOnSave": true}')

    pillar = StylePillar()
    result = pillar._check_editor_integration_documented(tmp_path)

    assert result.passed
    assert "VSCode" in result.message or ".vscode" in result.message


def test_check_editor_integration_editorconfig(tmp_path: Path) -> None:
    """Test detecting .editorconfig."""
    (tmp_path / ".editorconfig").touch()

    pillar = StylePillar()
    result = pillar._check_editor_integration_documented(tmp_path)

    assert result.passed
    assert ".editorconfig" in result.message


def test_check_editor_integration_docs(tmp_path: Path) -> None:
    """Test detecting editor setup in docs."""
    readme = tmp_path / "CONTRIBUTING.md"
    readme.write_text("## Editor Setup\n\nInstall the ESLint extension...")

    pillar = StylePillar()
    result = pillar._check_editor_integration_documented(tmp_path)

    assert result.passed


def test_check_editor_integration_not_found(tmp_path: Path) -> None:
    """Test when no editor integration is found."""
    pillar = StylePillar()
    result = pillar._check_editor_integration_documented(tmp_path)

    assert not result.passed
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_check_editor_integration_vscode -v`
Expected: FAIL with "AttributeError: 'StylePillar' object has no attribute '_check_editor_integration_documented'"

**Step 3: Implement _check_editor_integration_documented**

Add to `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    # ... existing code ...

    def _check_editor_integration_documented(self, target_dir: Path) -> CheckResult:
        """Check if editor integration is documented.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult indicating if editor integration is documented
        """
        found_items = []

        # Check for VSCode settings
        vscode_settings = target_dir / ".vscode" / "settings.json"
        if vscode_settings.exists():
            found_items.append("VSCode settings")

        # Check for .editorconfig
        editorconfig = target_dir / ".editorconfig"
        if editorconfig.exists():
            found_items.append(".editorconfig")

        # Check for documentation mentioning editor setup
        doc_files = [
            target_dir / "CONTRIBUTING.md",
            target_dir / "README.md",
            target_dir / "DEVELOPMENT.md",
        ]

        editor_keywords = ["editor setup", "editor config", "vscode", "eslint extension", "editor integration"]

        for doc_file in doc_files:
            if doc_file.exists():
                content = doc_file.read_text().lower()
                if any(keyword in content for keyword in editor_keywords):
                    found_items.append(f"Documentation in {doc_file.name}")
                    break

        if found_items:
            return CheckResult(
                name="Editor integration documented",
                passed=True,
                message=f"Found: {', '.join(found_items)}",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Editor integration documented",
                passed=False,
                message="No editor integration documentation found",
                severity=Severity.INFO,  # Lower severity for Level 4
            )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_check_editor_integration -v`
Expected: 4 tests PASS

**Step 5: Update evaluate() to include Level 4 check**

Update `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for style and validation checks."""
        checks = []
        languages = self._detect_languages(target_dir)

        # Level 1: Basic linting exists
        checks.append(self._check_any_linter_config(target_dir, languages))

        # Level 2: Explicit configs
        checks.append(self._check_formatter_config(target_dir, languages))

        # Level 3: Automation
        checks.append(self._check_precommit_hooks(target_dir))
        checks.append(self._check_linting_in_ci(target_dir))
        checks.append(self._check_formatting_in_ci(target_dir))

        # Level 4: Optimization
        checks.append(self._check_editor_integration_documented(target_dir))

        return checks
```

**Step 6: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: implement Level 4 check for editor integration

Checks for VSCode settings, .editorconfig, and editor setup
documentation in README/CONTRIBUTING files.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Level 5 - Check Style Guide for Agents

**Files:**
- Modify: `tests/pillars/test_style.py`
- Modify: `src/agent_readiness/pillars/style.py`

**Step 1: Write failing test**

Add to `tests/pillars/test_style.py`:
```python
def test_check_style_guide_agents_md(tmp_path: Path) -> None:
    """Test detecting AGENTS.md with style section."""
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("## Code Style\n\nWe use ruff for linting...")

    pillar = StylePillar()
    result = pillar._check_style_guide_for_agents(tmp_path)

    assert result.passed
    assert "AGENTS.md" in result.message


def test_check_style_guide_style_md(tmp_path: Path) -> None:
    """Test detecting STYLE.md."""
    style_md = tmp_path / "STYLE.md"
    style_md.write_text("# Style Guide\n\nOur coding conventions...")

    pillar = StylePillar()
    result = pillar._check_style_guide_for_agents(tmp_path)

    assert result.passed
    assert "STYLE.md" in result.message


def test_check_style_guide_contributing(tmp_path: Path) -> None:
    """Test detecting style guide in CONTRIBUTING.md."""
    contrib = tmp_path / "CONTRIBUTING.md"
    contrib.write_text("## Style Guidelines\n\nFollow these conventions...")

    pillar = StylePillar()
    result = pillar._check_style_guide_for_agents(tmp_path)

    assert result.passed


def test_check_style_guide_not_found(tmp_path: Path) -> None:
    """Test when no style guide is found."""
    pillar = StylePillar()
    result = pillar._check_style_guide_for_agents(tmp_path)

    assert not result.passed
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/pillars/test_style.py::test_check_style_guide_agents_md -v`
Expected: FAIL with "AttributeError: 'StylePillar' object has no attribute '_check_style_guide_for_agents'"

**Step 3: Implement _check_style_guide_for_agents**

Add to `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    # ... existing code ...

    def _check_style_guide_for_agents(self, target_dir: Path) -> CheckResult:
        """Check if style guidelines are documented for AI agents.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult indicating if style guide exists
        """
        # Check for STYLE.md
        style_md = target_dir / "STYLE.md"
        if style_md.exists():
            return CheckResult(
                name="Style guide for agents",
                passed=True,
                message="Found STYLE.md",
                severity=Severity.INFO,
            )

        # Check for AGENTS.md with style section
        agents_md = target_dir / "AGENTS.md"
        if agents_md.exists():
            content = agents_md.read_text().lower()
            if any(keyword in content for keyword in ["style", "coding standard", "convention"]):
                return CheckResult(
                    name="Style guide for agents",
                    passed=True,
                    message="Found style section in AGENTS.md",
                    severity=Severity.INFO,
                )

        # Check CONTRIBUTING.md for detailed style guidelines
        contributing = target_dir / "CONTRIBUTING.md"
        if contributing.exists():
            content = contributing.read_text().lower()
            style_keywords = ["style guide", "coding standard", "style convention", "code style"]
            if any(keyword in content for keyword in style_keywords):
                return CheckResult(
                    name="Style guide for agents",
                    passed=True,
                    message="Found style guide in CONTRIBUTING.md",
                    severity=Severity.INFO,
                )

        return CheckResult(
            name="Style guide for agents",
            passed=False,
            message="No style guide documentation found (STYLE.md, AGENTS.md, or CONTRIBUTING.md)",
            severity=Severity.INFO,
        )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/pillars/test_style.py -k test_check_style_guide -v`
Expected: 4 tests PASS

**Step 5: Update evaluate() to include Level 5 check**

Update `src/agent_readiness/pillars/style.py`:
```python
class StylePillar(Pillar):
    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for style and validation checks."""
        checks = []
        languages = self._detect_languages(target_dir)

        # Level 1: Basic linting exists
        checks.append(self._check_any_linter_config(target_dir, languages))

        # Level 2: Explicit configs
        checks.append(self._check_formatter_config(target_dir, languages))

        # Level 3: Automation
        checks.append(self._check_precommit_hooks(target_dir))
        checks.append(self._check_linting_in_ci(target_dir))
        checks.append(self._check_formatting_in_ci(target_dir))

        # Level 4: Optimization
        checks.append(self._check_editor_integration_documented(target_dir))

        # Level 5: Autonomous
        checks.append(self._check_style_guide_for_agents(target_dir))

        return checks
```

**Step 6: Commit**

```bash
git add src/agent_readiness/pillars/style.py tests/pillars/test_style.py
git commit -m "feat: implement Level 5 check for agent style guide

Checks for STYLE.md, style section in AGENTS.md, or
comprehensive style guidelines in CONTRIBUTING.md.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Test StylePillar Integration with Scanner

**Files:**
- Create: `tests/test_integration.py`
- Modify: `src/agent_readiness/pillars/__init__.py`

**Step 1: Write integration test**

Create `tests/test_integration.py`:
```python
"""Integration tests for scanner and pillars."""

from pathlib import Path
from agent_readiness.scanner import Scanner
from agent_readiness.pillars import StylePillar


def test_scanner_with_style_pillar(tmp_path: Path) -> None:
    """Test Scanner integration with StylePillar."""
    # Setup: Python project with some features
    (tmp_path / "main.py").touch()
    (tmp_path / "ruff.toml").touch()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.black]\nline-length = 100\n")

    # Create scanner and register pillar
    scanner = Scanner()
    scanner.register_pillar(StylePillar())

    # Run scan
    result = scanner.scan(tmp_path)

    # Verify results
    assert result.target_directory == str(tmp_path.resolve())
    assert len(result.pillars) == 1
    assert result.pillars[0].name == "Style & Validation"
    assert len(result.pillars[0].checks) == 7  # All checks from Level 1-5

    # Should have linter and formatter passing, others failing
    passed = sum(1 for c in result.pillars[0].checks if c.passed)
    assert passed == 2  # linter and formatter only

    # Overall score should reflect this
    assert 0 < result.overall_score < 50  # Some checks passing but not many
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_integration.py::test_scanner_with_style_pillar -v`
Expected: FAIL (test file doesn't exist or import fails)

**Step 3: Create the test file and run**

Run: `pytest tests/test_integration.py::test_scanner_with_style_pillar -v`
Expected: Test should PASS (StylePillar is already complete)

**Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test for StylePillar with Scanner

Verifies that StylePillar works correctly when registered
with the Scanner.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Run Full Test Suite

**Files:**
- None

**Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 2: Run with coverage**

Run: `pytest tests/ -v --cov=agent_readiness --cov-report=term-missing`
Expected: Coverage >80% (ideally >90%)

**Step 3: If coverage is low, identify untested lines**

Check coverage report output
Add tests for any critical untested code paths

**Step 4: Run linter**

Run: `ruff check src/ tests/`
Expected: No errors

**Step 5: Run formatter check**

Run: `black --check src/ tests/`
Expected: All files formatted correctly

**Step 6: If linter/formatter finds issues, fix them**

Run: `ruff check --fix src/ tests/`
Run: `black src/ tests/`

**Step 7: Commit any formatting fixes**

```bash
git add -A
git commit -m "style: apply ruff and black formatting

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`

**Step 1: Update README roadmap**

Update `/Users/julienmika/Code/agent-readiness-score/.worktrees/pillar-1-style-validation/README.md`:

Change:
```markdown
- [ ] Pillar 1: Style & Validation checks
```

To:
```markdown
- [x] Pillar 1: Style & Validation checks
```

**Step 2: Update AGENTS.md**

Update `/Users/julienmika/Code/agent-readiness-score/.worktrees/pillar-1-style-validation/AGENTS.md`:

Add after line 26:
```markdown

### Pillar 1: Style & Validation (`pillars/style.py`)

Checks for:
- **Level 1**: Any linter configuration (ruff, eslint, etc.)
- **Level 2**: Formatter configuration (black, prettier, etc.)
- **Level 3**: Pre-commit hooks, CI linting/formatting
- **Level 4**: Editor integration documentation
- **Level 5**: Style guide for AI agents

**Language Support**: Python, JavaScript/TypeScript, Go, Rust
**CI Detection**: GitHub Actions, GitLab CI, CircleCI, Jenkins, Travis CI
```

**Step 3: Commit documentation updates**

```bash
git add README.md AGENTS.md
git commit -m "docs: update README and AGENTS.md for Pillar 1

Mark Pillar 1 as complete and document its capabilities.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Final Verification & Push

**Files:**
- None

**Step 1: Run complete test suite one more time**

Run: `pytest tests/ -v --cov=agent_readiness`
Expected: All tests PASS, good coverage

**Step 2: Verify git status is clean**

Run: `git status`
Expected: "nothing to commit, working tree clean"

**Step 3: View commit history**

Run: `git log --oneline -15`
Expected: Should see all commits from this implementation

**Step 4: Push branch to remote**

Run: `git push -u origin pillar-1-style-validation`

**Step 5: Create pull request**

Run: `gh pr create --title "feat: Implement Pillar 1 - Style & Validation" --body "$(cat <<'EOF'
## Summary

Implements Pillar 1: Style & Validation for the agent readiness scoring system.

## Features

### Multi-Language Support
- Python (ruff, flake8, pylint, black)
- JavaScript/TypeScript (eslint, prettier)
- Go (golangci-lint, gofmt)
- Rust (rustfmt, clippy)

### Maturity Levels
- **Level 1**: Basic linter configuration exists
- **Level 2**: Explicit linter and formatter configs
- **Level 3**: Pre-commit hooks + CI automation
- **Level 4**: Editor integration documented
- **Level 5**: Style guide for AI agents

### CI Platform Support
- GitHub Actions
- GitLab CI
- CircleCI
- Jenkins
- Travis CI

## Testing

- Comprehensive unit tests for all checks
- Integration test with Scanner
- Coverage: >90%

## Files Changed

- `src/agent_readiness/pillars/style.py` - StylePillar implementation
- `tests/pillars/test_style.py` - Unit tests
- `tests/test_integration.py` - Integration tests
- `README.md` - Updated roadmap
- `AGENTS.md` - Documented Pillar 1

## Closes

Closes #2

🦞 Generated with Claude Code
EOF
)"`

---

## Success Criteria

- [x] All Level 1-5 checks implemented
- [x] Multi-language support (Python, JS/TS, Go, Rust)
- [x] CI detection (5 platforms)
- [x] Comprehensive tests with >80% coverage
- [x] Integration with Scanner verified
- [x] Documentation updated
- [x] All tests passing
- [x] Code formatted and linted
- [x] Pull request created

## Notes

- This implementation focuses on file detection and content searching
- Future enhancements could include actually running linters to verify configs are valid
- Performance optimization may be needed for very large repositories
- Additional languages can be added by extending the language detection maps
