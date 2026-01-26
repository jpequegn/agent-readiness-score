"""Command-line interface for agent-readiness-score."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from agent_readiness.pillars import (
    BuildPillar,
    DebuggingObservabilityPillar,
    DevEnvironmentPillar,
    DocumentationPillar,
    SecurityPillar,
    StylePillar,
    TaskDiscoveryPillar,
    TestingPillar,
)
from agent_readiness.scanner import Scanner

console = Console()


def get_all_pillars() -> list:
    """Get all available pillars."""
    return [
        StylePillar(),
        BuildPillar(),
        TestingPillar(),
        DocumentationPillar(),
        DevEnvironmentPillar(),
        DebuggingObservabilityPillar(),
        SecurityPillar(),
        TaskDiscoveryPillar(),
    ]


def get_pillar_by_name(name: str):
    """Get a specific pillar by name."""
    pillars = get_all_pillars()
    for pillar in pillars:
        if pillar.name.lower() == name.lower():
            return pillar
    raise ValueError(f"Unknown pillar: {name}")


def format_json_output(result) -> str:
    """Format scan result as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def format_markdown_output(result) -> str:
    """Format scan result as Markdown report."""
    lines = [
        "# Agent Readiness Score Report",
        "",
        f"**Repository:** {result.target_directory}",
        f"**Overall Score:** {result.overall_score:.0f}% (Level {result.maturity_level})",
        f"**Maturity:** {result.get_maturity_label()}",
        "",
        "## Pillar Scores",
        "",
    ]

    # Add pillar table
    lines.append("| Pillar | Score | Level | Passed |")
    lines.append("|--------|-------|-------|--------|")

    for pillar in result.pillars:
        passed = sum(1 for c in pillar.checks if c.passed)
        total = len(pillar.checks)
        lines.append(
            f"| {pillar.name} | {pillar.score:.0f}% | {_get_level_from_score(pillar.score)} | "
            f"{passed}/{total} |"
        )

    lines.append("")
    lines.append("## Check Results")
    lines.append("")

    # Add detailed checks by level
    for level in range(1, 6):
        level_checks = []
        for pillar in result.pillars:
            level_checks.extend(
                [(pillar.name, check) for check in pillar.checks if check.level == level]
            )

        if not level_checks:
            continue

        level_names = [
            "Initial - Ad-hoc",
            "Developing - Basic",
            "Defined - Standardized",
            "Managed - Measured",
            "Optimizing - Improvement",
        ]

        lines.append(f"### Level {level}: {level_names[level - 1]}")
        lines.append("")

        for pillar_name, check in level_checks:
            status = "✅" if check.passed else "❌"
            lines.append(
                f"{status} **{pillar_name}:** {check.name} - {check.message}"
            )

        lines.append("")

    return "\n".join(lines)


def _get_level_from_score(score: float) -> int:
    """Determine level from score."""
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


def format_level_indicator(level: int) -> str:
    """Create a visual level indicator."""
    filled = "█" * level
    empty = "░" * (5 - level)
    return filled + empty


@click.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--format",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Output format",
)
@click.option("--pillar", help="Run only a specific pillar (e.g., 'Style & Validation')")
@click.option("--level", type=int, help="Show only checks for a specific level (1-5)")
@click.option("--quiet", is_flag=True, help="Suppress output, only exit code")
def main(path: str, format: str, pillar: str, level: int, quiet: bool) -> None:
    """Scan a directory for agent readiness."""
    try:
        target_path = Path(path).resolve()

        # Initialize scanner
        scanner = Scanner()

        # Register pillars
        if pillar:
            try:
                selected_pillar = get_pillar_by_name(pillar)
                scanner.register_pillar(selected_pillar)
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
        else:
            scanner.register_pillars(get_all_pillars())

        # Run scan with progress indicator
        if not quiet:
            if format == "text":
                with Progress() as progress:
                    task = progress.add_task(
                        "[cyan]Scanning repository...", total=None
                    )
                    result = scanner.scan(target_path)
                    progress.stop()
            else:
                result = scanner.scan(target_path)
        else:
            result = scanner.scan(target_path)

        # Filter by level if specified
        if level and 1 <= level <= 5:
            for pillar_result in result.pillars:
                pillar_result.checks = [c for c in pillar_result.checks if c.level == level]

        # Output results
        if format == "json":
            # Use raw print for JSON to avoid ANSI codes
            print(format_json_output(result))
        elif format == "markdown":
            # Use raw print for Markdown to avoid ANSI codes
            print(format_markdown_output(result))
        else:
            # Pretty text output
            if not quiet:
                _print_text_report(result)

        # Set exit code based on maturity level
        # 0 = Level 3+, 1 = Below Level 3
        exit_code = 0 if result.maturity_level >= 3 else 1
        sys.exit(exit_code)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


