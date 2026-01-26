"""Tests for Clawdbot AgentReadiness skill."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add skills to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "AgentReadiness"))

from scan import (
    format_natural_output,
    format_markdown_output,
    format_pillar_natural,
    get_level_from_score,
    get_recommendations,
)


# Sample scan result for testing
SAMPLE_RESULT = {
    "overall_score": 67.5,
    "maturity_level": 3,
    "summary": {
        "total_checks": 50,
        "passed": 35,
        "failed": 15,
        "pass_rate": "70%",
    },
    "pillars": [
        {
            "name": "Style & Validation",
            "score": 85.0,
            "passed": 8,
            "total": 10,
            "checks": [
                {
                    "name": "Linter configured",
                    "passed": True,
                    "message": "Found .ruff.toml",
                    "level": 1,
                    "severity": "warning",
                },
                {
                    "name": "Formatter configured",
                    "passed": True,
                    "message": "Found pyproject.toml with formatter config",
                    "level": 2,
                    "severity": "warning",
                },
                {
                    "name": "Pre-commit hooks",
                    "passed": False,
                    "message": "No .pre-commit-config.yaml found",
                    "level": 3,
                    "severity": "error",
                },
                {
                    "name": "CI linting",
                    "passed": True,
                    "message": "Linting runs in GitHub Actions",
                    "level": 3,
                    "severity": "warning",
                },
                {
                    "name": "Editor integration",
                    "passed": False,
                    "message": "No editor config found",
                    "level": 4,
                    "severity": "warning",
                },
            ],
        },
        {
            "name": "Testing",
            "score": 65.0,
            "passed": 6,
            "total": 10,
            "checks": [
                {
                    "name": "Tests exist",
                    "passed": True,
                    "message": "Found test files",
                    "level": 1,
                    "severity": "critical",
                },
                {
                    "name": "Test structure",
                    "passed": True,
                    "message": "Tests organized in tests/ directory",
                    "level": 2,
                    "severity": "warning",
                },
                {
                    "name": "Tests in CI",
                    "passed": True,
                    "message": "Tests run in GitHub Actions",
                    "level": 3,
                    "severity": "warning",
                },
                {
                    "name": "Coverage measured",
                    "passed": False,
                    "message": "No coverage tracking found",
                    "level": 3,
                    "severity": "error",
                },
                {
                    "name": "Coverage threshold",
                    "passed": False,
                    "message": "No coverage threshold configured",
                    "level": 4,
                    "severity": "error",
                },
            ],
        },
        {
            "name": "Documentation",
            "score": 55.0,
            "passed": 3,
            "total": 8,
            "checks": [
                {
                    "name": "README exists",
                    "passed": True,
                    "message": "README.md found",
                    "level": 1,
                    "severity": "warning",
                },
                {
                    "name": "AGENTS.md exists",
                    "passed": False,
                    "message": "No AGENTS.md found",
                    "level": 2,
                    "severity": "error",
                },
                {
                    "name": "API docs",
                    "passed": False,
                    "message": "No API documentation",
                    "level": 3,
                    "severity": "error",
                },
                {
                    "name": "Inline comments",
                    "passed": True,
                    "message": "Docstrings present in 60% of functions",
                    "level": 3,
                    "severity": "warning",
                },
            ],
        },
        {
            "name": "Build System",
            "score": 75.0,
            "passed": 7,
            "total": 10,
            "checks": [],
        },
        {
            "name": "Dev Environment",
            "score": 60.0,
            "passed": 5,
            "total": 10,
            "checks": [],
        },
        {
            "name": "Debugging & Observability",
            "score": 50.0,
            "passed": 4,
            "total": 10,
            "checks": [],
        },
        {
            "name": "Security",
            "score": 75.0,
            "passed": 7,
            "total": 10,
            "checks": [],
        },
        {
            "name": "Task Discovery",
            "score": 45.0,
            "passed": 3,
            "total": 8,
            "checks": [],
        },
    ],
}


class TestLevelFromScore:
    """Test score to level conversion."""

    def test_level_1(self):
        """Score below 40 should be Level 1."""
        assert get_level_from_score(30) == 1
        assert get_level_from_score(0) == 1

    def test_level_2(self):
        """Score 40-59 should be Level 2."""
        assert get_level_from_score(40) == 2
        assert get_level_from_score(50) == 2
        assert get_level_from_score(59) == 2

    def test_level_3(self):
        """Score 60-79 should be Level 3."""
        assert get_level_from_score(60) == 3
        assert get_level_from_score(70) == 3
        assert get_level_from_score(79) == 3

    def test_level_4(self):
        """Score 80-94 should be Level 4."""
        assert get_level_from_score(80) == 4
        assert get_level_from_score(90) == 4
        assert get_level_from_score(94) == 4

    def test_level_5(self):
        """Score 95+ should be Level 5."""
        assert get_level_from_score(95) == 5
        assert get_level_from_score(100) == 5


class TestFormatNaturalOutput:
    """Test natural language output formatting."""

    def test_format_with_valid_result(self):
        """Should format valid scan result."""
        output = format_natural_output(SAMPLE_RESULT)

        assert output["score"] == 68  # rounded from 67.5
        assert output["level"] == 3
        assert output["level_name"] == "Standardized"
        assert "Agent Readiness" in output["summary"]
        assert "pillars" in output
        assert "recommendations" in output

    def test_format_with_error(self):
        """Should pass through errors."""
        error_result = {"error": "Test error"}
        output = format_natural_output(error_result)
        assert "error" in output

    def test_pillars_in_output(self):
        """Should include all pillars in output."""
        output = format_natural_output(SAMPLE_RESULT)
        pillars_text = output["pillars"]

        assert "Style & Validation" in pillars_text
        assert "Testing" in pillars_text
        assert "Documentation" in pillars_text
        assert "Security" in pillars_text

    def test_status_indicators(self):
        """Should include status indicators for pillars."""
        output = format_natural_output(SAMPLE_RESULT)
        pillars_text = output["pillars"]

        # Level 3+ should have ✅, below should have ⚠️
        assert "85" in pillars_text  # Style has 85%
        assert "55" in pillars_text  # Documentation has 55%

    def test_statistics(self):
        """Should include scan statistics."""
        output = format_natural_output(SAMPLE_RESULT)
        stats = output["stats"]

        assert stats["total_checks"] == 50
        assert stats["passed"] == 35
        assert stats["failed"] == 15
        assert stats["pass_rate"] == "70%"

    def test_recommendations_included(self):
        """Should include top recommendations."""
        output = format_natural_output(SAMPLE_RESULT)
        recommendations = output["recommendations"]

        assert "AGENTS.md" in recommendations or len(recommendations) > 0


class TestFormatMarkdownOutput:
    """Test markdown output formatting."""

    def test_format_with_valid_result(self):
        """Should format valid result as markdown."""
        output = format_markdown_output(SAMPLE_RESULT)

        assert "markdown" in output
        assert "## 🦞 Agent Readiness Assessment" in output["markdown"]
        assert "68%" in output["markdown"]
        assert "Level 3" in output["markdown"]

    def test_markdown_includes_pillars(self):
        """Should include all pillars in markdown."""
        output = format_markdown_output(SAMPLE_RESULT)
        markdown = output["markdown"]

        for pillar in SAMPLE_RESULT["pillars"]:
            assert pillar["name"] in markdown

    def test_markdown_format_structure(self):
        """Should follow markdown format conventions."""
        output = format_markdown_output(SAMPLE_RESULT)
        markdown = output["markdown"]

        assert "##" in markdown
        assert "**" in markdown  # Bold formatting
        assert "-" in markdown   # List items


class TestFormatPillarNatural:
    """Test pillar formatting."""

    def test_format_pillar(self):
        """Should format pillar information."""
        pillar = SAMPLE_RESULT["pillars"][0]  # Style & Validation
        output = format_pillar_natural(pillar)

        assert output["score"] == 85
        assert output["level"] == 4
        assert output["checks_passed"] == 3
        assert output["checks_failed"] == 2
        assert output["total_checks"] == 10

    def test_pillar_includes_checks(self):
        """Should include passed and failed checks."""
        pillar = SAMPLE_RESULT["pillars"][0]
        output = format_pillar_natural(pillar)

        assert len(output["passed_checks"]) > 0
        assert len(output["failed_checks"]) > 0

    def test_pillar_check_formatting(self):
        """Should format checks with proper indicators."""
        pillar = SAMPLE_RESULT["pillars"][0]
        output = format_pillar_natural(pillar)

        # Check for status indicators
        passed_text = "\n".join(output["passed_checks"])
        failed_text = "\n".join(output["failed_checks"])

        assert "✅" in passed_text
        assert "❌" in failed_text


class TestGetRecommendations:
    """Test recommendation generation."""

    @patch("scan.Scanner")
    def test_get_recommendations(self, mock_scanner_class):
        """Should generate recommendations from scan."""
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = SAMPLE_RESULT
        mock_scanner_class.return_value = mock_scanner

        recommendations = get_recommendations(".")

        assert "summary" in recommendations
        assert "total_issues" in recommendations
        assert "critical" in recommendations["items"]
        assert "errors" in recommendations["items"]
        assert "warnings" in recommendations["items"]

    @patch("scan.Scanner")
    def test_recommendations_categorization(self, mock_scanner_class):
        """Should categorize recommendations by severity."""
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = SAMPLE_RESULT
        mock_scanner_class.return_value = mock_scanner

        recommendations = get_recommendations(".")

        # Should have error-level recommendations
        assert recommendations["errors"] > 0


class TestSkillIntegration:
    """Integration tests for the skill."""

    @patch("scan.Scanner")
    def test_scan_repository_natural_format(self, mock_scanner_class):
        """Should scan repository with natural format."""
        from scan import scan_repository

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = SAMPLE_RESULT
        mock_scanner_class.return_value = mock_scanner

        result = scan_repository(".", format="natural")

        assert result["score"] == 68
        assert result["level"] == 3
        assert "pillars" in result

    @patch("scan.Scanner")
    def test_scan_repository_json_format(self, mock_scanner_class):
        """Should scan repository with JSON format."""
        from scan import scan_repository

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = SAMPLE_RESULT
        mock_scanner_class.return_value = mock_scanner

        result = scan_repository(".", format="json")

        # Should return raw result for JSON format
        assert result == SAMPLE_RESULT

    @patch("scan.Scanner")
    def test_scan_repository_markdown_format(self, mock_scanner_class):
        """Should scan repository with markdown format."""
        from scan import scan_repository

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = SAMPLE_RESULT
        mock_scanner_class.return_value = mock_scanner

        result = scan_repository(".", format="markdown")

        assert "markdown" in result or "summary" in result

    @patch("scan.Scanner")
    def test_scan_pillar_specific(self, mock_scanner_class):
        """Should scan specific pillar."""
        from scan import scan_pillar

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = SAMPLE_RESULT
        mock_scanner_class.return_value = mock_scanner

        result = scan_pillar(".", "Style & Validation", format="natural")

        assert "score" in result
        assert result["score"] == 85

    @patch("scan.Scanner")
    def test_scan_error_handling(self, mock_scanner_class):
        """Should handle scan errors."""
        from scan import scan_repository

        mock_scanner_class.side_effect = Exception("Scan failed")

        result = scan_repository(".", format="natural")

        assert "error" in result


class TestClawdbotOutputFormat:
    """Test Clawdbot-specific output formatting."""

    def test_natural_output_for_clawdbot(self):
        """Output should be Clawdbot-friendly."""
        output = format_natural_output(SAMPLE_RESULT)

        # Should have human-readable format
        assert "score" in output
        assert "level" in output
        assert "summary" in output
        assert "description" in output

    def test_pillar_breakdown_readability(self):
        """Pillar breakdown should be easy to read."""
        output = format_natural_output(SAMPLE_RESULT)
        pillars = output["pillars"]

        # Should use emoji and clear formatting
        assert "%" in pillars
        assert "Level" in pillars or "level" in pillars.lower()

    def test_recommendations_actionable(self):
        """Recommendations should be actionable."""
        output = format_natural_output(SAMPLE_RESULT)
        recommendations = output["recommendations"]

        # Should suggest specific actions or improvements
        assert len(recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
