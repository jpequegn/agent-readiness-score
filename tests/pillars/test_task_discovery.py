"""Tests for the Task Discovery pillar."""

from pathlib import Path

import pytest

from agent_readiness.models import Severity
from agent_readiness.pillars.task_discovery import TaskDiscoveryPillar


@pytest.fixture
def task_discovery_pillar():
    """Create a TaskDiscoveryPillar instance."""
    return TaskDiscoveryPillar()


def test_task_discovery_pillar_name(task_discovery_pillar):
    """Test that the pillar has the correct name."""
    assert task_discovery_pillar.name == "Task Discovery"


def test_task_discovery_pillar_weight(task_discovery_pillar):
    """Test that the pillar has the correct weight."""
    assert task_discovery_pillar.weight == 1.0


def test_discover_task_infrastructure_empty(tmp_path, task_discovery_pillar):
    """Test discovery with empty directory."""
    result = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    assert result["has_github_issues"] is False
    assert result["has_contributing_guide"] is False
    assert result["has_issue_templates"] is False


def test_discover_task_infrastructure_with_github(tmp_path, task_discovery_pillar):
    """Test discovery with GitHub directory."""
    (tmp_path / ".github").mkdir()
    result = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    assert result["has_github_issues"] is True


def test_discover_task_infrastructure_with_contributing(tmp_path, task_discovery_pillar):
    """Test discovery with CONTRIBUTING.md."""
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing")
    result = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    assert result["has_contributing_guide"] is True


# Level 1 Tests

def test_check_issue_tracker_present_found(tmp_path, task_discovery_pillar):
    """Test issue tracker detection when present."""
    (tmp_path / ".github").mkdir()
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issue_tracker_present(tmp_path, task)
    assert result.passed is True
    assert "configured" in result.message.lower()


def test_check_issue_tracker_present_not_found(tmp_path, task_discovery_pillar):
    """Test issue tracker detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issue_tracker_present(tmp_path, task)
    assert result.passed is False


def test_check_contributing_guide_exists_found(tmp_path, task_discovery_pillar):
    """Test contributing guide detection when present."""
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_contributing_guide_exists(tmp_path, task)
    assert result.passed is True


def test_check_contributing_guide_exists_not_found(tmp_path, task_discovery_pillar):
    """Test contributing guide detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_contributing_guide_exists(tmp_path, task)
    assert result.passed is False


# Level 2 Tests

def test_check_readme_contribution_section_found(tmp_path, task_discovery_pillar):
    """Test README contribution section detection."""
    (tmp_path / "README.md").write_text("# Project\n\nContributing is welcome.")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_readme_contribution_section(tmp_path, task)
    assert result.passed is True


def test_check_readme_contribution_section_not_found(tmp_path, task_discovery_pillar):
    """Test README contribution section detection when absent."""
    (tmp_path / "README.md").write_text("# Project")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_readme_contribution_section(tmp_path, task)
    assert result.passed is False


def test_check_issues_labeled_found(tmp_path, task_discovery_pillar):
    """Test issues labeled detection."""
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "labels.json").write_text("{}")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issues_labeled(tmp_path, task)
    assert result.passed is True


def test_check_issues_labeled_not_found(tmp_path, task_discovery_pillar):
    """Test issues labeled detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issues_labeled(tmp_path, task)
    assert result.passed is False


def test_check_roadmap_visible_found(tmp_path, task_discovery_pillar):
    """Test roadmap visibility detection."""
    (tmp_path / "ROADMAP.md").write_text("# Roadmap")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_roadmap_visible(tmp_path, task)
    assert result.passed is True


def test_check_roadmap_visible_in_readme(tmp_path, task_discovery_pillar):
    """Test roadmap visibility in README."""
    (tmp_path / "README.md").write_text("# Project\n\nOur roadmap includes...")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_roadmap_visible(tmp_path, task)
    assert result.passed is True


def test_check_roadmap_visible_not_found(tmp_path, task_discovery_pillar):
    """Test roadmap visibility detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_roadmap_visible(tmp_path, task)
    assert result.passed is False


def test_check_good_first_issues_marked_in_contributing(tmp_path, task_discovery_pillar):
    """Test good-first-issue detection in CONTRIBUTING."""
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\nLook for good-first-issue labels."
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_good_first_issues_marked(tmp_path, task)
    assert result.passed is True


