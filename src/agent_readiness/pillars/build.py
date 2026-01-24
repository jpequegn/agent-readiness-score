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
