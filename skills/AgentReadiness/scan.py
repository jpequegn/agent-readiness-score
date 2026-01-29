#!/usr/bin/env python3
"""
Clawdbot wrapper for agent-readiness scans.

Provides natural language output formatting for Clawdbot integration.
"""

import json
import sys
from pathlib import Path
from typing import Optional

try:
    from agent_readiness.scanner import Scanner
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
except ImportError:
    print("Error: agent-readiness-score not installed. Run: pip install agent-readiness-score")
    sys.exit(1)


def scan_repository(path: str = ".", format: str = "natural") -> dict:
    """
    Scan a repository for agent readiness.

    Args:
        path: Repository path to scan
        format: Output format ('natural', 'json', 'markdown')

    Returns:
        Scan results as dictionary
    """
    try:
        scanner = Scanner()
        # Register all pillars
        scanner.register_pillars([
            StylePillar(),
            BuildPillar(),
            TestingPillar(),
            DocumentationPillar(),
            DevEnvironmentPillar(),
            DebuggingObservabilityPillar(),
            SecurityPillar(),
            TaskDiscoveryPillar(),
        ])
        result = scanner.scan(Path(path))
        # Handle both ScanResult objects and plain dicts (for testing)
        result_dict = result.to_dict() if hasattr(result, 'to_dict') else result

        if format == "json":
            return result_dict
        elif format == "natural":
            return format_natural_output(result_dict)
        elif format == "markdown":
            return format_markdown_output(result_dict)
        else:
            return result_dict
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to scan repository at {path}"
        }


def format_natural_output(result: dict) -> dict:
    """Format scan results for natural language output."""
    if "error" in result:
        return result

    score = round(result.get("overall_score", 0))
    level = result.get("maturity_level", 1)
    summary = result.get("summary", {})

    # Create natural language summary
    level_names = {
        1: "Functional",
        2: "Documented",
        3: "Standardized",
        4: "Optimized",
        5: "Autonomous"
    }

    level_descriptions = {
        1: "agents struggle on this codebase",
        2: "agents can navigate, but with difficulty",
        3: "agents work productively ✅",
        4: "agents work highly effectively",
        5: "agents work autonomously with self-healing"
    }

    # Build pillar breakdown
    pillar_lines = []
    for pillar in result.get("pillars", []):
        pillar_score = round(pillar.get("score", 0))
        pillar_name = pillar.get("name", "Unknown")
        pillar_level = get_level_from_score(pillar_score)
        status = "✅" if pillar_level >= 3 else "⚠️"
        pillar_lines.append(
            f"  • {pillar_name}: {pillar_score}% (Level {pillar_level}) {status}"
        )

    # Get top failed checks for recommendations
    failed_checks = []
    for pillar in result.get("pillars", []):
        for check in pillar.get("checks", []):
            if not check.get("passed", False):
                failed_checks.append({
                    "pillar": pillar.get("name", ""),
                    "check": check.get("name", ""),
                    "message": check.get("message", ""),
                    "level": check.get("level", 1)
                })

    # Sort by level (higher is more important)
    failed_checks.sort(key=lambda x: x.get("level", 1), reverse=True)
    top_failed = failed_checks[:3]

    recommendations = []
    for item in top_failed:
        recommendations.append(f"  • {item['pillar']}: {item['check']}")

    # Format output
    output = {
        "summary": f"Agent Readiness: {score}% (Level {level} - {level_names.get(level, 'Unknown')})",
        "description": f"Your repository {level_descriptions.get(level, 'is at an unknown readiness level')}.",
        "score": score,
        "level": level,
        "level_name": level_names.get(level, "Unknown"),
        "pillars": "\n".join(pillar_lines),
        "recommendations": "\n".join(recommendations) if recommendations else "  • All major infrastructure is in place!",
        "stats": {
            "total_checks": summary.get("total_checks", 0),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "pass_rate": summary.get("pass_rate", "0%")
        }
    }

    return output


def format_markdown_output(result: dict) -> dict:
    """Format scan results as markdown."""
    if "error" in result:
        return result

    score = round(result.get("overall_score", 0))
    level = result.get("maturity_level", 1)

    lines = [
        "## 🦞 Agent Readiness Assessment",
        "",
        f"**Score:** {score}% | **Level:** {level}/5",
        "",
        "### Pillar Breakdown",
        ""
    ]

    for pillar in result.get("pillars", []):
        pillar_score = round(pillar.get("score", 0))
        pillar_level = get_level_from_score(pillar_score)
        passed = pillar.get("passed", 0)
        total = pillar.get("total", 0)
        lines.append(
            f"- **{pillar.get('name', 'Unknown')}**: {pillar_score}% "
            f"(Level {pillar_level}, {passed}/{total} checks)"
        )

    markdown = "\n".join(lines)

    return {
        "summary": "Markdown Report Generated",
        "markdown": markdown
    }


def get_level_from_score(score: float) -> int:
    """Determine maturity level from score percentage."""
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


