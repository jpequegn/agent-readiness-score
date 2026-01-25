"""Testing pillar implementation."""

from pathlib import Path

from agent_readiness.pillar import Pillar
from agent_readiness.models import CheckResult, Severity


class TestingPillar(Pillar):
    """Evaluates test infrastructure and coverage."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Testing"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for testing checks."""
        return []

    def _detect_test_infrastructure(self, target_dir: Path) -> dict:
        """Detect test directories and infer languages.

        Args:
            target_dir: Directory to scan

        Returns:
            Dict with keys: languages (set), test_dirs (list), test_files (dict)
        """
        test_dirs = []
        test_files = {"python": [], "javascript": [], "go": [], "rust": []}
        languages = set()

        # Standard test directory names
        test_dir_names = ["tests", "test", "__tests__", "spec"]

        # Find test directories
        for dir_name in test_dir_names:
            test_dir = target_dir / dir_name
            if test_dir.exists() and test_dir.is_dir():
                test_dirs.append(test_dir)

        # Also check for src/**/test/, lib/**/test/ patterns
        for pattern in ["src/**/test", "lib/**/test"]:
            for test_dir in target_dir.glob(pattern):
                if test_dir.is_dir():
                    test_dirs.append(test_dir)

        # Scan all found test directories for test files
        test_patterns = {
            "python": ["test_*.py", "*_test.py"],
            "javascript": ["*.test.js", "*.spec.js", "*.test.ts", "*.spec.ts"],
            "go": ["*_test.go"],
            "rust": ["*_test.rs"],
        }

        seen_files = set()
        for test_dir in test_dirs:
            for lang, patterns in test_patterns.items():
                for pattern in patterns:
                    for test_file in test_dir.rglob(pattern):
                        if test_file.is_file() and str(test_file) not in seen_files:
                            test_files[lang].append(test_file)
                            languages.add(lang)
                            seen_files.add(str(test_file))

        return {
            "languages": languages,
            "test_dirs": test_dirs,
            "test_files": test_files,
        }

    def _check_tests_exist(self, target_dir: Path) -> CheckResult:
        """Check if any tests exist in the repository.

        Args:
            target_dir: Directory to scan

        Returns:
            Single CheckResult for the repository
        """
        test_info = self._detect_test_infrastructure(target_dir)
        total_files = sum(len(files) for files in test_info["test_files"].values())

        if total_files > 0:
            num_dirs = len(test_info["test_dirs"])
            file_word = "file" if total_files == 1 else "files"
            dir_word = "directory" if num_dirs == 1 else "directories"
            return CheckResult(
                name="Tests exist",
                passed=True,
                message=f"Found {total_files} test {file_word} in {num_dirs} {dir_word}",
                severity=Severity.REQUIRED,
                level=1,
            )
        else:
            return CheckResult(
                name="Tests exist",
                passed=False,
                message="No test files or directories found",
                severity=Severity.REQUIRED,
                level=1,
            )

    def _check_test_directory_structure(self, target_dir: Path) -> CheckResult:
        """Check if tests are organized in standard directory structure.

        Args:
            target_dir: Directory to scan

        Returns:
            Single CheckResult for the repository
        """
        test_info = self._detect_test_infrastructure(target_dir)
        total_files = sum(len(files) for files in test_info["test_files"].values())

        if total_files == 0:
            return CheckResult(
                name="Test directory structure",
                passed=False,
                message="No tests found to evaluate structure",
                severity=Severity.RECOMMENDED,
                level=2,
            )

        # Count files in standard directories
        files_in_standard_dirs = 0
        for test_dir in test_info["test_dirs"]:
            for lang_files in test_info["test_files"].values():
                for test_file in lang_files:
                    try:
                        test_file.relative_to(test_dir)
                        files_in_standard_dirs += 1
                    except ValueError:
                        pass

        percentage = (files_in_standard_dirs / total_files) * 100 if total_files > 0 else 0

        if percentage >= 50 and len(test_info["test_dirs"]) > 0:
            return CheckResult(
                name="Test directory structure",
                passed=True,
                message=(
                    f"Tests organized in standard directories "
                    f"({files_in_standard_dirs}/{total_files} files)"
                ),
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="Test directory structure",
                passed=False,
                message="Tests scattered outside standard directories (tests/, test/, __tests__/)",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_test_command_documented(self, target_dir: Path) -> CheckResult:
        """Check if test command is documented in README.

        Args:
            target_dir: Directory to scan

        Returns:
            Single CheckResult for the repository
        """
        readme_path = target_dir / "README.md"
        if not readme_path.exists():
            return CheckResult(
                name="Test command documented",
                passed=False,
                message="No README.md found",
                severity=Severity.RECOMMENDED,
                level=2,
            )

        try:
            content = readme_path.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            return CheckResult(
                name="Test command documented",
                passed=False,
                message="Could not read README.md",
                severity=Severity.RECOMMENDED,
                level=2,
            )

        # Look for test commands
        test_commands = ["pytest", "npm test", "go test", "cargo test", "make test"]
        found_commands = [cmd for cmd in test_commands if cmd in content]

        if found_commands:
            return CheckResult(
                name="Test command documented",
                passed=True,
                message=f"Test command documented in README.md: '{found_commands[0]}'",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="Test command documented",
                passed=False,
                message="No test command found in README.md",
                severity=Severity.RECOMMENDED,
                level=2,
            )
