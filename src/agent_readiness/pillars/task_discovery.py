"""Task Discovery pillar implementation."""

import re
from pathlib import Path

from agent_readiness.pillar import Pillar
from agent_readiness.models import CheckResult, Severity


class TaskDiscoveryPillar(Pillar):
    """Evaluates task discovery and issue management infrastructure."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Task Discovery"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for task discovery checks."""
        results = []

        # Discover task infrastructure
        task = self._discover_task_infrastructure(target_dir)

        # Level 1: Functional
        results.append(self._check_issue_tracker_present(target_dir, task))
        results.append(self._check_contributing_guide_exists(target_dir, task))

        # Level 2: Documented
        results.append(self._check_readme_contribution_section(target_dir, task))
        results.append(self._check_issues_labeled(target_dir, task))
        results.append(self._check_roadmap_visible(target_dir, task))
        results.append(self._check_good_first_issues_marked(target_dir, task))

        # Level 3: Standardized
        results.append(self._check_issue_templates_exist(target_dir, task))
        results.append(self._check_pr_templates_exist(target_dir, task))
        results.append(self._check_project_board_configured(target_dir, task))
        results.append(self._check_milestones_defined(target_dir, task))

        # Level 4: Optimized
        results.append(self._check_automated_issue_labeling(target_dir, task))
        results.append(self._check_issue_triaging_workflow(target_dir, task))
        results.append(self._check_release_management(target_dir, task))
        results.append(self._check_contributor_analytics(target_dir, task))

        # Level 5: Autonomous
        results.append(self._check_automated_task_creation(target_dir, task))
        results.append(self._check_intelligent_routing(target_dir, task))
        results.append(self._check_continuous_feedback(target_dir, task))
        results.append(self._check_task_recommendations(target_dir, task))

        return results

    def _discover_task_infrastructure(self, target_dir: Path) -> dict:
        """Discover available task and issue management infrastructure.

        Args:
            target_dir: Directory to scan

        Returns:
            Dict with task management configuration information
        """
        has_github_issues = False
        has_contributing_guide = False
        has_issue_templates = False
        has_pr_templates = False
        has_project_board = False
        has_labels = False
        has_roadmap = False
        has_milestones = False
        readme_content = ""
        contributing_content = ""
        ci_config = []
        has_automation = False
        has_codeowners = False
        changelog_found = False
        github_dir = target_dir / ".github"

        # Check for GitHub Issues
        if github_dir.exists():
            has_github_issues = True

        # Check for contributing guide
        for contrib_file in [
            "CONTRIBUTING.md",
            "CONTRIBUTING.rst",
            ".github/CONTRIBUTING.md",
            "docs/CONTRIBUTING.md",
        ]:
            contrib_path = target_dir / contrib_file
            if contrib_path.exists():
                has_contributing_guide = True
                try:
                    contributing_content = contrib_path.read_text(errors="ignore")
                except Exception:
                    pass
                break

        # Check for issue templates
        if (github_dir / "ISSUE_TEMPLATE").exists():
            has_issue_templates = True
        elif (target_dir / "issue_template.md").exists():
            has_issue_templates = True

        # Check for PR templates
        if (github_dir / "pull_request_template.md").exists():
            has_pr_templates = True
        elif (github_dir / "PULL_REQUEST_TEMPLATE.md").exists():
            has_pr_templates = True
        elif (github_dir / "PULL_REQUEST_TEMPLATE").exists():
            has_pr_templates = True

        # Check for project board config
        if (github_dir / "project.yml").exists() or (
            github_dir / "projects.yml"
        ).exists():
            has_project_board = True

        # Check for labels
        if (github_dir / "labels.json").exists():
            has_labels = True

        # Check for roadmap
        for roadmap_file in [
            "ROADMAP.md",
            "ROADMAP.rst",
            "docs/ROADMAP.md",
            "docs/VISION.md",
            "VISION.md",
        ]:
            if (target_dir / roadmap_file).exists():
                has_roadmap = True
                break

        # Check for milestones/versions
        if (target_dir / "CHANGELOG.md").exists() or (
            target_dir / "CHANGELOG.rst"
        ).exists():
            has_milestones = True
            changelog_found = True

        # Check package.json or pyproject.toml for version info
        if (target_dir / "package.json").exists():
            try:
                import json

                pkg = json.loads((target_dir / "package.json").read_text())
                if "version" in pkg:
                    has_milestones = True
            except Exception:
                pass

        if (target_dir / "pyproject.toml").exists():
            try:
                content = (target_dir / "pyproject.toml").read_text(errors="ignore")
                if "version" in content.lower():
                    has_milestones = True
            except Exception:
                pass

        # Check for README
        readme_path = target_dir / "README.md"
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text(errors="ignore")
            except Exception:
                pass

        # Check for CI config
        for ci_file in [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".circleci/config.yml",
        ]:
            ci_path = target_dir / ci_file
            if ci_path.exists():
                ci_config.append(ci_file)

                # Check for automation in workflows
                if ci_path.is_dir():
                    for workflow in ci_path.rglob("*.yml"):
                        try:
                            content = workflow.read_text(errors="ignore")
                            if any(
                                keyword in content.lower()
                                for keyword in [
                                    "label",
                                    "triage",
                                    "release",
                                    "stale",
                                    "archive",
                                ]
                            ):
                                has_automation = True
                        except Exception:
                            pass

        # Check for CODEOWNERS
        if (github_dir / "CODEOWNERS").exists():
            has_codeowners = True
        elif (target_dir / "CODEOWNERS").exists():
            has_codeowners = True

        return {
            "has_github_issues": has_github_issues,
            "has_contributing_guide": has_contributing_guide,
            "has_issue_templates": has_issue_templates,
            "has_pr_templates": has_pr_templates,
            "has_project_board": has_project_board,
            "has_labels": has_labels,
            "has_roadmap": has_roadmap,
            "has_milestones": has_milestones,
            "readme_content": readme_content,
            "contributing_content": contributing_content,
            "ci_config": ci_config,
            "has_automation": has_automation,
            "has_codeowners": has_codeowners,
            "changelog_found": changelog_found,
        }

    # Level 1: Functional

    def _check_issue_tracker_present(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if an issue tracker is configured."""
        passed = task["has_github_issues"]
        return CheckResult(
            name="Issue tracker present",
            passed=passed,
            message="GitHub Issues configured"
            if passed
            else "No issue tracker configured (GitHub Issues not found)",
            severity=Severity.REQUIRED,
            level=1,
            metadata={"github_issues": task["has_github_issues"]},
        )

    def _check_contributing_guide_exists(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if a contributing guide exists."""
        passed = task["has_contributing_guide"]
        return CheckResult(
            name="Contributing guide exists",
            passed=passed,
            message="Contributing guide found (CONTRIBUTING.md)"
            if passed
            else "No contribution guide found",
            severity=Severity.REQUIRED,
            level=1,
            metadata={},
        )

    # Level 2: Documented

    def _check_readme_contribution_section(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if README has contribution section."""
        readme = task["readme_content"].lower()
        passed = any(
            phrase in readme
            for phrase in ["contribut", "getting involved", "how to help", "development"]
        )

        return CheckResult(
            name="README contribution section",
            passed=passed,
            message="README includes contribution section"
            if passed
            else "No contribution section in README",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={},
        )

    def _check_issues_labeled(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if issues are labeled."""
        passed = task["has_labels"]

        # Also check for label references in templates
        if not passed and (target_dir / ".github" / "ISSUE_TEMPLATE").exists():
            for template in (target_dir / ".github" / "ISSUE_TEMPLATE").glob("*.md"):
                try:
                    content = template.read_text(errors="ignore")
                    if "label" in content.lower():
                        passed = True
                        break
                except Exception:
                    pass

        return CheckResult(
            name="Issues labeled",
            passed=passed,
            message="Issue labels found or label system evident"
            if passed
            else "No issue labels defined",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={"has_labels": task["has_labels"]},
        )

    def _check_roadmap_visible(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if roadmap or vision is visible."""
        passed = task["has_roadmap"]

        # Also check README for roadmap section
        if not passed:
            readme = task["readme_content"].lower()
            if "roadmap" in readme or "vision" in readme or "plan" in readme:
                passed = True

        return CheckResult(
            name="Roadmap visible",
            passed=passed,
            message="Roadmap or vision document found"
            if passed
            else "No roadmap or vision document found",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={"roadmap_file": task["has_roadmap"]},
        )

    def _check_good_first_issues_marked(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if good-first-issue labels are indicated."""
        passed = False

        # Check contributing guide
        contrib = task["contributing_content"].lower()
        if any(
            phrase in contrib
            for phrase in [
                "good-first-issue",
                "good first issue",
                "beginner-friendly",
                "beginner friendly",
                "help wanted",
                "starter tasks",
                "easy tasks",
            ]
        ):
            passed = True

        # Check README
        if not passed:
            readme = task["readme_content"].lower()
            if any(
                phrase in readme
                for phrase in [
                    "good-first-issue",
                    "good first issue",
                    "beginner-friendly",
                    "help wanted",
                    "starter tasks",
                ]
            ):
                passed = True

        # Check for good-first-issue label mentions in templates
        if not passed:
            for template in (target_dir / ".github" / "ISSUE_TEMPLATE").glob(
                "*.md"
            ) if (target_dir / ".github" / "ISSUE_TEMPLATE").exists() else []:
                try:
                    content = template.read_text(errors="ignore")
                    if "good-first-issue" in content.lower():
                        passed = True
                        break
                except Exception:
                    pass

        return CheckResult(
            name="Good-first-issues marked",
            passed=passed,
            message="Good-first-issue labels or beginner guidance found"
            if passed
            else "No good-first-issue labels or guidance",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={},
        )

    # Level 3: Standardized

    def _check_issue_templates_exist(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if issue templates exist."""
        passed = task["has_issue_templates"]
        return CheckResult(
            name="Issue templates exist",
            passed=passed,
            message="Issue templates found"
            if passed
            else "No issue templates found",
            severity=Severity.RECOMMENDED,
            level=3,
            metadata={"has_templates": task["has_issue_templates"]},
        )

    def _check_pr_templates_exist(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if PR template exists."""
        passed = task["has_pr_templates"]
        return CheckResult(
            name="PR template exists",
            passed=passed,
            message="Pull request template found"
            if passed
            else "No pull request template found",
            severity=Severity.RECOMMENDED,
            level=3,
            metadata={"has_template": task["has_pr_templates"]},
        )

    def _check_project_board_configured(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if project board is configured."""
        passed = task["has_project_board"]

        # Also check README for project board mentions
        if not passed:
            readme = task["readme_content"].lower()
            if any(
                phrase in readme
                for phrase in [
                    "project board",
                    "github projects",
                    "trello",
                    "linear",
                    "jira board",
                ]
            ):
                passed = True

        return CheckResult(
            name="Project board configured",
            passed=passed,
            message="Project board configured or referenced"
            if passed
            else "No project board configured",
            severity=Severity.RECOMMENDED,
            level=3,
            metadata={},
        )

    def _check_milestones_defined(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if milestones or release plan is defined."""
        passed = task["has_milestones"]

        # Also check for tags or versions in git
        if not passed:
            git_dir = target_dir / ".git"
            if git_dir.exists():
                passed = True

        return CheckResult(
            name="Milestones defined",
            passed=passed,
            message="Milestones or release planning documented"
            if passed
            else "No milestones or release plan defined",
            severity=Severity.RECOMMENDED,
            level=3,
            metadata={
                "changelog_found": task["changelog_found"],
                "has_milestones": task["has_milestones"],
            },
        )

    # Level 4: Optimized

    def _check_automated_issue_labeling(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if automated issue labeling is configured."""
        passed = False

        # Check for labeling workflows
        for ci_file in task["ci_config"]:
            ci_path = target_dir / ci_file
            if ci_path.is_dir():
                for workflow in ci_path.rglob("*.yml"):
                    try:
                        content = workflow.read_text(errors="ignore")
                        if "label" in content.lower() and ("add" in content.lower() or "pull_request" in content):
                            passed = True
                            break
                    except Exception:
                        pass
            if passed:
                break

        return CheckResult(
            name="Automated issue labeling",
            passed=passed,
            message="Automated issue labeling configured"
            if passed
            else "No automated issue labeling configured",
            severity=Severity.OPTIONAL,
            level=4,
            metadata={},
        )

    def _check_issue_triaging_workflow(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if issue triaging workflow exists."""
        passed = False

        # Check for triage/stale workflows
        for ci_file in task["ci_config"]:
            ci_path = target_dir / ci_file
            if ci_path.is_dir():
                for workflow in ci_path.rglob("*.yml"):
                    try:
                        content = workflow.read_text(errors="ignore")
                        if any(
                            keyword in content.lower()
                            for keyword in ["triage", "stale", "close", "archive"]
                        ):
                            passed = True
                            break
                    except Exception:
                        pass
            if passed:
                break

        return CheckResult(
            name="Issue triaging workflow",
            passed=passed,
            message="Issue triaging workflow configured"
            if passed
            else "No issue triaging workflow",
            severity=Severity.OPTIONAL,
            level=4,
            metadata={},
        )

    def _check_release_management(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if release management is configured."""
        passed = task["changelog_found"]

        # Check for release workflow
        if not passed:
            for ci_file in task["ci_config"]:
                ci_path = target_dir / ci_file
                if ci_path.is_dir():
                    for workflow in ci_path.rglob("*release*.yml"):
                        try:
                            content = workflow.read_text(errors="ignore")
                            if "release" in content.lower():
                                passed = True
                                break
                        except Exception:
                            pass
                if passed:
                    break

        return CheckResult(
            name="Release management",
            passed=passed,
            message="Release management configured or documented"
            if passed
            else "No release management configured",
            severity=Severity.OPTIONAL,
            level=4,
            metadata={},
        )

    def _check_contributor_analytics(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if contributor analytics or recognition exists."""
        passed = False

        # Check for ALL_CONTRIBUTORS
        if (target_dir / "ALL_CONTRIBUTORS.md").exists() or (
            target_dir / ".all-contributorsrc"
        ).exists():
            passed = True

        # Check README for contributor section
        if not passed:
            readme = task["readme_content"].lower()
            if any(
                phrase in readme
                for phrase in [
                    "contributor",
                    "acknowledgments",
                    "thanks to",
                    "built by",
                ]
            ):
                passed = True

        return CheckResult(
            name="Contributor analytics",
            passed=passed,
            message="Contributor analytics or recognition system found"
            if passed
            else "No contributor analytics or tracking",
            severity=Severity.OPTIONAL,
            level=4,
            metadata={},
        )

    # Level 5: Autonomous

    def _check_automated_task_creation(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if automated task creation is configured."""
        passed = False

        # Check for TODO detection or error tracking integration
        readme = task["readme_content"].lower()
        if any(
            phrase in readme
            for phrase in [
                "todo",
                "automated task",
                "error tracking",
                "sentry",
                "bugsnag",
            ]
        ):
            passed = True

        # Check for TODO comments in source code
        if not passed:
            for py_file in (target_dir / "src").rglob("*.py") if (
                target_dir / "src"
            ).exists() else []:
                try:
                    content = py_file.read_text(errors="ignore")
                    if "TODO" in content:
                        passed = True
                        break
                except Exception:
                    pass

        return CheckResult(
            name="Automated task creation",
            passed=passed,
            message="Automated task creation from TODOs/errors"
            if passed
            else "No automated task creation",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={},
        )

    def _check_intelligent_routing(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if intelligent task routing is configured."""
        passed = task["has_codeowners"]

        # Also check for team assignments in workflows
        if not passed:
            for ci_file in task["ci_config"]:
                ci_path = target_dir / ci_file
                if ci_path.is_dir():
                    for workflow in ci_path.rglob("*.yml"):
                        try:
                            content = workflow.read_text(errors="ignore")
                            if "assignees" in content.lower() or "assign" in content.lower():
                                passed = True
                                break
                        except Exception:
                            pass
                if passed:
                    break

        return CheckResult(
            name="Intelligent task routing",
            passed=passed,
            message="Intelligent task routing configured (CODEOWNERS, etc.)"
            if passed
            else "No intelligent task routing configured",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={"has_codeowners": task["has_codeowners"]},
        )

    def _check_continuous_feedback(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if continuous feedback loops are configured."""
        passed = False

        # Check for feedback mechanisms in workflows
        for ci_file in task["ci_config"]:
            ci_path = target_dir / ci_file
            if ci_path.is_dir():
                for workflow in ci_path.rglob("*.yml"):
                    try:
                        content = workflow.read_text(errors="ignore")
                        if any(
                            keyword in content.lower()
                            for keyword in [
                                "comment",
                                "feedback",
                                "metrics",
                                "analytics",
                                "status",
                            ]
                        ):
                            passed = True
                            break
                    except Exception:
                        pass
            if passed:
                break

        return CheckResult(
            name="Continuous feedback loops",
            passed=passed,
            message="Continuous feedback mechanisms configured"
            if passed
            else "No continuous feedback loops",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={},
        )

    def _check_task_recommendations(self, target_dir: Path, task: dict) -> CheckResult:
        """Check if task recommendation system is indicated."""
        passed = False

        # Check for recommendation system hints
        readme = task["readme_content"].lower()
        if any(
            phrase in readme
            for phrase in [
                "recommend",
                "suggestion",
                "smart match",
                "personalized",
                "machine learning",
                "ai",
            ]
        ):
            passed = True

        # Check for ML workflows
        if not passed:
            for ci_file in task["ci_config"]:
                ci_path = target_dir / ci_file
                if ci_path.is_dir():
                    for workflow in ci_path.rglob("*.yml"):
                        try:
                            content = workflow.read_text(errors="ignore")
                            if "ml" in content.lower() or "model" in content.lower():
                                passed = True
                                break
                        except Exception:
                            pass
                if passed:
                    break

        return CheckResult(
            name="Task recommendations",
            passed=passed,
            message="Task recommendation system indicated"
            if passed
            else "No task recommendation system",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={},
        )
