# Pillar 8: Task Discovery Design Document

**Date**: January 26, 2026
**Status**: In Progress
**Coverage Target**: 85%+
**Test Count Target**: 35+ tests

## Overview

The **Task Discovery Pillar** evaluates how well a codebase helps developers find, understand, and claim work. Good task discovery means:

- Issues and work items are tracked and visible
- Tasks are well-documented and easy to understand
- Entry points for new contributors are clear
- Roadmaps and project status are visible
- Work can be discovered and tracked efficiently
- Contribution process is documented
- Tasks are prioritized and categorized

## What We're Measuring

### Level 1: Functional (Basic Task Tracking)
**Goal**: Basic task tracking infrastructure exists

Checks:
- ✅ **Issue tracker present**: GitHub Issues, GitLab Issues, Jira, etc.
- ✅ **Contributing guide exists**: CONTRIBUTING.md or similar

### Level 2: Documented (Task Visibility)
**Goal**: Tasks and contribution process are documented

Checks:
- ✅ **README explains how to contribute**: README.md has contribution section
- ✅ **Issues are labeled**: Labels exist for categorization
- ✅ **Roadmap visible**: Roadmap, project board, or milestone documentation
- ✅ **Good first issues marked**: "good-first-issue" or similar labels

### Level 3: Standardized (Organized Task Management)
**Goal**: Task management practices are consistent and well-organized

Checks:
- ✅ **Issue templates exist**: GitHub issue templates for consistent format
- ✅ **PR templates exist**: Pull request templates defined
- ✅ **Project board configured**: GitHub Projects or similar board
- ✅ **Milestones defined**: Development milestones or release planning

### Level 4: Optimized (Advanced Task Management)
**Goal**: Production-ready task management with deep insights

Checks:
- ✅ **Automated issue labeling**: GitHub Actions or Renovate labeling
- ✅ **Issue triaging workflow**: Automated or documented triage process
- ✅ **Release management**: Release planning and automation
- ✅ **Contributor analytics**: Insights into contribution patterns

### Level 5: Autonomous (Proactive Task Discovery)
**Goal**: Tasks are automatically discovered and optimized

Checks:
- ✅ **Automated task creation**: Tasks created from errors, TODOs, or code patterns
- ✅ **Intelligent routing**: Tasks routed to appropriate contributors
- ✅ **Continuous feedback**: Automated insights on task difficulty/impact
- ✅ **Task recommendations**: Suggestions for work based on patterns

## Architecture

### Class Structure

```python
class TaskDiscoveryPillar(Pillar):
    name: str = "Task Discovery"
    weight: float = 1.0

    # Discovery
    def _discover_task_infrastructure(target_dir: Path) -> dict

    # Level 1: Functional
    def _check_issue_tracker_present(target_dir: Path) -> CheckResult
    def _check_contributing_guide_exists(target_dir: Path) -> CheckResult

    # Level 2: Documented
    def _check_readme_contribution_section(target_dir: Path) -> CheckResult
    def _check_issues_labeled(target_dir: Path) -> CheckResult
    def _check_roadmap_visible(target_dir: Path) -> CheckResult
    def _check_good_first_issues_marked(target_dir: Path) -> CheckResult

    # Level 3: Standardized
    def _check_issue_templates_exist(target_dir: Path) -> CheckResult
    def _check_pr_templates_exist(target_dir: Path) -> CheckResult
    def _check_project_board_configured(target_dir: Path) -> CheckResult
    def _check_milestones_defined(target_dir: Path) -> CheckResult

    # Level 4: Optimized
    def _check_automated_issue_labeling(target_dir: Path) -> CheckResult
    def _check_issue_triaging_workflow(target_dir: Path) -> CheckResult
    def _check_release_management(target_dir: Path) -> CheckResult
    def _check_contributor_analytics(target_dir: Path) -> CheckResult

    # Level 5: Autonomous
    def _check_automated_task_creation(target_dir: Path) -> CheckResult
    def _check_intelligent_routing(target_dir: Path) -> CheckResult
    def _check_continuous_feedback(target_dir: Path) -> CheckResult
    def _check_task_recommendations(target_dir: Path) -> CheckResult
```

### Discovery Logic (`_discover_task_infrastructure`)

Returns dict with keys:
- `has_github_issues`: Whether GitHub Issues is configured
- `has_contributing_guide`: Whether CONTRIBUTING.md exists
- `has_issue_templates`: Whether issue templates are configured
- `has_pr_templates`: Whether PR templates are configured
- `has_project_board`: Whether GitHub Projects is configured
- `has_labels`: Whether labels are configured
- `has_roadmap`: Roadmap documentation found
- `has_milestones`: Milestones configured
- `readme_content`: README.md content
- `contributing_content`: CONTRIBUTING.md content
- `ci_config`: CI configuration files
- `has_automation`: Task automation indicators

