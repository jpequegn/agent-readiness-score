"""Scanner orchestration class that runs all pillars and aggregates results."""

from pathlib import Path

from .models import ScanResult
from .pillar import Pillar


class Scanner:
    """Orchestrates pillar evaluation and aggregates results.

    The scanner is responsible for:
    - Managing registered pillars
    - Running all pillars against a target directory
    - Calculating weighted overall score
    - Determining maturity level
    - Producing structured results
    """

    def __init__(self) -> None:
        """Initialize scanner with empty pillar registry."""
        self._pillars: list[Pillar] = []

    def register_pillar(self, pillar: Pillar) -> None:
        """Register a pillar for evaluation.

        Args:
            pillar: Pillar instance to register
        """
        self._pillars.append(pillar)

    def register_pillars(self, pillars: list[Pillar]) -> None:
        """Register multiple pillars at once.

        Args:
            pillars: List of pillar instances to register
        """
        self._pillars.extend(pillars)

    def scan(self, target_dir: str | Path) -> ScanResult:
        """Scan a directory with all registered pillars.

        Args:
            target_dir: Path to directory to scan

        Returns:
            ScanResult with all pillar results, overall score, and maturity level

        Raises:
            ValueError: If no pillars are registered
            FileNotFoundError: If target directory doesn't exist
        """
        if not self._pillars:
            raise ValueError("No pillars registered. Use register_pillar() to add pillars.")

        target_path = Path(target_dir)
        if not target_path.exists():
            raise FileNotFoundError(f"Target directory does not exist: {target_dir}")
        if not target_path.is_dir():
            raise ValueError(f"Target path is not a directory: {target_dir}")

        # Run all pillars
        pillar_results = [pillar.run(target_path) for pillar in self._pillars]

        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(pillar_results)

        # Determine maturity level
        maturity_level = self._determine_maturity_level(overall_score)

        return ScanResult(
            pillars=pillar_results,
            overall_score=overall_score,
            maturity_level=maturity_level,
            target_directory=str(target_path.resolve()),
        )

    def _calculate_overall_score(self, pillar_results: list) -> float:
        """Calculate weighted average score across all pillars.

        Args:
            pillar_results: List of PillarResult objects

        Returns:
            Weighted average score (0-100)
        """
        if not pillar_results:
            return 0.0

        total_weight = sum(p.weight for p in pillar_results)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(p.score * p.weight for p in pillar_results)
        return weighted_sum / total_weight

    def _determine_maturity_level(self, score: float) -> int:
        """Determine maturity level (1-5) based on overall score.

        Maturity levels:
        - Level 1 (Initial):      0-39%   - Ad-hoc, unpredictable processes
        - Level 2 (Developing):   40-59%  - Basic processes in place
        - Level 3 (Defined):      60-79%  - Documented and standardized
        - Level 4 (Managed):      80-94%  - Measured and controlled
        - Level 5 (Optimizing):   95-100% - Continuous improvement

        Args:
            score: Overall score (0-100)

        Returns:
            Maturity level (1-5)
        """
        if score < 40:
            return 1
        elif score < 60:
            return 2
        elif score < 80:
            return 3
        elif score < 95:
            return 4
        else:
            return 5