def _print_text_report(result) -> None:
    """Print formatted text report with rich."""
    # Header
    console.print()
    console.print("[bold cyan]🦞 Agent Readiness Score[/bold cyan]")
    console.print()

    console.print(f"[bold]Repository:[/bold] {result.target_directory}")
    console.print(
        f"[bold]Overall Score:[/bold] [bold cyan]{result.overall_score:.0f}%[/bold cyan] "
        f"(Level {result.maturity_level})"
    )
    console.print(f"[bold]Maturity:[/bold] {result.get_maturity_label()}")
    console.print()

    # Pillar scores table
    table = Table(title="Pillar Scores", show_header=True, header_style="bold")
    table.add_column("Pillar", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Level", justify="center")
    table.add_column("Progress", justify="left")
    table.add_column("Checks", justify="right")

    for pillar in result.pillars:
        passed = sum(1 for c in pillar.checks if c.passed)
        total = len(pillar.checks)
        level = _get_level_from_score(pillar.score)

        # Color code based on score
        if pillar.score >= 80:
            score_color = "green"
        elif pillar.score >= 60:
            score_color = "yellow"
        else:
            score_color = "red"

        score_text = f"[{score_color}]{pillar.score:.0f}%[/{score_color}]"
        level_text = format_level_indicator(level)

        table.add_row(
            pillar.name,
            score_text,
            str(level),
            level_text,
            f"{passed}/{total}",
        )

    console.print(table)
    console.print()

    # Failed checks summary
    all_failed_checks = []
    for pillar in result.pillars:
        for check in pillar.checks:
            if not check.passed:
                all_failed_checks.append((pillar.name, check))

    if all_failed_checks:
        console.print("[bold red]Failed Checks:[/bold red]")
        for pillar_name, check in all_failed_checks[:10]:  # Show first 10
            console.print(f"  ❌ [{pillar_name}] {check.name}: {check.message}")

        if len(all_failed_checks) > 10:
            console.print(f"  ... and {len(all_failed_checks) - 10} more")
        console.print()

    # Recommendations
    recommendations = _generate_recommendations(result)
    if recommendations:
        console.print("[bold yellow]Recommendations:[/bold yellow]")
        for i, rec in enumerate(recommendations[:5], 1):
            console.print(f"  {i}. {rec}")
        console.print()


def _generate_recommendations(result) -> list[str]:
    """Generate recommendations based on scan results."""
    recommendations = []

    for pillar in result.pillars:
        failed_checks = [c for c in pillar.checks if not c.passed]
        if failed_checks:
            # Group by severity
            critical = [c for c in failed_checks if c.severity.value == "critical"]
            required = [
                c
                for c in failed_checks
                if c.severity.value in ("required", "error")
            ]

            if critical:
                recommendations.append(
                    f"[{pillar.name}] Address {len(critical)} critical issues"
                )
            elif required:
                recommendations.append(
                    f"[{pillar.name}] Implement {len(required)} required checks"
                )
            else:
                recommendations.append(
                    f"[{pillar.name}] Consider {len(failed_checks)} improvements"
                )

    return recommendations


if __name__ == "__main__":
    main()
