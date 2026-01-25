"""Testing pillar implementation."""

from pathlib import Path

from agent_readiness.pillar import Pillar
from agent_readiness.models import CheckResult


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
