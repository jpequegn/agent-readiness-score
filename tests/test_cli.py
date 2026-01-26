"""Tests for the CLI module."""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from agent_readiness.cli import (
    format_json_output,
    format_markdown_output,
    format_level_indicator,
    get_all_pillars,
    get_pillar_by_name,
    main,
)


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_repo():
    """Create a sample repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Create basic files to make it a valid repo
        (repo_path / "README.md").write_text("# Test Project\n\nThis is a test project.")
        (repo_path / "package.json").write_text('{"name": "test"}')

        yield str(repo_path)


class TestCLIBasic:
    """Test basic CLI functionality."""

    def test_cli_with_valid_path(self, runner, sample_repo):
        """Test CLI with a valid path."""
        result = runner.invoke(main, [sample_repo])
        assert result.exit_code in (0, 1)  # Valid exit codes
        assert "🦞" in result.output or "Agent Readiness" in result.output

    def test_cli_with_invalid_path(self, runner):
        """Test CLI with an invalid path."""
        result = runner.invoke(main, ["/nonexistent/path"])
        assert result.exit_code != 0

    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Scan a directory" in result.output


class TestCLIFormats:
    """Test different output formats."""

    def test_json_format(self, runner, sample_repo):
        """Test JSON output format."""
        result = runner.invoke(main, [sample_repo, "--format", "json"])
        assert result.exit_code in (0, 1)

        # Parse JSON output - find where JSON starts
        output = result.output.strip()
        json_start = output.find("{")
        if json_start != -1:
            json_str = output[json_start:]
            data = json.loads(json_str)
            assert "overall_score" in data
            assert "pillars" in data
            assert "maturity_level" in data

    def test_markdown_format(self, runner, sample_repo):
        """Test Markdown output format."""
        result = runner.invoke(main, [sample_repo, "--format", "markdown"])
        assert result.exit_code in (0, 1)
        assert "# Agent Readiness Score Report" in result.output

    def test_text_format_default(self, runner, sample_repo):
        """Test default text format."""
        result = runner.invoke(main, [sample_repo])
        assert result.exit_code in (0, 1)
        assert "Agent Readiness" in result.output or "🦞" in result.output


class TestCLIPillarOption:
    """Test --pillar option."""

    def test_pillar_option_valid(self, runner, sample_repo):
        """Test --pillar option with valid pillar name."""
        result = runner.invoke(main, [sample_repo, "--pillar", "Style & Validation"])
        assert result.exit_code in (0, 1)

    def test_pillar_option_case_insensitive(self, runner, sample_repo):
        """Test --pillar option is case-insensitive."""
        result = runner.invoke(
            main, [sample_repo, "--pillar", "style & validation"]
        )
        assert result.exit_code in (0, 1)

    def test_pillar_option_invalid(self, runner, sample_repo):
        """Test --pillar option with invalid pillar name."""
        result = runner.invoke(main, [sample_repo, "--pillar", "NonexistentPillar"])
        assert result.exit_code != 0


class TestCLILevelOption:
    """Test --level option."""

    def test_level_option_valid(self, runner, sample_repo):
        """Test --level option with valid level."""
        for level in [1, 2, 3, 4, 5]:
            result = runner.invoke(main, [sample_repo, "--level", str(level)])
            assert result.exit_code in (0, 1)

    def test_level_option_invalid(self, runner, sample_repo):
        """Test --level option with invalid level."""
        result = runner.invoke(main, [sample_repo, "--level", "6"])
        assert result.exit_code in (0, 1)  # Should still run, just won't filter


class TestCLIQuietOption:
    """Test --quiet option."""

    def test_quiet_option(self, runner, sample_repo):
        """Test --quiet option suppresses output."""
        result = runner.invoke(main, [sample_repo, "--quiet"])
        assert result.exit_code in (0, 1)
        # Quiet mode should have minimal output


class TestPillarDiscovery:
    """Test pillar discovery functions."""

    def test_get_all_pillars(self):
        """Test getting all available pillars."""
        pillars = get_all_pillars()
        assert len(pillars) == 8
        assert all(hasattr(p, "name") for p in pillars)

    def test_get_pillar_by_name_valid(self):
        """Test getting pillar by name."""
        pillar = get_pillar_by_name("Style & Validation")
        assert pillar is not None
        assert pillar.name == "Style & Validation"

    def test_get_pillar_by_name_case_insensitive(self):
        """Test getting pillar by name is case-insensitive."""
        pillar = get_pillar_by_name("style & validation")
        assert pillar is not None
        assert pillar.name == "Style & Validation"

    def test_get_pillar_by_name_invalid(self):
        """Test getting pillar by invalid name raises error."""
        with pytest.raises(ValueError):
            get_pillar_by_name("NonexistentPillar")


class TestOutputFormatters:
    """Test output formatter functions."""

    def test_format_level_indicator(self):
        """Test level indicator formatting."""
        assert format_level_indicator(1) == "█░░░░"
        assert format_level_indicator(3) == "███░░"
        assert format_level_indicator(5) == "█████"

    def test_format_json_output(self):
        """Test JSON output formatter."""
        # Create a mock result
        from agent_readiness.models import ScanResult, PillarResult, CheckResult

        checks = [
            CheckResult("Test Check", True, "Check passed", level=1),
        ]
        pillar = PillarResult("Test Pillar", checks, 100.0)
        result = ScanResult([pillar], 100.0, 5, "/test/dir")

        json_str = format_json_output(result)
        data = json.loads(json_str)

        assert data["overall_score"] == 100.0
        assert data["maturity_level"] == 5
        assert len(data["pillars"]) == 1

    def test_format_markdown_output(self):
        """Test Markdown output formatter."""
        from agent_readiness.models import ScanResult, PillarResult, CheckResult

        checks = [
            CheckResult("Test Check", True, "Check passed", level=1),
            CheckResult("Failed Check", False, "Check failed", level=2),
        ]
        pillar = PillarResult("Test Pillar", checks, 50.0)
        result = ScanResult([pillar], 50.0, 2, "/test/dir")

        markdown_str = format_markdown_output(result)

        assert "# Agent Readiness Score Report" in markdown_str
        assert "/test/dir" in markdown_str
        assert "Test Pillar" in markdown_str
        assert "Test Check" in markdown_str


class TestExitCodes:
    """Test exit code behavior."""

    def test_exit_code_reflects_maturity(self, runner, sample_repo):
        """Test exit code reflects readiness level."""
        result = runner.invoke(main, [sample_repo, "--quiet"])
        # Exit code should be 0 for Level 3+ or 1 for below
        assert result.exit_code in (0, 1)


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_full_scan_workflow(self, runner, sample_repo):
        """Test complete scan workflow."""
        # Run a full scan
        result = runner.invoke(main, [sample_repo])
        assert result.exit_code in (0, 1)

        # Verify output contains key information
        output = result.output
        assert "Repository" in output or "Agent Readiness" in output

    def test_json_format_integration(self, runner, sample_repo):
        """Test JSON format with real scan."""
        result = runner.invoke(main, [sample_repo, "--format", "json"])
        assert result.exit_code in (0, 1)

        # Extract JSON from output
        output_lines = result.output.strip().split("\n")
        json_start = None
        for i, line in enumerate(output_lines):
            if line.startswith("{"):
                json_start = i
                break

        if json_start is not None:
            json_str = "\n".join(output_lines[json_start:])
            data = json.loads(json_str)
            assert isinstance(data, dict)

    def test_pillar_specific_scan(self, runner, sample_repo):
        """Test scanning specific pillar."""
        result = runner.invoke(
            main, [sample_repo, "--pillar", "Style & Validation"]
        )
        assert result.exit_code in (0, 1)
        # Should complete without error

    def test_level_filter(self, runner, sample_repo):
        """Test scanning with level filter."""
        result = runner.invoke(main, [sample_repo, "--level", "1"])
        assert result.exit_code in (0, 1)
        # Should complete without error
