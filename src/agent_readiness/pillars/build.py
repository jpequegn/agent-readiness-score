"""Build System pillar implementation."""

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
