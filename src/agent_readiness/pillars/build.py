"""Build System pillar implementation."""

import json
from pathlib import Path

from agent_readiness.models import CheckResult, Severity
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
                        message=f"{lang.capitalize()} project found: {', '.join(found_files)}",
                        severity=Severity.REQUIRED,
                        level=1,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        name=f"{lang.capitalize()} package manager",
                        passed=False,
                        message=f"No {lang} package manager file found (expected: {', '.join(files)})",
                        severity=Severity.REQUIRED,
                        level=1,
                    )
                )

        return results

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
                        message=f"{lang.capitalize()} lock file found: {', '.join(found_files)}",
                        severity=Severity.RECOMMENDED,
                        level=2,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        name=f"{lang.capitalize()} lock file",
                        passed=False,
                        message=f"No {lang} lock file found (expected: {', '.join(files)})",
                        severity=Severity.RECOMMENDED,
                        level=2,
                    )
                )

        return results

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
                message=f"Build cache configured in {', '.join(found)}",
                severity=Severity.OPTIONAL,
                level=4,
            )
        else:
            return CheckResult(
                name="Build caching",
                passed=False,
                message="No build cache detected in CI configuration",
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
