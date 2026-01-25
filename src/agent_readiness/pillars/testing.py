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

    def _check_tests_in_ci(self, target_dir: Path) -> CheckResult:
        """Check if tests run in CI pipeline.

        Args:
            target_dir: Directory to scan

        Returns:
            Single CheckResult for the repository
        """
        # CI configuration locations to check
        ci_configs = [
            (".github/workflows", "*.yml", "GitHub Actions"),
            (".github/workflows", "*.yaml", "GitHub Actions"),
            (".gitlab-ci.yml", None, "GitLab CI"),
            (".circleci/config.yml", None, "CircleCI"),
        ]

        # Test commands to look for
        test_commands = ["pytest", "npm test", "go test", "cargo test", "make test"]

        for config_path, pattern, ci_name in ci_configs:
            if pattern:
                # Directory with multiple files
                ci_dir = target_dir / config_path
                if ci_dir.exists() and ci_dir.is_dir():
                    for ci_file in ci_dir.glob(pattern):
                        try:
                            content = ci_file.read_text(encoding="utf-8", errors="ignore").lower()
                            for cmd in test_commands:
                                if cmd in content:
                                    return CheckResult(
                                        name="Tests in CI",
                                        passed=True,
                                        message=f"Tests run in CI: {ci_name} ({ci_file.name})",
                                        severity=Severity.RECOMMENDED,
                                        level=3,
                                    )
                        except Exception:
                            continue
            else:
                # Single file
                ci_file = target_dir / config_path
                if ci_file.exists():
                    try:
                        content = ci_file.read_text(encoding="utf-8", errors="ignore").lower()
                        for cmd in test_commands:
                            if cmd in content:
                                return CheckResult(
                                    name="Tests in CI",
                                    passed=True,
                                    message=f"Tests run in CI: {ci_name} ({ci_file.name})",
                                    severity=Severity.RECOMMENDED,
                                    level=3,
                                )
                    except Exception:
                        continue

        return CheckResult(
            name="Tests in CI",
            passed=False,
            message="No CI configuration found with test commands",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_coverage_measured(self, target_dir: Path) -> list[CheckResult]:
        """Check if test coverage is being measured for each language.

        Args:
            target_dir: Directory to scan

        Returns:
            List of CheckResult, one per detected language
        """
        test_info = self._detect_test_infrastructure(target_dir)
        results = []

        if not test_info["languages"]:
            # No tests detected, return empty list
            return results

        for language in sorted(test_info["languages"]):
            if language == "python":
                result = self._check_python_coverage(target_dir)
            elif language == "javascript":
                result = self._check_javascript_coverage(target_dir)
            elif language == "go":
                result = self._check_go_coverage(target_dir)
            elif language == "rust":
                result = self._check_rust_coverage(target_dir)
            else:
                # Unknown language, skip
                continue

            results.append(result)

        return results

    def _check_python_coverage(self, target_dir: Path) -> CheckResult:
        """Check if Python coverage is configured.

        Looks for:
        - pytest-cov in pyproject.toml [tool.pytest.ini_options] addopts
        - coverage section in pyproject.toml
        - .coveragerc file
        - pytest.ini with coverage options

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for Python coverage
        """
        # Check pyproject.toml
        pyproject_path = target_dir / "pyproject.toml"
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text(encoding="utf-8", errors="ignore")
                # Check for pytest-cov in addopts or coverage tool section
                if "--cov" in content or "[tool.coverage" in content:
                    return CheckResult(
                        name="Coverage measured (python)",
                        passed=True,
                        message="Python coverage measured (pytest-cov configured)",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
            except Exception:
                pass

        # Check .coveragerc
        coveragerc_path = target_dir / ".coveragerc"
        if coveragerc_path.exists():
            return CheckResult(
                name="Coverage measured (python)",
                passed=True,
                message="Python coverage measured (.coveragerc found)",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        # Check pytest.ini
        pytest_ini_path = target_dir / "pytest.ini"
        if pytest_ini_path.exists():
            try:
                content = pytest_ini_path.read_text(encoding="utf-8", errors="ignore")
                if "--cov" in content or "coverage" in content:
                    return CheckResult(
                        name="Coverage measured (python)",
                        passed=True,
                        message="Python coverage measured (pytest.ini configured)",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
            except Exception:
                pass

        # Not configured
        return CheckResult(
            name="Coverage measured (python)",
            passed=False,
            message="Python coverage not configured",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_javascript_coverage(self, target_dir: Path) -> CheckResult:
        """Check if JavaScript coverage is configured.

        Looks for:
        - jest collectCoverage in jest.config.js or package.json
        - vitest coverage in vitest.config
        - nyc in package.json scripts

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for JavaScript coverage
        """
        # Check package.json
        package_json_path = target_dir / "package.json"
        if package_json_path.exists():
            try:
                content = package_json_path.read_text(encoding="utf-8", errors="ignore")
                if "collectCoverage" in content or "coverage" in content:
                    return CheckResult(
                        name="Coverage measured (javascript)",
                        passed=True,
                        message="JavaScript coverage measured (package.json configured)",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
            except Exception:
                pass

        # Check jest.config.js
        jest_config_path = target_dir / "jest.config.js"
        if jest_config_path.exists():
            try:
                content = jest_config_path.read_text(encoding="utf-8", errors="ignore")
                if "collectCoverage" in content or "coverage" in content:
                    return CheckResult(
                        name="Coverage measured (javascript)",
                        passed=True,
                        message="JavaScript coverage measured (jest.config.js configured)",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
            except Exception:
                pass

        # Check vitest.config
        for vitest_config in ["vitest.config.js", "vitest.config.ts"]:
            vitest_config_path = target_dir / vitest_config
            if vitest_config_path.exists():
                try:
                    content = vitest_config_path.read_text(encoding="utf-8", errors="ignore")
                    if "coverage" in content:
                        return CheckResult(
                            name="Coverage measured (javascript)",
                            passed=True,
                            message="JavaScript coverage measured (vitest configured)",
                            severity=Severity.RECOMMENDED,
                            level=3,
                        )
                except Exception:
                    pass

        # Not configured
        return CheckResult(
            name="Coverage measured (javascript)",
            passed=False,
            message="JavaScript coverage not configured",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_go_coverage(self, target_dir: Path) -> CheckResult:
        """Check if Go coverage is configured.

        Go has built-in coverage support, so this always passes.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for Go coverage (always passes)
        """
        return CheckResult(
            name="Coverage measured (go)",
            passed=True,
            message="Go coverage measured (built-in support)",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_rust_coverage(self, target_dir: Path) -> CheckResult:
        """Check if Rust coverage is configured.

        Looks for:
        - tarpaulin in Cargo.toml
        - llvm-cov configuration

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for Rust coverage
        """
        # Check Cargo.toml for tarpaulin or llvm-cov
        cargo_toml_path = target_dir / "Cargo.toml"
        if cargo_toml_path.exists():
            try:
                content = cargo_toml_path.read_text(encoding="utf-8", errors="ignore")
                if "tarpaulin" in content or "llvm-cov" in content:
                    return CheckResult(
                        name="Coverage measured (rust)",
                        passed=True,
                        message="Rust coverage measured (tarpaulin/llvm-cov configured)",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
            except Exception:
                pass

        # Not configured
        return CheckResult(
            name="Coverage measured (rust)",
            passed=False,
            message="Rust coverage not configured",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_unit_tests_isolated(
        self, target_dir: Path, languages: set
    ) -> list[CheckResult]:
        """Check if unit tests use isolation patterns (fixtures, mocks).

        Per-language check for test isolation practices.
        - Python: Looks for @pytest.fixture or unittest.mock
        - JavaScript: Looks for jest.mock or vi.mock
        - Go: Always passes (interface-based isolation)
        - Rust: Always passes (isolated by default)

        Args:
            target_dir: Directory to scan
            languages: Set of languages to check

        Returns:
            List of CheckResult, one per language
        """
        results = []

        for language in sorted(languages):
            if language == "python":
                result = self._check_python_isolation(target_dir)
            elif language == "javascript":
                result = self._check_javascript_isolation(target_dir)
            elif language == "go":
                result = self._check_go_isolation(target_dir)
            elif language == "rust":
                result = self._check_rust_isolation(target_dir)
            else:
                # Unknown language, skip
                continue

            results.append(result)

        return results

    def _check_python_isolation(self, target_dir: Path) -> CheckResult:
        """Check if Python tests use isolation patterns (fixtures, mocks).

        Looks for @pytest.fixture or unittest.mock in test files.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for Python isolation
        """
        test_info = self._detect_test_infrastructure(target_dir)
        test_files = test_info["test_files"]["python"]

        if not test_files:
            return CheckResult(
                name="Unit tests isolated (python)",
                passed=False,
                message="No Python test files found",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        # Sample first 10 files to avoid scanning everything
        files_to_check = test_files[:10]

        isolation_patterns = ["@pytest.fixture", "unittest.mock", "from unittest import mock"]
        found_patterns = False

        for test_file in files_to_check:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in isolation_patterns:
                    if pattern in content:
                        found_patterns = True
                        break
                if found_patterns:
                    break
            except Exception:
                continue

        if found_patterns:
            return CheckResult(
                name="Unit tests isolated (python)",
                passed=True,
                message="Python tests use isolation patterns (fixtures/mocks)",
                severity=Severity.RECOMMENDED,
                level=3,
            )
        else:
            return CheckResult(
                name="Unit tests isolated (python)",
                passed=False,
                message="Python tests do not use isolation patterns (fixtures/mocks)",
                severity=Severity.RECOMMENDED,
                level=3,
            )

    def _check_javascript_isolation(self, target_dir: Path) -> CheckResult:
        """Check if JavaScript tests use isolation patterns (mocks).

        Looks for jest.mock or vi.mock in test files.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for JavaScript isolation
        """
        test_info = self._detect_test_infrastructure(target_dir)
        test_files = test_info["test_files"]["javascript"]

        if not test_files:
            return CheckResult(
                name="Unit tests isolated (javascript)",
                passed=False,
                message="No JavaScript test files found",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        # Sample first 10 files to avoid scanning everything
        files_to_check = test_files[:10]

        isolation_patterns = ["jest.mock", "vi.mock"]
        found_patterns = False

        for test_file in files_to_check:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in isolation_patterns:
                    if pattern in content:
                        found_patterns = True
                        break
                if found_patterns:
                    break
            except Exception:
                continue

        if found_patterns:
            return CheckResult(
                name="Unit tests isolated (javascript)",
                passed=True,
                message="JavaScript tests use isolation patterns (mocks)",
                severity=Severity.RECOMMENDED,
                level=3,
            )
        else:
            return CheckResult(
                name="Unit tests isolated (javascript)",
                passed=False,
                message="JavaScript tests do not use isolation patterns (mocks)",
                severity=Severity.RECOMMENDED,
                level=3,
            )

    def _check_go_isolation(self, target_dir: Path) -> CheckResult:
        """Check if Go tests use isolation (always passes).

        Go achieves isolation through interfaces and dependency injection,
        which is implicit in the language design.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for Go isolation (always passes)
        """
        return CheckResult(
            name="Unit tests isolated (go)",
            passed=True,
            message="Go tests use isolation (interface-based design)",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_rust_isolation(self, target_dir: Path) -> CheckResult:
        """Check if Rust tests use isolation (always passes).

        Rust's type system and module system provide isolation by default.

        Args:
            target_dir: Directory to scan

        Returns:
            CheckResult for Rust isolation (always passes)
        """
        return CheckResult(
            name="Unit tests isolated (rust)",
            passed=True,
            message="Rust tests isolated (built-in isolation)",
            severity=Severity.RECOMMENDED,
            level=3,
        )
