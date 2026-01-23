"""Quick test of core scanning framework."""

from pathlib import Path

from agent_readiness import CheckResult, Pillar, Scanner
from agent_readiness.models import Severity


class DemoPillar(Pillar):
    """Demo pillar to test the framework."""

    @property
    def name(self) -> str:
        return "Demo Pillar"

    @property
    def weight(self) -> float:
        return 1.0

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Run some demo checks."""
        return [
            CheckResult(
                name="Has README",
                passed=(target_dir / "README.md").exists(),
                message="Project has README.md file",
                severity=Severity.WARNING,
            ),
            CheckResult(
                name="Has pyproject.toml",
                passed=(target_dir / "pyproject.toml").exists(),
                message="Project has pyproject.toml file",
                severity=Severity.ERROR,
            ),
        ]


def main() -> None:
    """Test the core framework."""
    print("Testing Agent Readiness Score Core Framework\n")

    # Create scanner and register demo pillar
    scanner = Scanner()
    scanner.register_pillar(DemoPillar())

    # Scan current directory
    result = scanner.scan(".")

    # Display results
    print(f"Target: {result.target_directory}")
    print(f"Overall Score: {result.overall_score:.1f}%")
    print(f"Maturity Level: {result.maturity_level} - {result.get_maturity_label()}")
    print()

    for pillar in result.pillars:
        print(f"Pillar: {pillar.name}")
        print(f"Score: {pillar.score:.1f}%")
        print(f"Checks: {len(pillar.checks)} total")
        for check in pillar.checks:
            status = "✓" if check.passed else "✗"
            print(f"  {status} {check.name}: {check.message}")
        print()

    # Test JSON output
    import json

    print("JSON Output:")
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
