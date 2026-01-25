"""Tests for Testing pillar."""

from pathlib import Path

from agent_readiness.pillars.testing import TestingPillar


def test_testing_pillar_name() -> None:
    """Test TestingPillar has correct name."""
    pillar = TestingPillar()
    assert pillar.name == "Testing"


def test_testing_pillar_weight() -> None:
    """Test TestingPillar has default weight."""
    pillar = TestingPillar()
    assert pillar.weight == 1.0
