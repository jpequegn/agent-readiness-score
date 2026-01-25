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
