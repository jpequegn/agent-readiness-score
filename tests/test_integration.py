"""Integration tests for scanner and pillars."""

from pathlib import Path

from agent_readiness.pillars import StylePillar
from agent_readiness.scanner import Scanner


def test_scanner_with_style_pillar(tmp_path: Path) -> None:
    """Test Scanner integration with StylePillar."""
    # Setup: Python project with some features
    (tmp_path / "main.py").touch()
    (tmp_path / "ruff.toml").touch()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.black]\nline-length = 100\n")

    # Create scanner and register pillar
    scanner = Scanner()
    scanner.register_pillar(StylePillar())

    # Run scan
    result = scanner.scan(tmp_path)

    # Verify results
    assert result.target_directory == str(tmp_path.resolve())
    assert len(result.pillars) == 1
    assert result.pillars[0].name == "Style & Validation"
    # Note: Based on current implementation, we have 5 checks total
    assert len(result.pillars[0].checks) >= 5

    # Should have linter and formatter passing
    passed = sum(1 for c in result.pillars[0].checks if c.passed)
    assert passed >= 2  # at least linter and formatter

    # Overall score should be reasonable
    assert result.overall_score > 0