def scan_pillar(path: str, pillar_name: str, format: str = "natural") -> dict:
    """
    Scan a specific pillar.

    Args:
        path: Repository path
        pillar_name: Name of pillar to scan
        format: Output format ('natural', 'json')

    Returns:
        Pillar scan results
    """
    try:
        scanner = Scanner()
        # Register all pillars
        scanner.register_pillars([
            StylePillar(),
            BuildPillar(),
            TestingPillar(),
            DocumentationPillar(),
            DevEnvironmentPillar(),
            DebuggingObservabilityPillar(),
            SecurityPillar(),
            TaskDiscoveryPillar(),
        ])
        result = scanner.scan(Path(path))
        # Handle both ScanResult objects and plain dicts (for testing)
        result_dict = result.to_dict() if hasattr(result, 'to_dict') else result

        # Find the pillar
        for pillar in result_dict.get("pillars", []):
            if pillar.get("name", "").lower() == pillar_name.lower():
                if format == "natural":
                    return format_pillar_natural(pillar)
                else:
                    return pillar

        return {"error": f"Pillar '{pillar_name}' not found"}
    except Exception as e:
        return {"error": str(e)}


def format_pillar_natural(pillar: dict) -> dict:
    """Format a single pillar for natural language."""
    pillar_score = round(pillar.get("score", 0))
    pillar_level = get_level_from_score(pillar_score)
    passed = pillar.get("passed", 0)
    total = pillar.get("total", 0)

    # Separate passed and failed checks
    passed_checks = [c for c in pillar.get("checks", []) if c.get("passed", False)]
    failed_checks = [c for c in pillar.get("checks", []) if not c.get("passed", False)]

    output = {
        "summary": f"{pillar.get('name', 'Unknown')} Pillar Assessment",
        "score": pillar_score,
        "level": pillar_level,
        "checks_passed": len(passed_checks),
        "checks_failed": len(failed_checks),
        "total_checks": total,
        "passed_checks": [f"  ✅ {c.get('name', '')}" for c in passed_checks],
        "failed_checks": [f"  ❌ {c.get('name', '')}: {c.get('message', '')}" for c in failed_checks]
    }

    return output


def get_recommendations(path: str) -> dict:
    """
    Get actionable recommendations for improvement.

    Args:
        path: Repository path

    Returns:
        Improvement recommendations
    """
    try:
        scanner = Scanner()
        # Register all pillars
        scanner.register_pillars([
            StylePillar(),
            BuildPillar(),
            TestingPillar(),
            DocumentationPillar(),
            DevEnvironmentPillar(),
            DebuggingObservabilityPillar(),
            SecurityPillar(),
            TaskDiscoveryPillar(),
        ])
        result = scanner.scan(Path(path))
        # Handle both ScanResult objects and plain dicts (for testing)
        result_dict = result.to_dict() if hasattr(result, 'to_dict') else result

        # Collect all failed checks
        failed_checks = []
        for pillar in result_dict.get("pillars", []):
            for check in pillar.get("checks", []):
                if not check.get("passed", False):
                    failed_checks.append({
                        "pillar": pillar.get("name", ""),
                        "check": check.get("name", ""),
                        "message": check.get("message", ""),
                        "level": check.get("level", 1),
                        "severity": check.get("severity", "warning")
                    })

        # Categorize by severity
        critical = [c for c in failed_checks if c.get("severity") == "critical"]
        errors = [c for c in failed_checks if c.get("severity") == "error"]
        warnings = [c for c in failed_checks if c.get("severity") == "warning"]

        recommendations = {
            "summary": "Improvement Recommendations",
            "total_issues": len(failed_checks),
            "critical": len(critical),
            "errors": len(errors),
            "warnings": len(warnings),
            "items": {
                "critical": [
                    f"  🔴 {c['pillar']}: {c['check']}"
                    for c in critical[:3]
                ],
                "errors": [
                    f"  🟠 {c['pillar']}: {c['check']}"
                    for c in errors[:3]
                ],
                "warnings": [
                    f"  🟡 {c['pillar']}: {c['check']}"
                    for c in warnings[:3]
                ]
            }
        }

        return recommendations
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agent Readiness Clawdbot Skill")
    parser.add_argument("path", nargs="?", default=".", help="Repository path to scan")
    parser.add_argument("--format", default="natural",
                       choices=["natural", "json", "markdown"],
                       help="Output format")
    parser.add_argument("--pillar", help="Scan specific pillar")
    parser.add_argument("--recommendations", action="store_true",
                       help="Get improvement recommendations")

    args = parser.parse_args()

    if args.recommendations:
        result = get_recommendations(args.path)
    elif args.pillar:
        result = scan_pillar(args.path, args.pillar, args.format)
    else:
        result = scan_repository(args.path, args.format)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Natural or markdown format - print formatted output
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            for key, value in result.items():
                if isinstance(value, list):
                    print("\n".join(value))
                elif isinstance(value, dict):
                    for k, v in value.items():
                        print(f"{k}: {v}")
                else:
                    print(f"{key}: {value}")
