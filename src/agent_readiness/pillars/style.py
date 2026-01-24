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