def test_check_good_first_issues_marked_in_readme(tmp_path, task_discovery_pillar):
    """Test good-first-issue detection in README."""
    (tmp_path / "README.md").write_text(
        "# Project\n\nCheck beginner-friendly issues to start."
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_good_first_issues_marked(tmp_path, task)
    assert result.passed is True


def test_check_good_first_issues_marked_not_found(tmp_path, task_discovery_pillar):
    """Test good-first-issue detection when absent."""
    (tmp_path / "README.md").write_text("# Project")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_good_first_issues_marked(tmp_path, task)
    assert result.passed is False


# Level 3 Tests

def test_check_issue_templates_exist_found(tmp_path, task_discovery_pillar):
    """Test issue templates detection."""
    template_dir = tmp_path / ".github" / "ISSUE_TEMPLATE"
    template_dir.mkdir(parents=True)
    (template_dir / "bug.md").write_text("# Bug")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issue_templates_exist(tmp_path, task)
    assert result.passed is True


def test_check_issue_templates_exist_not_found(tmp_path, task_discovery_pillar):
    """Test issue templates detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issue_templates_exist(tmp_path, task)
    assert result.passed is False


def test_check_pr_templates_exist_found(tmp_path, task_discovery_pillar):
    """Test PR template detection."""
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "pull_request_template.md").write_text("# PR")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_pr_templates_exist(tmp_path, task)
    assert result.passed is True


def test_check_pr_templates_exist_not_found(tmp_path, task_discovery_pillar):
    """Test PR template detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_pr_templates_exist(tmp_path, task)
    assert result.passed is False


def test_check_project_board_configured_found(tmp_path, task_discovery_pillar):
    """Test project board detection."""
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "project.yml").write_text("name: Board")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_project_board_configured(tmp_path, task)
    assert result.passed is True


def test_check_project_board_configured_not_found(tmp_path, task_discovery_pillar):
    """Test project board detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_project_board_configured(tmp_path, task)
    assert result.passed is False


def test_check_milestones_defined_found(tmp_path, task_discovery_pillar):
    """Test milestones detection."""
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## v1.0.0")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_milestones_defined(tmp_path, task)
    assert result.passed is True


def test_check_milestones_defined_git(tmp_path, task_discovery_pillar):
    """Test milestones detection with git."""
    (tmp_path / ".git").mkdir()
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_milestones_defined(tmp_path, task)
    assert result.passed is True


# Level 4 Tests

def test_check_automated_issue_labeling_found(tmp_path, task_discovery_pillar):
    """Test automated labeling detection."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "label.yml").write_text(
        """
on: pull_request
jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - name: Add labels
    """
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_automated_issue_labeling(tmp_path, task)
    assert result.passed is True


def test_check_automated_issue_labeling_not_found(tmp_path, task_discovery_pillar):
    """Test automated labeling detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_automated_issue_labeling(tmp_path, task)
    assert result.passed is False


def test_check_issue_triaging_workflow_found(tmp_path, task_discovery_pillar):
    """Test triaging workflow detection."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "triage.yml").write_text(
        """
on: issues
jobs:
  triage:
    runs-on: ubuntu-latest
    """
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issue_triaging_workflow(tmp_path, task)
    assert result.passed is True


def test_check_issue_triaging_workflow_not_found(tmp_path, task_discovery_pillar):
    """Test triaging workflow detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_issue_triaging_workflow(tmp_path, task)
    assert result.passed is False


def test_check_release_management_found(tmp_path, task_discovery_pillar):
    """Test release management detection."""
    (tmp_path / "CHANGELOG.md").write_text("# Changelog")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_release_management(tmp_path, task)
    assert result.passed is True


def test_check_release_management_not_found(tmp_path, task_discovery_pillar):
    """Test release management detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_release_management(tmp_path, task)
    assert result.passed is False


def test_check_contributor_analytics_found(tmp_path, task_discovery_pillar):
    """Test contributor analytics detection."""
    (tmp_path / "ALL_CONTRIBUTORS.md").write_text("# Contributors")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_contributor_analytics(tmp_path, task)
    assert result.passed is True


