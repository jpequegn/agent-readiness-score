"""Tests for Build System pillar."""



from agent_readiness.pillars.build import BuildPillar


def test_build_pillar_name() -> None:
    """Test BuildPillar has correct name."""
    pillar = BuildPillar()
    assert pillar.name == "Build System"


def test_build_pillar_weight() -> None:
    """Test BuildPillar has default weight."""
    pillar = BuildPillar()
    assert pillar.weight == 1.0
