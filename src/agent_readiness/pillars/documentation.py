"""Documentation pillar implementation."""

import re
from pathlib import Path

from agent_readiness.models import CheckResult, Severity
from agent_readiness.pillar import Pillar


class DocumentationPillar(Pillar):
    """Evaluates documentation quality, comprehensiveness, and agent-readiness."""

    # Key documentation file patterns
    README_PATTERNS = ["README.md", "README.rst", "README.txt", "README"]
    AGENTS_PATTERNS = ["AGENTS.md"]
    CONTRIBUTING_PATTERNS = ["CONTRIBUTING.md"]
    ARCHITECTURE_PATTERNS = ["ARCHITECTURE.md", "DESIGN.md"]
    CHANGELOG_PATTERNS = ["CHANGELOG.md", "HISTORY.md", "NEWS.md", "CHANGES.md"]
    API_PATTERNS = ["API.md", "ENDPOINTS.md"]
    CODE_OF_CONDUCT_PATTERNS = ["CODE_OF_CONDUCT.md"]

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Documentation"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for documentation checks."""
        results = []

        # Discover documentation assets
        docs = self._discover_documentation(target_dir)

        # Level 1: README exists
        results.append(self._check_readme_exists(target_dir, docs))

        # Level 2: README quality, AGENTS.md, CONTRIBUTING
        results.append(self._check_readme_quality(target_dir, docs))
        results.append(self._check_agents_md_exists(target_dir, docs))
        results.append(self._check_contributing_exists(target_dir, docs))

        # Level 3: AGENTS quality, API docs, architecture
        results.append(self._check_agents_md_quality(target_dir, docs))
        results.append(self._check_api_documentation(target_dir, docs))
        results.append(self._check_architecture_documented(target_dir, docs))

        # Level 4: Coverage, changelog, inline docs
        results.append(self._check_documentation_coverage(target_dir, docs))
        results.append(self._check_changelog_exists(target_dir, docs))
        results.append(self._check_inline_documentation(target_dir))

        # Level 5: Code of conduct, auto-generated docs, examples
        results.append(self._check_code_of_conduct(target_dir, docs))
        results.append(self._check_auto_generated_docs(target_dir, docs))
        results.append(self._check_examples_and_tutorials(target_dir, docs))

        return results

    def _discover_documentation(self, target_dir: Path) -> dict:
        """Discover documentation assets in the repository.

        Args:
            target_dir: Directory to scan

        Returns:
            Dictionary with paths to various documentation files
        """
        docs = {
            "readme": None,
            "agents_md": None,
            "contributing": None,
            "architecture": None,
            "changelog": None,
            "api": None,
            "code_of_conduct": None,
            "docs_dir": None,
        }

        # Find README (case-insensitive search)
        for pattern in self.README_PATTERNS:
            readme_path = target_dir / pattern
            if readme_path.exists():
                docs["readme"] = readme_path
                break
            # Case-insensitive check
            for file_path in target_dir.glob("*"):
                if file_path.name.lower() == pattern.lower():
                    docs["readme"] = file_path
                    break

        # Find AGENTS.md
        agents_path = target_dir / "AGENTS.md"
        if agents_path.exists():
            docs["agents_md"] = agents_path

        # Find CONTRIBUTING.md
        contrib_path = target_dir / "CONTRIBUTING.md"
        if contrib_path.exists():
            docs["contributing"] = contrib_path
        elif (target_dir / ".github" / "CONTRIBUTING.md").exists():
            docs["contributing"] = target_dir / ".github" / "CONTRIBUTING.md"

        # Find ARCHITECTURE.md
        for pattern in self.ARCHITECTURE_PATTERNS:
            arch_path = target_dir / pattern
            if arch_path.exists():
                docs["architecture"] = arch_path
                break
        # Also check docs/ directory
        if not docs["architecture"]:
            docs_dir = target_dir / "docs"
            if docs_dir.exists():
                for arch_file in docs_dir.glob("*architecture*"):
                    if arch_file.is_file():
                        docs["architecture"] = arch_file
                        break

        # Find CHANGELOG
        for pattern in self.CHANGELOG_PATTERNS:
            changelog_path = target_dir / pattern
            if changelog_path.exists():
                docs["changelog"] = changelog_path
                break

        # Find API documentation
        for pattern in self.API_PATTERNS:
            api_path = target_dir / pattern
            if api_path.exists():
                docs["api"] = api_path
                break

        # Find CODE_OF_CONDUCT
        coc_path = target_dir / "CODE_OF_CONDUCT.md"
        if coc_path.exists():
            docs["code_of_conduct"] = coc_path
        elif (target_dir / ".github" / "CODE_OF_CONDUCT.md").exists():
            docs["code_of_conduct"] = target_dir / ".github" / "CODE_OF_CONDUCT.md"

        # Find docs directory
        docs_dir = target_dir / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            docs["docs_dir"] = docs_dir

        return docs

    def _check_readme_exists(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if README exists (Level 1)."""
        if docs["readme"]:
            return CheckResult(
                name="README exists",
                passed=True,
                message=f"README found: {docs['readme'].name}",
                severity=Severity.REQUIRED,
                level=1,
            )
        else:
            return CheckResult(
                name="README exists",
                passed=False,
                message="No README found in repository root",
                severity=Severity.REQUIRED,
                level=1,
            )

    def _check_readme_quality(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if README has minimum quality (Level 2)."""
        if not docs["readme"]:
            return CheckResult(
                name="README quality",
                passed=False,
                message="Cannot evaluate quality - no README found",
                severity=Severity.RECOMMENDED,
                level=2,
            )

        try:
            content = docs["readme"].read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return CheckResult(
                name="README quality",
                passed=False,
                message="Error reading README",
                severity=Severity.RECOMMENDED,
                level=2,
            )

        quality_indicators = []

        # Check minimum length
        if len(content) >= 500:
            quality_indicators.append("adequate length")

        # Check for key sections (case-insensitive)
        content_lower = content.lower()

        if any(
            section in content_lower
            for section in ["## installation", "# installation", "setup", "getting started"]
        ):
            quality_indicators.append("installation/setup section")

        if any(
            section in content_lower
            for section in ["## usage", "# usage", "quick start", "examples"]
        ):
            quality_indicators.append("usage/examples section")

        if any(
            section in content_lower
            for section in ["## project", "# overview", "# about", "description"]
        ):
            quality_indicators.append("project description")

        # Check for code examples
        if "```" in content or "`" in content:
            quality_indicators.append("code examples")

        # Check for links or badges
        if "[" in content and "](" in content:
            quality_indicators.append("links/references")

        if len(quality_indicators) >= 2:
            return CheckResult(
                name="README quality",
                passed=True,
                message=f"README has good quality ({', '.join(quality_indicators[:2])})",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        elif len(quality_indicators) == 1:
            return CheckResult(
                name="README quality",
                passed=False,
                message=f"README minimal quality ({quality_indicators[0]} only)",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="README quality",
                passed=False,
                message="README lacks key sections (installation, usage, description)",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_agents_md_exists(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if AGENTS.md exists (Level 2)."""
        if docs["agents_md"]:
            return CheckResult(
                name="AGENTS.md exists",
                passed=True,
                message=f"AGENTS.md found at {docs['agents_md'].name}",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="AGENTS.md exists",
                passed=False,
                message="AGENTS.md not found (AI agent readiness guide recommended)",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_contributing_exists(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if contribution guidelines exist (Level 2)."""
        if docs["contributing"]:
            return CheckResult(
                name="CONTRIBUTING exists",
                passed=True,
                message=f"Contribution guidelines found",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            # Check if it's in README
            if docs["readme"]:
                try:
                    readme_content = docs["readme"].read_text(encoding="utf-8", errors="ignore").lower()
                    if any(
                        section in readme_content
                        for section in ["## contributing", "# contributing", "contribution"]
                    ):
                        return CheckResult(
                            name="CONTRIBUTING exists",
                            passed=True,
                            message="Contributing guidelines in README.md",
                            severity=Severity.RECOMMENDED,
                            level=2,
                        )
                except Exception:
                    pass

            return CheckResult(
                name="CONTRIBUTING exists",
                passed=False,
                message="No contribution guidelines found (CONTRIBUTING.md or README section)",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_agents_md_quality(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if AGENTS.md has quality content (Level 3)."""
        if not docs["agents_md"]:
            return CheckResult(
                name="AGENTS.md quality",
                passed=False,
                message="Cannot evaluate quality - AGENTS.md not found",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        try:
            content = docs["agents_md"].read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return CheckResult(
                name="AGENTS.md quality",
                passed=False,
                message="Error reading AGENTS.md",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        if len(content) < 200:
            return CheckResult(
                name="AGENTS.md quality",
                passed=False,
                message="AGENTS.md is too short (minimum 200 characters)",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        content_lower = content.lower()
        found_sections = []

        # Check for key sections
        if any(
            s in content_lower
            for s in ["architecture", "design", "structure", "codebase"]
        ):
            found_sections.append("architecture")

        if any(
            s in content_lower
            for s in ["setup", "development", "install", "environment"]
        ):
            found_sections.append("setup")

        if any(
            s in content_lower for s in ["test", "testing", "pytest", "jest", "cargo test"]
        ):
            found_sections.append("testing")

        if any(
            s in content_lower
            for s in ["file", "location", "structure", "directory"]
        ):
            found_sections.append("file locations")

        if len(found_sections) >= 3:
            return CheckResult(
                name="AGENTS.md quality",
                passed=True,
                message=f"AGENTS.md comprehensive ({', '.join(found_sections)})",
                severity=Severity.RECOMMENDED,
                level=3,
            )
        elif len(found_sections) >= 1:
            return CheckResult(
                name="AGENTS.md quality",
                passed=False,
                message=f"AGENTS.md incomplete ({len(found_sections)} sections, need >=3)",
                severity=Severity.RECOMMENDED,
                level=3,
            )
        else:
            return CheckResult(
                name="AGENTS.md quality",
                passed=False,
                message="AGENTS.md lacks key sections (architecture, setup, testing)",
                severity=Severity.RECOMMENDED,
                level=3,
            )

    def _check_api_documentation(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if API documentation exists (Level 3)."""
        if docs["api"]:
            return CheckResult(
                name="API documentation",
                passed=True,
                message=f"API documentation found",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        # Check for docstrings in main modules
        src_dirs = [target_dir / "src", target_dir / "lib", target_dir]

        for src_dir in src_dirs:
            if not src_dir.exists():
                continue

            # Check Python modules
            py_files = list(src_dir.glob("**/*.py"))
            if py_files:
                # Sample first 10 files
                has_docstrings = 0
                for py_file in py_files[:10]:
                    try:
                        content = py_file.read_text(encoding="utf-8", errors="ignore")
                        if '"""' in content or "'''" in content or "def " in content:
                            if '"""' in content or "'''" in content:
                                has_docstrings += 1
                    except Exception:
                        pass

                if has_docstrings >= 5:
                    return CheckResult(
                        name="API documentation",
                        passed=True,
                        message=f"Docstrings found in Python modules",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )

        return CheckResult(
            name="API documentation",
            passed=False,
            message="No API documentation found (API.md or module docstrings)",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_architecture_documented(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if architecture is documented (Level 3)."""
        if docs["architecture"]:
            return CheckResult(
                name="Architecture documented",
                passed=True,
                message=f"Architecture documentation found",
                severity=Severity.RECOMMENDED,
                level=3,
            )

        # Check AGENTS.md for architecture section
        if docs["agents_md"]:
            try:
                content = docs["agents_md"].read_text(encoding="utf-8", errors="ignore").lower()
                if any(
                    s in content
                    for s in ["architecture", "design", "structure", "overview"]
                ):
                    return CheckResult(
                        name="Architecture documented",
                        passed=True,
                        message="Architecture described in AGENTS.md",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Architecture documented",
            passed=False,
            message="No architecture documentation found",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_documentation_coverage(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check documentation coverage of components (Level 4)."""
        # Count major directories/components
        major_dirs = 0
        documented_dirs = 0

        # Check for README files in subdirectories
        for item in target_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                major_dirs += 1

                # Check for README in subdirectory
                if (item / "README.md").exists():
                    documented_dirs += 1

        if major_dirs == 0:
            return CheckResult(
                name="Documentation coverage",
                passed=False,
                message="No subdirectories found to evaluate coverage",
                severity=Severity.OPTIONAL,
                level=4,
            )

        coverage_percent = (documented_dirs / major_dirs * 100) if major_dirs > 0 else 0

        if coverage_percent >= 60:
            return CheckResult(
                name="Documentation coverage",
                passed=True,
                message=f"Documentation covers {coverage_percent:.0f}% of components",
                severity=Severity.OPTIONAL,
                level=4,
            )
        else:
            return CheckResult(
                name="Documentation coverage",
                passed=False,
                message=f"Documentation covers only {coverage_percent:.0f}% of components",
                severity=Severity.OPTIONAL,
                level=4,
            )

    def _check_changelog_exists(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if changelog exists (Level 4)."""
        if docs["changelog"]:
            return CheckResult(
                name="Changelog exists",
                passed=True,
                message=f"Changelog found",
                severity=Severity.OPTIONAL,
                level=4,
            )
        else:
            return CheckResult(
                name="Changelog exists",
                passed=False,
                message="No CHANGELOG.md found",
                severity=Severity.OPTIONAL,
                level=4,
            )

    def _check_inline_documentation(self, target_dir: Path) -> CheckResult:
        """Check if code has inline documentation (Level 4)."""
        # Sample Python files
        py_files = list(target_dir.glob("**/*.py"))
        if not py_files:
            return CheckResult(
                name="Inline documentation",
                passed=False,
                message="No Python files found to evaluate",
                severity=Severity.OPTIONAL,
                level=4,
            )

        # Sample up to 10 files
        sampled_files = py_files[:10]
        total_lines = 0
        documented_lines = 0

        for py_file in sampled_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")

                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        total_lines += 1
                        if (
                            stripped.startswith("#")
                            or '"""' in line
                            or "'''" in line
                        ):
                            documented_lines += 1
            except Exception:
                pass

        if total_lines == 0:
            return CheckResult(
                name="Inline documentation",
                passed=False,
                message="Could not analyze code documentation",
                severity=Severity.OPTIONAL,
                level=4,
            )

        doc_percent = (documented_lines / total_lines * 100) if total_lines > 0 else 0

        if doc_percent >= 20:
            return CheckResult(
                name="Inline documentation",
                passed=True,
                message=f"Code has inline documentation ({doc_percent:.0f}% coverage)",
                severity=Severity.OPTIONAL,
                level=4,
            )
        else:
            return CheckResult(
                name="Inline documentation",
                passed=False,
                message=f"Code has limited inline documentation ({doc_percent:.0f}% coverage)",
                severity=Severity.OPTIONAL,
                level=4,
            )

    def _check_code_of_conduct(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if code of conduct exists (Level 5)."""
        if docs["code_of_conduct"]:
            return CheckResult(
                name="Code of conduct",
                passed=True,
                message=f"Code of conduct found",
                severity=Severity.OPTIONAL,
                level=5,
            )
        else:
            return CheckResult(
                name="Code of conduct",
                passed=False,
                message="No code of conduct found (CODE_OF_CONDUCT.md)",
                severity=Severity.OPTIONAL,
                level=5,
            )

    def _check_auto_generated_docs(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if documentation generation is configured (Level 5)."""
        tools_found = []

        # Check for Sphinx
        if (target_dir / "conf.py").exists() or (target_dir / "docs" / "conf.py").exists():
            tools_found.append("Sphinx")

        # Check for MkDocs
        if (target_dir / "mkdocs.yml").exists():
            tools_found.append("MkDocs")

        # Check for TypeDoc
        if (target_dir / "typedoc.json").exists():
            tools_found.append("TypeDoc")

        # Check for JSDoc config
        if (target_dir / "jsdoc.json").exists():
            tools_found.append("JSDoc")

        if tools_found:
            return CheckResult(
                name="Auto-generated docs",
                passed=True,
                message=f"Documentation generation configured ({', '.join(tools_found)})",
                severity=Severity.OPTIONAL,
                level=5,
            )
        else:
            return CheckResult(
                name="Auto-generated docs",
                passed=False,
                message="No doc generation tool configured (Sphinx, MkDocs, TypeDoc, JSDoc)",
                severity=Severity.OPTIONAL,
                level=5,
            )

    def _check_examples_and_tutorials(self, target_dir: Path, docs: dict) -> CheckResult:
        """Check if examples and tutorials exist (Level 5)."""
        examples_found = []

        # Check for examples directory
        if (target_dir / "examples").exists():
            example_files = list((target_dir / "examples").glob("**/*"))
            examples_found.append(f"examples/ ({len(example_files)} files)")

        # Check for tutorials directory
        if (target_dir / "tutorials").exists():
            tutorial_files = list((target_dir / "tutorials").glob("**/*"))
            examples_found.append(f"tutorials/ ({len(tutorial_files)} files)")

        # Check for Jupyter notebooks
        notebooks = list(target_dir.glob("**/*.ipynb"))
        if notebooks:
            examples_found.append(f"Jupyter notebooks ({len(notebooks)})")

        # Check for code examples in README
        if docs["readme"]:
            try:
                content = docs["readme"].read_text(encoding="utf-8", errors="ignore")
                if "```" in content:
                    examples_found.append("code examples in README")
            except Exception:
                pass

        if examples_found:
            return CheckResult(
                name="Examples and tutorials",
                passed=True,
                message=f"Examples/tutorials found ({', '.join(examples_found[:2])})",
                severity=Severity.OPTIONAL,
                level=5,
            )
        else:
            return CheckResult(
                name="Examples and tutorials",
                passed=False,
                message="No examples or tutorials found",
                severity=Severity.OPTIONAL,
                level=5,
            )
