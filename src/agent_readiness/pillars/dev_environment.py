"""Dev Environment pillar implementation."""

import json
import re
from pathlib import Path

from agent_readiness.pillar import Pillar
from agent_readiness.models import CheckResult, Severity


class DevEnvironmentPillar(Pillar):
    """Evaluates development environment setup and reproducibility."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Dev Environment"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for dev environment checks."""
        results = []

        # Discover available dev environment assets
        dev_env = self._discover_dev_environment(target_dir)

        # Level 1: Functional
        results.append(self._check_setup_instructions_exist(target_dir, dev_env))
        results.append(self._check_dependency_file_exists(target_dir, dev_env))

        # Level 2: Documented
        results.append(self._check_env_example_exists(target_dir, dev_env))
        results.append(self._check_setup_steps_documented(target_dir, dev_env))
        results.append(self._check_dependency_groups_documented(target_dir, dev_env))
        results.append(self._check_python_requirements_documented(target_dir, dev_env))

        # Level 3: Standardized
        results.append(self._check_devcontainer_exists(target_dir, dev_env))
        results.append(self._check_dockerfile_exists(target_dir, dev_env))
        results.append(self._check_version_pinning(target_dir, dev_env))
        results.append(self._check_setup_script_available(target_dir, dev_env))

        # Level 4: Optimized
        results.append(self._check_devcontainer_features(target_dir, dev_env))
        results.append(self._check_environment_validation(target_dir, dev_env))
        results.append(self._check_quick_start_script(target_dir, dev_env))
        results.append(self._check_ide_extensions_documented(target_dir, dev_env))

        # Level 5: Autonomous
        results.append(self._check_precommit_hooks(target_dir, dev_env))
        results.append(self._check_environment_monitoring(target_dir, dev_env))
        results.append(self._check_auto_setup_on_clone(target_dir, dev_env))
        results.append(self._check_containerized_ci(target_dir, dev_env))

        return results

    def _discover_dev_environment(self, target_dir: Path) -> dict:
        """Discover available development environment assets.

        Args:
            target_dir: Directory to scan

        Returns:
            Dict with keys for various dev environment indicators
        """
        env_example = None
        devcontainer_json = None
        dockerfile = None
        setup_scripts = []
        dependency_files = {}
        precommit_config = None
        readme_content = ""
        agents_content = ""

        # Check for .env.example
        for variant in [".env.example", ".env.sample", ".env.template"]:
            if (target_dir / variant).exists():
                env_example = target_dir / variant
                break

        # Check for devcontainer
        dc_path = target_dir / ".devcontainer" / "devcontainer.json"
        if dc_path.exists():
            devcontainer_json = dc_path

        # Check for Dockerfile
        if (target_dir / "Dockerfile").exists():
            dockerfile = target_dir / "Dockerfile"

        # Check for setup scripts
        for script in ["setup.sh", "quick-start.sh", "Makefile", "docker-compose.yml"]:
            if (target_dir / script).exists():
                setup_scripts.append(target_dir / script)

        # Check for scripts directory
        scripts_dir = target_dir / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.sh"):
                setup_scripts.append(script)

        # Check for dependency files
        for lang, files in {
            "python": ["pyproject.toml", "setup.py", "requirements.txt"],
            "node": ["package.json"],
            "rust": ["Cargo.toml"],
            "go": ["go.mod"],
        }.items():
            for file in files:
                if (target_dir / file).exists():
                    dependency_files[lang] = target_dir / file
                    break

        # Check for pre-commit config
        if (target_dir / ".pre-commit-config.yaml").exists():
            precommit_config = target_dir / ".pre-commit-config.yaml"

        # Read README and AGENTS.md
        readme = target_dir / "README.md"
        if readme.exists():
            readme_content = readme.read_text(errors="ignore").lower()

        agents = target_dir / "AGENTS.md"
        if agents.exists():
            agents_content = agents.read_text(errors="ignore").lower()

        return {
            "env_example": env_example,
            "devcontainer_json": devcontainer_json,
            "dockerfile": dockerfile,
            "setup_scripts": setup_scripts,
            "dependency_files": dependency_files,
            "precommit_config": precommit_config,
            "readme_content": readme_content,
            "agents_content": agents_content,
        }

    # Level 1: Functional

    def _check_setup_instructions_exist(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if setup instructions exist in documentation."""
        content = dev_env["readme_content"] + dev_env["agents_content"]

        # Look for setup-related keywords
        setup_keywords = [
            "install",
            "setup",
            "development",
            "develop",
            "getting started",
            "quick start",
        ]

        has_setup = any(keyword in content for keyword in setup_keywords)
        has_length = len(content) > 50

        if has_setup and has_length:
            return CheckResult(
                name="Setup instructions exist",
                passed=True,
                message="Setup instructions found in README or AGENTS.md",
                severity=Severity.REQUIRED,
                level=1,
            )
        else:
            return CheckResult(
                name="Setup instructions exist",
                passed=False,
                message="No clear setup instructions found in README or AGENTS.md",
                severity=Severity.REQUIRED,
                level=1,
            )

    def _check_dependency_file_exists(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if dependency file exists."""
        if dev_env["dependency_files"]:
            lang = list(dev_env["dependency_files"].keys())[0]
            filename = dev_env["dependency_files"][lang].name
            return CheckResult(
                name="Dependency file exists",
                passed=True,
                message=f"Dependency file found: {filename}",
                severity=Severity.REQUIRED,
                level=1,
            )
        else:
            return CheckResult(
                name="Dependency file exists",
                passed=False,
                message="No dependency file found (pyproject.toml, package.json, etc.)",
                severity=Severity.REQUIRED,
                level=1,
            )

    # Level 2: Documented

    def _check_env_example_exists(self, target_dir: Path, dev_env: dict) -> CheckResult:
        """Check if .env.example exists."""
        if dev_env["env_example"] and dev_env["env_example"].stat().st_size >= 20:
            return CheckResult(
                name=".env.example exists",
                passed=True,
                message=".env.example file found with documentation",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name=".env.example exists",
                passed=False,
                message="No .env.example file found",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_setup_steps_documented(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if setup steps are clearly documented."""
        content = dev_env["readme_content"] + dev_env["agents_content"]

        # Look for installation commands
        commands = [
            "pip install",
            "npm install",
            "cargo build",
            "go get",
            "python -m",
            "make install",
        ]

        has_commands = any(cmd in content for cmd in commands)
        has_length = len(content) > 100

        if has_commands and has_length:
            return CheckResult(
                name="Setup steps documented",
                passed=True,
                message="Setup steps clearly documented with commands",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="Setup steps documented",
                passed=False,
                message="Setup steps not clearly documented with specific commands",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_dependency_groups_documented(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if dev dependencies are separated from production."""
        passed = False

        # Check Python projects
        if "python" in dev_env["dependency_files"]:
            py_file = dev_env["dependency_files"]["python"]
            if py_file.name == "pyproject.toml":
                content = py_file.read_text(errors="ignore")
                if (
                    "[tool.poetry.group" in content
                    or "[project.optional-dependencies]" in content
                ):
                    passed = True
            elif py_file.name in ["requirements.txt", "setup.py"]:
                # Check for requirements-dev.txt
                if (target_dir / "requirements-dev.txt").exists():
                    passed = True

        # Check Node projects
        if "node" in dev_env["dependency_files"]:
            node_file = dev_env["dependency_files"]["node"]
            content = node_file.read_text(errors="ignore")
            if "devDependencies" in content:
                passed = True

        if passed:
            return CheckResult(
                name="Dependency groups documented",
                passed=True,
                message="Development dependencies properly separated",
                severity=Severity.OPTIONAL,
                level=2,
            )
        else:
            return CheckResult(
                name="Dependency groups documented",
                passed=False,
                message="Development dependencies not clearly separated",
                severity=Severity.OPTIONAL,
                level=2,
            )

    def _check_python_requirements_documented(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if Python requirements are properly documented."""
        if "python" not in dev_env["dependency_files"]:
            return CheckResult(
                name="Python requirements documented",
                passed=True,
                message="Not a Python project",
                severity=Severity.OPTIONAL,
                level=2,
            )

        py_file = dev_env["dependency_files"]["python"]

        if py_file.name == "pyproject.toml":
            try:
                content = py_file.read_text(errors="ignore")
                if "[project]" in content or "[tool.poetry]" in content:
                    return CheckResult(
                        name="Python requirements documented",
                        passed=True,
                        message="Python requirements documented in pyproject.toml",
                        severity=Severity.OPTIONAL,
                        level=2,
                    )
            except Exception:
                pass

        elif py_file.name == "requirements.txt":
            content = py_file.read_text(errors="ignore")
            if len(content.strip()) > 0:
                return CheckResult(
                    name="Python requirements documented",
                    passed=True,
                    message="Python requirements documented in requirements.txt",
                    severity=Severity.OPTIONAL,
                    level=2,
                )

        return CheckResult(
            name="Python requirements documented",
            passed=False,
            message="Python requirements not properly documented",
            severity=Severity.OPTIONAL,
            level=2,
        )

    # Level 3: Standardized

    def _check_devcontainer_exists(self, target_dir: Path, dev_env: dict) -> CheckResult:
        """Check if devcontainer configuration exists."""
        if dev_env["devcontainer_json"]:
            try:
                content = dev_env["devcontainer_json"].read_text()
                data = json.loads(content)
                if "image" in data or "build" in data:
                    return CheckResult(
                        name="Devcontainer configured",
                        passed=True,
                        message="Devcontainer configuration found",
                        severity=Severity.RECOMMENDED,
                        level=3,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Devcontainer configured",
            passed=False,
            message="No .devcontainer/devcontainer.json found",
            severity=Severity.RECOMMENDED,
            level=3,
        )

    def _check_dockerfile_exists(self, target_dir: Path, dev_env: dict) -> CheckResult:
        """Check if Dockerfile exists."""
        if dev_env["dockerfile"]:
            content = dev_env["dockerfile"].read_text(errors="ignore")

            # Check for multi-stage build
            if "FROM" in content.upper():
                return CheckResult(
                    name="Dockerfile configured",
                    passed=True,
                    message="Dockerfile found",
                    severity=Severity.OPTIONAL,
                    level=3,
                )

        return CheckResult(
            name="Dockerfile configured",
            passed=False,
            message="No Dockerfile found",
            severity=Severity.OPTIONAL,
            level=3,
        )

    def _check_version_pinning(self, target_dir: Path, dev_env: dict) -> CheckResult:
        """Check if dependency versions are pinned."""
        passed = False

        # Check for lock files
        lock_files = [
            "requirements.txt",
            "poetry.lock",
            "package-lock.json",
            "yarn.lock",
            "go.sum",
            "Cargo.lock",
        ]

        for lock_file in lock_files:
            if (target_dir / lock_file).exists():
                passed = True
                break

        # Check Python requirements.txt for pinned versions
        if "python" in dev_env["dependency_files"]:
            py_file = dev_env["dependency_files"]["python"]
            if py_file.name == "requirements.txt":
                content = py_file.read_text(errors="ignore")
                # Check if any line has == (pinned version)
                if any("==" in line for line in content.split("\n") if line.strip()):
                    passed = True

        if passed:
            return CheckResult(
                name="Version pinning configured",
                passed=True,
                message="Dependency versions pinned via lock file",
                severity=Severity.RECOMMENDED,
                level=3,
            )
        else:
            return CheckResult(
                name="Version pinning configured",
                passed=False,
                message="No dependency lock file found",
                severity=Severity.RECOMMENDED,
                level=3,
            )

    def _check_setup_script_available(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if automated setup script is available."""
        for script in dev_env["setup_scripts"]:
            if script.name == "setup.sh":
                if script.stat().st_size > 100:
                    return CheckResult(
                        name="Setup script available",
                        passed=True,
                        message=f"Setup script found: {script.name}",
                        severity=Severity.OPTIONAL,
                        level=3,
                    )

            elif script.name == "Makefile":
                content = script.read_text(errors="ignore")
                if "dev" in content or "install" in content or "setup" in content:
                    return CheckResult(
                        name="Setup script available",
                        passed=True,
                        message="Makefile with setup targets found",
                        severity=Severity.OPTIONAL,
                        level=3,
                    )

        return CheckResult(
            name="Setup script available",
            passed=False,
            message="No automated setup script found",
            severity=Severity.OPTIONAL,
            level=3,
        )

    # Level 4: Optimized

    def _check_devcontainer_features(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if devcontainer includes development extensions."""
        if not dev_env["devcontainer_json"]:
            return CheckResult(
                name="Devcontainer extensions configured",
                passed=False,
                message="No devcontainer found",
                severity=Severity.OPTIONAL,
                level=4,
            )

        try:
            content = dev_env["devcontainer_json"].read_text()
            data = json.loads(content)

            extensions = []
            if "customizations" in data and "vscode" in data["customizations"]:
                extensions = data["customizations"]["vscode"].get("extensions", [])

            # Look for common dev extensions
            dev_extension_keywords = ["ruff", "prettier", "eslint", "python", "docker"]
            has_extensions = any(
                any(keyword in ext.lower() for keyword in dev_extension_keywords)
                for ext in extensions
            )

            if has_extensions or len(extensions) >= 3:
                return CheckResult(
                    name="Devcontainer extensions configured",
                    passed=True,
                    message=f"Devcontainer configured with {len(extensions)} extensions",
                    severity=Severity.OPTIONAL,
                    level=4,
                )
        except Exception:
            pass

        return CheckResult(
            name="Devcontainer extensions configured",
            passed=False,
            message="Devcontainer lacks development extensions",
            severity=Severity.OPTIONAL,
            level=4,
        )

    def _check_environment_validation(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if environment validation script exists."""
        validation_scripts = ["verify.sh", "validate.sh", "check-env.sh"]

        for script in validation_scripts:
            if (target_dir / script).exists():
                content = (target_dir / script).read_text(errors="ignore")
                if len(content) > 100:
                    return CheckResult(
                        name="Environment validation available",
                        passed=True,
                        message=f"Validation script found: {script}",
                        severity=Severity.OPTIONAL,
                        level=4,
                    )

        # Check for Makefile validation target
        for script in dev_env["setup_scripts"]:
            if script.name == "Makefile":
                content = script.read_text(errors="ignore")
                if "validate" in content or "check-env" in content:
                    return CheckResult(
                        name="Environment validation available",
                        passed=True,
                        message="Makefile validation target found",
                        severity=Severity.OPTIONAL,
                        level=4,
                    )

        return CheckResult(
            name="Environment validation available",
            passed=False,
            message="No environment validation script found",
            severity=Severity.OPTIONAL,
            level=4,
        )

    def _check_quick_start_script(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if quick-start instructions are documented."""
        content = dev_env["readme_content"] + dev_env["agents_content"]

        # Look for quick start section with code block
        quick_start_patterns = [
            r"quick.?start.*```",
            r"get started.*```",
            r"```.*git clone.*&&.*cd",
        ]

        for pattern in quick_start_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return CheckResult(
                    name="Quick-start instructions available",
                    passed=True,
                    message="Quick-start setup documented",
                    severity=Severity.OPTIONAL,
                    level=4,
                )

        # Check for quick-start.sh script
        if (target_dir / "quick-start.sh").exists():
            return CheckResult(
                name="Quick-start instructions available",
                passed=True,
                message="Quick-start script found",
                severity=Severity.OPTIONAL,
                level=4,
            )

        return CheckResult(
            name="Quick-start instructions available",
            passed=False,
            message="No quick-start command documented",
            severity=Severity.OPTIONAL,
            level=4,
        )

    def _check_ide_extensions_documented(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if IDE extension recommendations are documented."""
        content = dev_env["readme_content"] + dev_env["agents_content"]

        # Check for VS Code extensions mention
        if "vs code" in content or "extension" in content or "editor" in content:
            return CheckResult(
                name="IDE extensions documented",
                passed=True,
                message="IDE extension recommendations found",
                severity=Severity.OPTIONAL,
                level=4,
            )

        # Check for .vscode/extensions.json
        if (target_dir / ".vscode" / "extensions.json").exists():
            return CheckResult(
                name="IDE extensions documented",
                passed=True,
                message="VS Code extensions.json found",
                severity=Severity.OPTIONAL,
                level=4,
            )

        return CheckResult(
            name="IDE extensions documented",
            passed=False,
            message="No IDE extension recommendations found",
            severity=Severity.OPTIONAL,
            level=4,
        )

    # Level 5: Autonomous

    def _check_precommit_hooks(self, target_dir: Path, dev_env: dict) -> CheckResult:
        """Check if pre-commit hooks are configured."""
        if not dev_env["precommit_config"]:
            return CheckResult(
                name="Pre-commit hooks configured",
                passed=False,
                message="No .pre-commit-config.yaml found",
                severity=Severity.OPTIONAL,
                level=5,
            )

        try:
            import yaml

            content = dev_env["precommit_config"].read_text()
            data = yaml.safe_load(content)

            if isinstance(data, dict) and "repos" in data:
                repos = data.get("repos", [])
                if len(repos) >= 2:
                    return CheckResult(
                        name="Pre-commit hooks configured",
                        passed=True,
                        message=f"Pre-commit hooks configured with {len(repos)} repos",
                        severity=Severity.OPTIONAL,
                        level=5,
                    )
        except Exception:
            # If yaml parsing fails, still try basic check
            content = dev_env["precommit_config"].read_text(errors="ignore")
            if "repos:" in content and content.count("-"):
                return CheckResult(
                    name="Pre-commit hooks configured",
                    passed=True,
                    message="Pre-commit hooks configured",
                    severity=Severity.OPTIONAL,
                    level=5,
                )

        return CheckResult(
            name="Pre-commit hooks configured",
            passed=False,
            message="Pre-commit configuration incomplete",
            severity=Severity.OPTIONAL,
            level=5,
        )

    def _check_environment_monitoring(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if environment monitoring script exists."""
        monitoring_scripts = ["monitor.sh", "health-check.sh", "check-health.sh"]

        for script in monitoring_scripts:
            if (target_dir / script).exists():
                content = (target_dir / script).read_text(errors="ignore")
                if len(content) > 100:
                    return CheckResult(
                        name="Environment monitoring available",
                        passed=True,
                        message=f"Monitoring script found: {script}",
                        severity=Severity.OPTIONAL,
                        level=5,
                    )

        return CheckResult(
            name="Environment monitoring available",
            passed=False,
            message="No environment monitoring script found",
            severity=Severity.OPTIONAL,
            level=5,
        )

    def _check_auto_setup_on_clone(
        self, target_dir: Path, dev_env: dict
    ) -> CheckResult:
        """Check if automatic setup runs on clone."""
        # Check for post-checkout hook
        git_hooks = target_dir / ".git" / "hooks"
        if git_hooks.exists():
            for hook in ["post-checkout", "post-merge"]:
                if (git_hooks / hook).exists():
                    return CheckResult(
                        name="Auto setup on clone configured",
                        passed=True,
                        message=f"Git {hook} hook found",
                        severity=Severity.OPTIONAL,
                        level=5,
                    )

        # Check for husky configuration
        if (target_dir / ".husky" / "post-checkout").exists():
            return CheckResult(
                name="Auto setup on clone configured",
                passed=True,
                message="Husky post-checkout hook found",
                severity=Severity.OPTIONAL,
                level=5,
            )

        return CheckResult(
            name="Auto setup on clone configured",
            passed=False,
            message="No automatic setup on clone configured",
            severity=Severity.OPTIONAL,
            level=5,
        )

    def _check_containerized_ci(self, target_dir: Path, dev_env: dict) -> CheckResult:
        """Check if CI uses containerized environment."""
        # Check GitHub Actions
        workflows_dir = target_dir / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                content = workflow_file.read_text(errors="ignore")
                if "container:" in content or "docker" in content.lower():
                    return CheckResult(
                        name="Containerized CI configured",
                        passed=True,
                        message="CI uses containerized environment",
                        severity=Severity.OPTIONAL,
                        level=5,
                    )

        # Check GitLab CI
        if (target_dir / ".gitlab-ci.yml").exists():
            content = (target_dir / ".gitlab-ci.yml").read_text(errors="ignore")
            if "image:" in content or "docker" in content.lower():
                return CheckResult(
                    name="Containerized CI configured",
                    passed=True,
                    message="GitLab CI uses containerized environment",
                    severity=Severity.OPTIONAL,
                    level=5,
                )

        return CheckResult(
            name="Containerized CI configured",
            passed=False,
            message="CI does not use containerized environment",
            severity=Severity.OPTIONAL,
            level=5,
        )
