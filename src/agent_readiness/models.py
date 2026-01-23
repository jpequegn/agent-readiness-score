"""Core data models for the agent readiness scoring system."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    """Check severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CheckResult:
    """Result of a single check within a pillar.

    Attributes:
        name: Human-readable name of the check
        passed: Whether the check passed
        message: Explanation of the result
        severity: Severity level if the check failed
        metadata: Additional contextual information
    """

    name: str
    passed: bool
    message: str
    severity: Severity = Severity.INFO
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity.value,
            "metadata": self.metadata,
        }


@dataclass
class PillarResult:
    """Results from evaluating a single pillar.

    Attributes:
        name: Name of the pillar
        checks: List of individual check results
        score: Percentage of checks passed (0-100)
        weight: Weight of this pillar in overall scoring (default 1.0)
    """

    name: str
    checks: list[CheckResult]
    score: float
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "checks": [check.to_dict() for check in self.checks],
            "score": self.score,
            "weight": self.weight,
            "passed": sum(1 for c in self.checks if c.passed),
            "failed": sum(1 for c in self.checks if not c.passed),
            "total": len(self.checks),
        }


@dataclass
class ScanResult:
    """Complete scan results across all pillars.

    Attributes:
        pillars: Results from each pillar
        overall_score: Weighted average score across all pillars (0-100)
        maturity_level: Maturity level based on score (1-5)
        target_directory: Directory that was scanned
    """

    pillars: list[PillarResult]
    overall_score: float
    maturity_level: int
    target_directory: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        total_checks = sum(len(p.checks) for p in self.pillars)
        passed_checks = sum(sum(1 for c in p.checks if c.passed) for p in self.pillars)
        failed_checks = total_checks - passed_checks

        return {
            "target_directory": self.target_directory,
            "overall_score": self.overall_score,
            "maturity_level": self.maturity_level,
            "summary": {
                "total_checks": total_checks,
                "passed": passed_checks,
                "failed": failed_checks,
                "pass_rate": f"{(passed_checks / total_checks * 100) if total_checks > 0 else 0:.1f}%",
            },
            "pillars": [pillar.to_dict() for pillar in self.pillars],
        }

    def get_maturity_label(self) -> str:
        """Get human-readable maturity level label."""
        labels = {
            1: "Initial - Ad-hoc processes",
            2: "Developing - Basic processes in place",
            3: "Defined - Documented and standardized",
            4: "Managed - Measured and controlled",
            5: "Optimizing - Continuous improvement",
        }
        return labels.get(self.maturity_level, "Unknown")
