"""Base pillar class that all evaluation pillars inherit from."""

from abc import ABC, abstractmethod
from pathlib import Path

from .models import CheckResult, PillarResult


class Pillar(ABC):
    """Abstract base class for all evaluation pillars.

    Each pillar represents a category of checks (e.g., testing, documentation, error handling).
    Pillars are discovered and loaded dynamically by the scanner.

    Subclasses must implement:
        - name: Property returning the pillar name
        - weight: Property returning the pillar weight (default 1.0)
        - evaluate: Method that runs checks and returns results
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this pillar."""
        pass

    @property
    def weight(self) -> float:
        """Weight of this pillar in overall scoring (default 1.0).

        Override this to give certain pillars more importance.
        For example, a security pillar might have weight 2.0.
        """
        return 1.0

    @abstractmethod
    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory against this pillar's checks.

        Args:
            target_dir: Path to the directory to evaluate

        Returns:
            List of CheckResult objects, one per check performed
        """
        pass

    def run(self, target_dir: Path) -> PillarResult:
        """Execute pillar evaluation and calculate score.

        This is the main entry point called by the scanner.
        It runs the checks, calculates the score, and wraps everything
        in a PillarResult object.

        Args:
            target_dir: Path to the directory to evaluate

        Returns:
            PillarResult with checks and calculated score
        """
        checks = self.evaluate(target_dir)

        # Calculate score as percentage of checks passed
        if not checks:
            score = 100.0  # No checks means perfect score
        else:
            passed = sum(1 for check in checks if check.passed)
            score = (passed / len(checks)) * 100

        return PillarResult(
            name=self.name,
            checks=checks,
            score=score,
            weight=self.weight,
        )