## Detailed Check Implementations

### Level 1

#### _check_issue_tracker_present
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Check for:
    - GitHub Issues (has .github directory)
    - GitLab Issues (has .gitlab-ci.yml or GitLab config)
    - Jira (has JIRA config or links in README)
    - Linear (has linear config)
    - Any issue tracker integration
  - At least one must be present
- **Failure message**: "No issue tracker configured"
- **Pass message**: "Issue tracker found (GitHub Issues, GitLab, etc.)"

#### _check_contributing_guide_exists
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Look for:
    - CONTRIBUTING.md file
    - CONTRIBUTING.rst file
    - .github/CONTRIBUTING.md
    - docs/CONTRIBUTING.md
  - Content should be > 100 characters
- **Failure message**: "No contribution guide found"
- **Pass message**: "Contributing guide found (CONTRIBUTING.md)"

### Level 2

#### _check_readme_contribution_section
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Check README.md for sections about:
    - Contributing
    - Getting involved
    - How to help
    - Development
    - Setup instructions
  - Content should mention contribution process
- **Failure message**: "No contribution section in README"
- **Pass message**: "README includes contribution section"

#### _check_issues_labeled
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Check for:
    - .github/labels.json or label definitions
    - Label mentions in issue templates
    - Common labels: bug, feature, documentation, etc.
    - Or check GitHub API hints in config
  - At least some structure for labels
- **Failure message**: "No issue labels defined"
- **Pass message**: "Issue labels found or label system evident"

#### _check_roadmap_visible
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Look for:
    - ROADMAP.md or ROADMAP.rst
    - docs/ROADMAP.md
    - docs/VISION.md
    - VISION.md
    - Milestones in code/config
    - README section about roadmap
  - At least one should exist
- **Failure message**: "No roadmap or vision document found"
- **Pass message**: "Roadmap or vision document found"

#### _check_good_first_issues_marked
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Check for:
    - "good-first-issue" label reference
    - "beginner-friendly" label reference
    - "help wanted" label reference
    - Documentation about starter tasks
    - CONTRIBUTING.md mentions easy tasks
  - At least one pattern should exist
- **Failure message**: "No good-first-issue labels or guidance"
- **Pass message**: "Good-first-issue labels or beginner guidance found"

### Level 3

#### _check_issue_templates_exist
- **Severity**: RECOMMENDED
- **Level**: 3
- **Logic**:
  - Look for:
    - .github/ISSUE_TEMPLATE/ directory
    - .github/ISSUE_TEMPLATE/bug_report.md
    - .github/ISSUE_TEMPLATE/feature_request.md
    - issue_template.md files
  - At least one template should exist
- **Failure message**: "No issue templates found"
- **Pass message**: "Issue templates found"

#### _check_pr_templates_exist
- **Severity**: RECOMMENDED
- **Level**: 3
- **Logic**:
  - Look for:
    - .github/pull_request_template.md
    - .github/PULL_REQUEST_TEMPLATE.md
    - .github/PULL_REQUEST_TEMPLATE/ directory
  - Template file should exist
- **Failure message**: "No pull request template found"
- **Pass message**: "Pull request template found"

#### _check_project_board_configured
- **Severity**: RECOMMENDED
- **Level**: 3
- **Logic**:
  - Look for:
    - .github/project*.yml or project files
    - References to GitHub Projects
    - Mention of Trello, Linear, Jira boards
    - Project automation config
  - Or check CONTRIBUTING/README for board setup
- **Failure message**: "No project board configured"
- **Pass message**: "Project board configured or referenced"

#### _check_milestones_defined
- **Severity**: RECOMMENDED
- **Level**: 3
- **Logic**:
  - Look for:
    - Release planning documentation
    - Version information (v1.0, v2.0, etc.)
    - Milestone references in code
    - Release notes (CHANGELOG.md, RELEASES.md)
    - Tags in git (indicates versioning)
  - At least basic versioning should exist
- **Failure message**: "No milestones or release plan defined"
- **Pass message**: "Milestones or release planning documented"

### Level 4