def test_check_contributor_analytics_in_readme(tmp_path, task_discovery_pillar):
    """Test contributor analytics in README."""
    (tmp_path / "README.md").write_text(
        "# Project\n\nThanks to our contributors."
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_contributor_analytics(tmp_path, task)
    assert result.passed is True


def test_check_contributor_analytics_not_found(tmp_path, task_discovery_pillar):
    """Test contributor analytics detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_contributor_analytics(tmp_path, task)
    assert result.passed is False


# Level 5 Tests

def test_check_automated_task_creation_found(tmp_path, task_discovery_pillar):
    """Test automated task creation detection."""
    (tmp_path / "README.md").write_text(
        "# Project\n\nWe use automated task creation from TODOs."
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_automated_task_creation(tmp_path, task)
    assert result.passed is True


def test_check_automated_task_creation_not_found(tmp_path, task_discovery_pillar):
    """Test automated task creation detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_automated_task_creation(tmp_path, task)
    assert result.passed is False


def test_check_intelligent_routing_found(tmp_path, task_discovery_pillar):
    """Test intelligent routing detection."""
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "CODEOWNERS").write_text("/ @maintainers")
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_intelligent_routing(tmp_path, task)
    assert result.passed is True


def test_check_intelligent_routing_not_found(tmp_path, task_discovery_pillar):
    """Test intelligent routing detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_intelligent_routing(tmp_path, task)
    assert result.passed is False


def test_check_continuous_feedback_found(tmp_path, task_discovery_pillar):
    """Test continuous feedback detection."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "feedback.yml").write_text(
        """
jobs:
  feedback:
    steps:
      - name: Add comment
    """
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_continuous_feedback(tmp_path, task)
    assert result.passed is True


def test_check_continuous_feedback_not_found(tmp_path, task_discovery_pillar):
    """Test continuous feedback detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_continuous_feedback(tmp_path, task)
    assert result.passed is False


def test_check_task_recommendations_found(tmp_path, task_discovery_pillar):
    """Test task recommendations detection."""
    (tmp_path / "README.md").write_text(
        "# Project\n\nWe use AI recommendations for task assignment."
    )
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_task_recommendations(tmp_path, task)
    assert result.passed is True


def test_check_task_recommendations_not_found(tmp_path, task_discovery_pillar):
    """Test task recommendations detection when absent."""
    task = task_discovery_pillar._discover_task_infrastructure(tmp_path)
    result = task_discovery_pillar._check_task_recommendations(tmp_path, task)
    assert result.passed is False


# Fixture-based integration tests

def test_task_discovery_pillar_with_minimal_fixture(task_discovery_pillar):
    """Test pillar against minimal fixture."""
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "task-discovery-minimal"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")

    results = task_discovery_pillar.evaluate(fixture_dir)
    assert len(results) == 18
    assert all(hasattr(r, "passed") for r in results)


def test_task_discovery_pillar_with_complete_fixture(task_discovery_pillar):
    """Test pillar against complete fixture."""
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "task-discovery-complete"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")

    results = task_discovery_pillar.evaluate(fixture_dir)
    assert len(results) == 18
    passed_count = sum(1 for r in results if r.passed)
    # Complete fixture should pass most checks
    assert passed_count >= 10


def test_task_discovery_pillar_with_advanced_fixture(task_discovery_pillar):
    """Test pillar against advanced fixture."""
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "task-discovery-advanced"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")

    results = task_discovery_pillar.evaluate(fixture_dir)
    assert len(results) == 18
    passed_count = sum(1 for r in results if r.passed)
    # Advanced fixture should pass most checks including advanced ones
    assert passed_count >= 13


def test_task_discovery_pillar_importable():
    """Test that TaskDiscoveryPillar is importable."""
    from agent_readiness.pillars import TaskDiscoveryPillar as ImportedPillar

    assert ImportedPillar is not None
    assert ImportedPillar().name == "Task Discovery"


def test_evaluate_returns_correct_structure(task_discovery_pillar, tmp_path):
    """Test that evaluate returns properly structured results."""
    (tmp_path / ".github").mkdir()
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing")

    results = task_discovery_pillar.evaluate(tmp_path)

    assert len(results) == 18
    for result in results:
        assert hasattr(result, "name")
        assert hasattr(result, "passed")
        assert hasattr(result, "message")
        assert hasattr(result, "severity")
        assert hasattr(result, "level")
        assert hasattr(result, "metadata")
        assert isinstance(result.passed, bool)
        assert isinstance(result.severity, Severity)
        assert result.level in [1, 2, 3, 4, 5]
