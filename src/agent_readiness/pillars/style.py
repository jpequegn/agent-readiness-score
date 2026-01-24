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