#### _check_automated_issue_labeling
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for automation:
    - GitHub Actions workflows that label issues
    - Renovate labeling configuration
    - Automated label application rules
    - .github/workflows/*label*.yml files
    - Configuration for issue automation
  - Workflow should include labeling logic
- **Failure message**: "No automated issue labeling configured"
- **Pass message**: "Automated issue labeling configured"

#### _check_issue_triaging_workflow
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for:
    - Triage workflow documentation
    - Automated triage actions
    - Issue stale handling
    - Automatic close of resolved issues
    - .github/workflows/*triage*.yml or similar
    - Documentation about triage process
  - At least some triaging automation
- **Failure message**: "No issue triaging workflow"
- **Pass message**: "Issue triaging workflow configured"

#### _check_release_management
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for:
    - Release automation (.github/workflows/release.yml)
    - CHANGELOG.md with structured format
    - Release notes generation hints
    - Semantic versioning in package.json/pyproject.toml
    - Release branch protection rules
    - GitHub Releases API usage
  - At least documented release process
- **Failure message**: "No release management configured"
- **Pass message**: "Release management configured or documented"

#### _check_contributor_analytics
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for:
    - ALL_CONTRIBUTORS.md or config
    - Contribution tracking
    - Stats/analytics tools referenced
    - GitHub insights configuration
    - Contributor recognition documentation
    - Points/rewards system hints
  - At least tracking or recognition system
- **Failure message**: "No contributor analytics or tracking"
- **Pass message**: "Contributor analytics or recognition system found"

### Level 5

#### _check_automated_task_creation
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for:
    - TODO detection in code
    - TODO comment scanning
    - Error tracking integration
    - Automatic issue creation from errors
    - Code pattern detection for TODOs
    - Comments indicating automated task creation
  - Some automation for creating tasks
- **Failure message**: "No automated task creation"
- **Pass message**: "Automated task creation from TODOs/errors"

#### _check_intelligent_routing
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for:
    - CODEOWNERS file for routing
    - Team assignments in workflows
    - Skill-based routing hints
    - .github/CODEOWNERS or similar
    - Assignee automation
    - Route to domain experts configuration
  - Some routing logic present
- **Failure message**: "No intelligent task routing configured"
- **Pass message**: "Intelligent task routing configured (CODEOWNERS, etc.)"

#### _check_continuous_feedback
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for:
    - Feedback loops in workflows
    - Task difficulty metrics
    - Time-to-close tracking
    - Burndown charts referenced
    - Continuous improvement loops
    - Analytics on task completion
  - Some feedback mechanism
- **Failure message**: "No continuous feedback loops"
- **Pass message**: "Continuous feedback mechanisms configured"

#### _check_task_recommendations
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for:
    - Recommendation engine hints
    - ML/AI suggestions mentioned
    - Personalized task assignment
    - Priority-based recommendations
    - Machine learning workflows
    - Smart matching of tasks to contributors
  - Recommendation system indicated
- **Failure message**: "No task recommendation system"
- **Pass message**: "Task recommendation system indicated"

## Test Fixture Strategy

Create 5 fixture directories with increasing task discovery maturity:

### `tests/fixtures/task-discovery-none/`
Empty project - no task tracking setup

### `tests/fixtures/task-discovery-minimal/`
- GitHub Issues (indicated by .github directory)
- Basic CONTRIBUTING.md file
- No templates or advanced setup

### `tests/fixtures/task-discovery-basic/`
- CONTRIBUTING.md with detailed guide
- Issue templates in .github/ISSUE_TEMPLATE/
- PR template in .github/
- README with contribution section
- Labeled issues concept
- ROADMAP.md

### `tests/fixtures/task-discovery-complete/`
- Full contribution guide
- Issue and PR templates
- GitHub Projects configuration
- Milestone definitions
- Label definitions
- Roadmap and vision docs
- CHANGELOG.md
- ALL_CONTRIBUTORS.md
- GitHub workflow for automation

### `tests/fixtures/task-discovery-advanced/`
- All from `complete` plus:
- Automated issue labeling workflow
- Triaging workflow
- Release management automation
- CODEOWNERS for routing
- Contributor recognition system
- TODO tracking hints
- Analytics configuration

## Implementation Notes

1. **Issue Tracker Detection**: Primarily GitHub-focused, with hints for others
2. **Task Organization**: Focus on documentation, labels, and templates
3. **Automation Detection**: GitHub Actions workflows are primary source
4. **Metadata Tracking**: Track what automation/tools are present
5. **Coverage Target**: 85%+ code coverage
6. **Test Count**: 35-45 tests covering all checks

## Success Criteria

- All 18 checks implemented and working correctly
- 40+ unit tests with 85%+ coverage
- Test fixtures demonstrate progression through maturity levels
- Clear failure messages guide improvement
- Efficient file scanning (< 1s for large projects)
