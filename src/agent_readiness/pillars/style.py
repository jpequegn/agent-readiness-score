"""Style & Validation pillar implementation."""

from pathlib import Path
from agent_readiness.models import CheckResult, Severity
from agent_readiness.pillar import Pillar


class StylePillar(Pillar):
    """Evaluates code style enforcement and validation tooling."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Style & Validation"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for style and validation checks."""
        results = []

        # Detect languages first
        languages = self._detect_languages(target_dir)

        # Level 1: Check for any linter configuration
        results.append(self._check_any_linter_config(target_dir, languages))

        # Level 2: Check for formatter configuration
        results.append(self._check_formatter_config(target_dir, languages))

        # Level 3: Check for pre-commit hooks
        results.append(self._check_precommit_hooks(target_dir))

        # Level 4: Check for CI integration
        results.append(self._check_ci_integration(target_dir))

        # Level 5: Check for style guide documentation
        results.append(self._check_style_guide_docs(target_dir))

        return results

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

    def _check_any_linter_config(self, target_dir: Path, languages: set[str]) -> CheckResult:
        """Check if any linter configuration exists."""
        linter_configs = {
            "python": ["ruff.toml", ".ruff.toml", ".flake8", ".pylintrc", "pylint.rc", "pyproject.toml"],
            "javascript": [".eslintrc", ".eslintrc.json", ".eslintrc.js", ".eslintrc.yml", ".eslintrc.yaml", "eslint.config.js"],
            "go": [".golangci.yml", ".golangci.yaml"],
            "rust": ["rustfmt.toml", ".rustfmt.toml"],
        }

        found_configs = []
        for lang in languages:
            if lang not in linter_configs:
                continue
            for config_file in linter_configs[lang]:
                config_path = target_dir / config_file
                if config_path.exists():
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

    def _check_formatter_config(self, target_dir: Path, languages: set[str]) -> CheckResult:
        """Check if formatter configuration exists."""
        formatter_configs = {
            "python": ["pyproject.toml", ".black", "black.toml"],
            "javascript": [".prettierrc", ".prettierrc.json", ".prettierrc.js", ".prettierrc.yml", ".prettierrc.yaml", "prettier.config.js"],
            "go": ["__builtin__"],  # gofmt is built-in
            "rust": ["rustfmt.toml", ".rustfmt.toml"],
        }

        found_configs = []
        for lang in languages:
            if lang not in formatter_configs:
                continue

            # Special case for Go - gofmt is built-in
            if lang == "go":
                found_configs.append("gofmt (built-in)")
                continue

            for config_file in formatter_configs[lang]:
                config_path = target_dir / config_file
                if config_path.exists():
                    if config_file == "pyproject.toml":
                        content = config_path.read_text()
                        if "[tool.black]" in content or "[tool.ruff.format]" in content:
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

    def _check_precommit_hooks(self, target_dir: Path) -> CheckResult:
        """Check if pre-commit hooks are configured."""
        precommit_config = target_dir / ".pre-commit-config.yaml"

        if precommit_config.exists():
            return CheckResult(
                name="Has pre-commit hooks",
                passed=True,
                message="Found .pre-commit-config.yaml",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Has pre-commit hooks",
                passed=False,
                message="No pre-commit configuration found",
                severity=Severity.WARNING,
            )

    def _check_ci_integration(self, target_dir: Path) -> CheckResult:
        """Check if CI integration for linting/formatting exists."""
        ci_configs = [
            (".github/workflows", "GitHub Actions"),
            (".gitlab-ci.yml", "GitLab CI"),
            (".circleci/config.yml", "CircleCI"),
            ("azure-pipelines.yml", "Azure Pipelines"),
            (".travis.yml", "Travis CI"),
        ]

        found_ci = []
        for config_path, ci_name in ci_configs:
            full_path = target_dir / config_path
            if full_path.exists():
                found_ci.append(ci_name)

        if found_ci:
            return CheckResult(
                name="Has CI integration",
                passed=True,
                message=f"Found CI configuration: {', '.join(found_ci)}",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Has CI integration",
                passed=False,
                message="No CI integration found for style checks",
                severity=Severity.WARNING,
            )

    def _check_style_guide_docs(self, target_dir: Path) -> CheckResult:
        """Check if style guide documentation exists."""
        style_guide_files = [
            "STYLE_GUIDE.md",
            "STYLEGUIDE.md",
            "docs/STYLE_GUIDE.md",
            "docs/style-guide.md",
            "CONTRIBUTING.md",
        ]

        found_docs = []
        for doc_file in style_guide_files:
            doc_path = target_dir / doc_file
            if doc_path.exists():
                # For CONTRIBUTING.md, check if it has style guide content
                if "CONTRIBUTING" in doc_file:
                    content = doc_path.read_text().lower()
                    if "style" in content or "format" in content or "lint" in content:
                        found_docs.append(doc_file)
                else:
                    found_docs.append(doc_file)

        if found_docs:
            return CheckResult(
                name="Has style guide documentation",
                passed=True,
                message=f"Found style guide documentation: {', '.join(found_docs)}",
                severity=Severity.INFO,
            )
        else:
            return CheckResult(
                name="Has style guide documentation",
                passed=False,
                message="No style guide documentation found",
                severity=Severity.WARNING,
            )
