"""Security pillar implementation."""

import re
from pathlib import Path

from agent_readiness.pillar import Pillar
from agent_readiness.models import CheckResult, Severity


class SecurityPillar(Pillar):
    """Evaluates security practices and vulnerability management."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Security"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for security checks."""
        results = []

        # Discover security assets
        sec = self._discover_security_setup(target_dir)

        # Level 1: Functional
        results.append(self._check_dependency_file_exists(target_dir, sec))
        results.append(self._check_secrets_not_in_code(target_dir, sec))

        # Level 2: Documented
        results.append(self._check_security_documentation(target_dir, sec))
        results.append(self._check_dependency_management_documented(target_dir, sec))
        results.append(self._check_secret_management_documented(target_dir, sec))
        results.append(self._check_access_control_documented(target_dir, sec))

        # Level 3: Standardized
        results.append(self._check_dependency_lock_file(target_dir, sec))
        results.append(self._check_vulnerability_scanning_configured(target_dir, sec))
        results.append(self._check_secrets_management_tool(target_dir, sec))
        results.append(self._check_input_validation_present(target_dir, sec))

        # Level 4: Optimized
        results.append(self._check_sast_configured(target_dir, sec))
        results.append(self._check_dependency_scanning_in_ci(target_dir, sec))
        results.append(self._check_encryption_indicators(target_dir, sec))
        results.append(self._check_security_testing(target_dir, sec))

        # Level 5: Autonomous
        results.append(self._check_secrets_scanning_in_ci(target_dir, sec))
        results.append(self._check_automated_security_updates(target_dir, sec))
        results.append(self._check_runtime_security(target_dir, sec))
        results.append(self._check_threat_modeling(target_dir, sec))

        return results

    def _discover_security_setup(self, target_dir: Path) -> dict:
        """Discover available security infrastructure.

        Args:
            target_dir: Directory to scan

        Returns:
            Dict with security configuration information
        """
        dependency_files = []
        lock_files = []
        secret_patterns_found = {}
        has_security_doc = False
        sast_config = {}
        dependency_scanning_tools = set()
        env_file_patterns = []
        ci_config = []
        encryption_indicators = set()
        test_files = []
        readme_content = ""
        agents_content = ""
        source_files = []

        # Find dependency files
        for dep_file in [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "Gemfile",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "Pipfile",
        ]:
            if (target_dir / dep_file).exists():
                dependency_files.append(dep_file)

        # Find lock files
        for lock_file in [
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "Cargo.lock",
            "go.sum",
            "Gemfile.lock",
            "poetry.lock",
            "requirements.lock",
            "Pipfile.lock",
        ]:
            if (target_dir / lock_file).exists():
                lock_files.append(lock_file)

        # Check for security documentation
        if (target_dir / "SECURITY.md").exists():
            has_security_doc = True

        # Check README for security section
        readme_path = target_dir / "README.md"
        if readme_path.exists():
            readme_content = readme_path.read_text(errors="ignore")
            if "security" in readme_content.lower():
                has_security_doc = True

        # Check AGENTS.md
        agents_path = target_dir / "AGENTS.md"
        if agents_path.exists():
            agents_content = agents_path.read_text(errors="ignore")

        # Find .env patterns
        for env_file in [".env", ".env.example", ".env.local"]:
            if (target_dir / env_file).exists():
                env_file_patterns.append(env_file)

        # Find SAST configurations
        sast_files = {
            ".bandit": "bandit",
            ".eslintrc": "eslint",
            ".eslintrc.json": "eslint",
            ".eslintrc.yml": "eslint",
            "sonarqube-project.properties": "sonarqube",
            ".codeclimate.yml": "codeclimate",
            "golangci.yml": "golangci-lint",
            "clippy.toml": "clippy",
            ".pylintrc": "pylint",
        }
        for config_file, tool_name in sast_files.items():
            if (target_dir / config_file).exists():
                sast_config[tool_name] = config_file

        # Check CI configurations
        ci_files = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".circleci/config.yml",
            ".travis.yml",
            "Jenkinsfile",
        ]
        for ci_file in ci_files:
            ci_path = target_dir / ci_file
            if ci_path.exists():
                ci_config.append(ci_file)
                # Check for security scanning in CI
                if ci_path.is_file():
                    try:
                        content = ci_path.read_text(errors="ignore")
                        if any(
                            tool in content
                            for tool in [
                                "npm audit",
                                "pip-audit",
                                "cargo audit",
                                "safety",
                                "snyk",
                                "dependabot",
                                "renovate",
                            ]
                        ):
                            dependency_scanning_tools.add(ci_file)
                    except Exception:
                        pass
                elif ci_path.is_dir():
                    for workflow_file in ci_path.rglob("*.yml"):
                        try:
                            content = workflow_file.read_text(errors="ignore")
                            if any(
                                tool in content
                                for tool in [
                                    "npm audit",
                                    "pip-audit",
                                    "cargo audit",
                                    "safety",
                                    "snyk",
                                    "dependabot",
                                    "renovate",
                                ]
                            ):
                                dependency_scanning_tools.add(workflow_file.name)
                        except Exception:
                            pass

        # Check package.json/requirements.txt for audit scripts
        if (target_dir / "package.json").exists():
            try:
                import json

                pkg = json.loads((target_dir / "package.json").read_text())
                if "scripts" in pkg:
                    for script_name, script in pkg.get("scripts", {}).items():
                        if "audit" in script or "snyk" in script:
                            dependency_scanning_tools.add("npm audit")
                            break
            except Exception:
                pass

        # Scan for encryption indicators
        encryption_patterns = [
            "bcrypt",
            "argon2",
            "cryptography",
            "pycryptodome",
            "PyCrypto",
            "hashlib",
            "ssl",
            "tls",
            "RSA",
            "AES",
            "sodium",
            "nacl",
        ]

        # Check package.json and requirements.txt
        if (target_dir / "package.json").exists():
            try:
                import json

                pkg = json.loads((target_dir / "package.json").read_text())
                for dep in list(pkg.get("dependencies", {}).keys()) + list(
                    pkg.get("devDependencies", {}).keys()
                ):
                    if any(pattern.lower() in dep.lower() for pattern in encryption_patterns):
                        encryption_indicators.add(dep)
            except Exception:
                pass

        if (target_dir / "requirements.txt").exists():
            try:
                reqs = (target_dir / "requirements.txt").read_text(errors="ignore")
                for pattern in encryption_patterns:
                    if pattern.lower() in reqs.lower():
                        encryption_indicators.add(pattern)
            except Exception:
                pass

        # Scan source files for encryption imports
        for py_file in list(target_dir.rglob("*.py"))[:50]:
            try:
                content = py_file.read_text(errors="ignore")
                for pattern in encryption_patterns:
                    if pattern in content:
                        encryption_indicators.add(pattern)
                        break
            except Exception:
                pass

        for js_file in list(target_dir.rglob("*.js"))[:50]:
            try:
                content = js_file.read_text(errors="ignore")
                for pattern in encryption_patterns:
                    if pattern.lower() in content.lower():
                        encryption_indicators.add(pattern)
                        break
            except Exception:
                pass

        # Find test files
        for test_file in target_dir.rglob("test*.py"):
            test_files.append(str(test_file))
        for test_file in target_dir.rglob("*.test.js"):
            test_files.append(str(test_file))
        for test_file in target_dir.rglob("*.spec.js"):
            test_files.append(str(test_file))

        # Collect source files
        for py_file in list(target_dir.rglob("*.py"))[:100]:
            if "test" not in py_file.name and "__pycache__" not in str(py_file):
                source_files.append(py_file)
        for js_file in list(target_dir.rglob("*.js"))[:100]:
            if "test" not in js_file.name and "node_modules" not in str(js_file):
                source_files.append(js_file)

        return {
            "dependency_files": dependency_files,
            "lock_files": lock_files,
            "secret_patterns_found": secret_patterns_found,
            "has_security_doc": has_security_doc,
            "sast_config": sast_config,
            "dependency_scanning_tools": list(dependency_scanning_tools),
            "env_file_patterns": env_file_patterns,
            "ci_config": ci_config,
            "encryption_indicators": list(encryption_indicators),
            "test_files": test_files,
            "readme_content": readme_content,
            "agents_content": agents_content,
            "source_files": source_files,
        }

    # Level 1: Functional

    def _check_dependency_file_exists(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if dependency management file exists."""
        passed = bool(sec["dependency_files"])
        files_found = ", ".join(sec["dependency_files"]) if sec["dependency_files"] else "none"
        return CheckResult(
            name="Dependency file exists",
            passed=passed,
            message=f"Dependency files found: {files_found}"
            if passed
            else "No dependency management file found (package.json, requirements.txt, etc.)",
            severity=Severity.REQUIRED,
            level=1,
            metadata={"files": sec["dependency_files"]},
        )

    def _check_secrets_not_in_code(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check that secrets are not exposed in code."""
        secret_patterns = [
            r"(?i)(aws_secret_access_key|private_key|api_key)\s*=\s*['\"][^'\"]*['\"]",
            r"-----BEGIN RSA PRIVATE KEY-----",
            r"-----BEGIN PRIVATE KEY-----",
            r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{0,1000}['\"]",
        ]

        secrets_found = False
        checked_files = 0

        # Sample source files
        for py_file in list(target_dir.rglob("*.py"))[:50]:
            if "test" in py_file.name or "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(errors="ignore")
                checked_files += 1
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        secrets_found = True
                        break
            except Exception:
                pass

        for js_file in list(target_dir.rglob("*.js"))[:50]:
            if "test" in js_file.name or "node_modules" in str(js_file):
                continue
            try:
                content = js_file.read_text(errors="ignore")
                checked_files += 1
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        secrets_found = True
                        break
            except Exception:
                pass

        return CheckResult(
            name="Secrets not in code",
            passed=not secrets_found,
            message="No obvious secrets detected in code"
            if not secrets_found
            else "Potential secrets detected in code",
            severity=Severity.REQUIRED,
            level=1,
            metadata={"files_checked": checked_files},
        )

    # Level 2: Documented

    def _check_security_documentation(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if security documentation exists."""
        passed = sec["has_security_doc"]
        return CheckResult(
            name="Security documentation exists",
            passed=passed,
            message="Security documentation found (SECURITY.md or README section)"
            if passed
            else "No security documentation found",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={"has_security_md": (target_dir / "SECURITY.md").exists()},
        )

    def _check_dependency_management_documented(
        self, target_dir: Path, sec: dict
    ) -> CheckResult:
        """Check if dependency management is documented."""
        readme_mentions = False
        agents_mentions = False
        security_mentions = False

        readme = sec["readme_content"].lower()
        if any(
            phrase in readme
            for phrase in [
                "dependency",
                "update",
                "install",
                "requirements",
                "package",
            ]
        ):
            readme_mentions = True

        agents = sec["agents_content"].lower()
        if any(
            phrase in agents
            for phrase in [
                "dependency",
                "update",
                "install",
                "requirements",
                "package",
            ]
        ):
            agents_mentions = True

        security_doc_path = target_dir / "SECURITY.md"
        if security_doc_path.exists():
            security_content = security_doc_path.read_text(errors="ignore").lower()
            if any(
                phrase in security_content
                for phrase in [
                    "dependency",
                    "update",
                    "install",
                    "requirements",
                    "package",
                ]
            ):
                security_mentions = True

        passed = readme_mentions or agents_mentions or security_mentions

        return CheckResult(
            name="Dependency management documented",
            passed=passed,
            message="Dependency management process documented"
            if passed
            else "Dependency management process not documented",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={"in_readme": readme_mentions, "in_agents": agents_mentions},
        )

    def _check_secret_management_documented(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if secret management is documented."""
        has_env_example = ".env.example" in sec["env_file_patterns"]

        readme = sec["readme_content"].lower()
        agents = sec["agents_content"].lower()

        readme_mentions = any(
            phrase in readme for phrase in ["environment", "secret", "api", "key", "env"]
        )
        agents_mentions = any(
            phrase in agents for phrase in ["environment", "secret", "api", "key", "env"]
        )

        security_doc_path = target_dir / "SECURITY.md"
        security_mentions = False
        if security_doc_path.exists():
            content = security_doc_path.read_text(errors="ignore").lower()
            security_mentions = any(
                phrase in content for phrase in ["environment", "secret", "api", "key", "env"]
            )

        passed = has_env_example or readme_mentions or agents_mentions or security_mentions

        return CheckResult(
            name="Secret management documented",
            passed=passed,
            message="Secret management documented (.env.example, README, etc.)"
            if passed
            else "Secret management approach not documented",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={"has_env_example": has_env_example},
        )

    def _check_access_control_documented(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if access control is documented."""
        readme = sec["readme_content"].lower()
        agents = sec["agents_content"].lower()

        readme_mentions = any(
            phrase in readme
            for phrase in ["auth", "permission", "role", "access", "user", "jwt", "oauth"]
        )
        agents_mentions = any(
            phrase in agents
            for phrase in ["auth", "permission", "role", "access", "user", "jwt", "oauth"]
        )

        security_doc_path = target_dir / "SECURITY.md"
        security_mentions = False
        if security_doc_path.exists():
            content = security_doc_path.read_text(errors="ignore").lower()
            security_mentions = any(
                phrase in content
                for phrase in ["auth", "permission", "role", "access", "user", "jwt", "oauth"]
            )

        passed = readme_mentions or agents_mentions or security_mentions

        return CheckResult(
            name="Access control documented",
            passed=passed,
            message="Access control/authentication approach documented"
            if passed
            else "Access control approach not documented",
            severity=Severity.RECOMMENDED,
            level=2,
            metadata={"in_readme": readme_mentions},
        )

    # Level 3: Standardized

    def _check_dependency_lock_file(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if dependency lock file exists."""
        passed = bool(sec["lock_files"])
        files = ", ".join(sec["lock_files"]) if sec["lock_files"] else "none"
        return CheckResult(
            name="Dependency lock file present",
            passed=passed,
            message=f"Lock file found: {files}"
            if passed
            else "No dependency lock file found (package-lock.json, Cargo.lock, etc.)",
            severity=Severity.REQUIRED,
            level=3,
            metadata={"files": sec["lock_files"]},
        )

    def _check_vulnerability_scanning_configured(
        self, target_dir: Path, sec: dict
    ) -> CheckResult:
        """Check if vulnerability scanning is configured."""
        tools_found = []

        # Check package.json for audit script
        if (target_dir / "package.json").exists():
            try:
                import json

                pkg = json.loads((target_dir / "package.json").read_text())
                if "scripts" in pkg:
                    for script_name, script in pkg.get("scripts", {}).items():
                        if "audit" in script or "snyk" in script:
                            tools_found.append("npm audit")
                            break
            except Exception:
                pass

        # Check for vulnerability scanning tools in dependencies
        if (target_dir / "requirements.txt").exists():
            content = (target_dir / "requirements.txt").read_text(errors="ignore")
            if "pip-audit" in content or "safety" in content:
                tools_found.append("pip-audit/safety")

        # Check setup.py or pyproject.toml
        if (target_dir / "setup.py").exists():
            content = (target_dir / "setup.py").read_text(errors="ignore")
            if "audit" in content.lower() or "safety" in content.lower():
                tools_found.append("pip-audit")

        if (target_dir / "pyproject.toml").exists():
            content = (target_dir / "pyproject.toml").read_text(errors="ignore")
            if "audit" in content.lower() or "safety" in content.lower():
                tools_found.append("pip-audit")

        # Check Cargo.toml
        if (target_dir / "Cargo.toml").exists():
            content = (target_dir / "Cargo.toml").read_text(errors="ignore")
            if "cargo-audit" in content.lower():
                tools_found.append("cargo-audit")

        passed = bool(tools_found)
        tools_str = ", ".join(set(tools_found)) if tools_found else "none"

        return CheckResult(
            name="Vulnerability scanning configured",
            passed=passed,
            message=f"Vulnerability scanning tool found: {tools_str}"
            if passed
            else "No vulnerability scanning tool configured",
            severity=Severity.REQUIRED,
            level=3,
            metadata={"tools": list(set(tools_found))},
        )

    def _check_secrets_management_tool(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if secrets management is configured."""
        has_env = bool(sec["env_file_patterns"])

        # Check for dotenv patterns in source code
        dotenv_patterns_found = False
        for py_file in list(target_dir.rglob("*.py"))[:30]:
            try:
                content = py_file.read_text(errors="ignore")
                if "dotenv" in content or "load_dotenv" in content or "os.environ" in content:
                    dotenv_patterns_found = True
                    break
            except Exception:
                pass

        for js_file in list(target_dir.rglob("*.js"))[:30]:
            try:
                content = js_file.read_text(errors="ignore")
                if "dotenv" in content or "process.env" in content:
                    dotenv_patterns_found = True
                    break
            except Exception:
                pass

        passed = has_env or dotenv_patterns_found

        return CheckResult(
            name="Secrets management tool present",
            passed=passed,
            message="Secrets management configured (.env pattern, dotenv, etc.)"
            if passed
            else "No secrets management approach found",
            severity=Severity.REQUIRED,
            level=3,
            metadata={"has_env_files": has_env, "has_dotenv_pattern": dotenv_patterns_found},
        )

    def _check_input_validation_present(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if input validation is present."""
        validation_patterns = [
            "pydantic",
            "marshmallow",
            "validator",
            "joi",
            "yup",
            "zod",
            "express-validator",
            "govalidator",
            "serde",
        ]

        found_validations = set()

        # Check requirements.txt
        if (target_dir / "requirements.txt").exists():
            content = (target_dir / "requirements.txt").read_text(errors="ignore")
            for pattern in validation_patterns:
                if pattern.lower() in content.lower():
                    found_validations.add(pattern)

        # Check package.json
        if (target_dir / "package.json").exists():
            try:
                import json

                pkg = json.loads((target_dir / "package.json").read_text())
                for dep in list(pkg.get("dependencies", {}).keys()) + list(
                    pkg.get("devDependencies", {}).keys()
                ):
                    if any(pattern.lower() in dep.lower() for pattern in validation_patterns):
                        found_validations.add(dep)
            except Exception:
                pass

        # Check source files for validation patterns
        for py_file in list(target_dir.rglob("*.py"))[:30]:
            try:
                content = py_file.read_text(errors="ignore")
                for pattern in ["pydantic", "marshmallow", "validator", "isinstance"]:
                    if pattern in content:
                        found_validations.add("manual-validation")
                        break
            except Exception:
                pass

        for js_file in list(target_dir.rglob("*.js"))[:30]:
            try:
                content = js_file.read_text(errors="ignore")
                for pattern in ["joi", "yup", "zod", "validator"]:
                    if pattern in content:
                        found_validations.add("client-validation")
                        break
            except Exception:
                pass

        passed = bool(found_validations)
        tools_str = ", ".join(sorted(found_validations)) if found_validations else "none"

        return CheckResult(
            name="Input validation present",
            passed=passed,
            message=f"Input validation found: {tools_str}"
            if passed
            else "No input validation detected",
            severity=Severity.REQUIRED,
            level=3,
            metadata={"tools": list(found_validations)},
        )

    # Level 4: Optimized

    def _check_sast_configured(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if SAST tool is configured."""
        tools_found = list(sec["sast_config"].keys())
        passed = bool(tools_found)
        tools_str = ", ".join(sorted(tools_found)) if tools_found else "none"

        return CheckResult(
            name="SAST tool configured",
            passed=passed,
            message=f"SAST tool found: {tools_str}"
            if passed
            else "No SAST tool configured",
            severity=Severity.RECOMMENDED,
            level=4,
            metadata={"tools": tools_found},
        )

    def _check_dependency_scanning_in_ci(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if dependency scanning is in CI."""
        tools_found = sec["dependency_scanning_tools"]
        passed = bool(tools_found)
        tools_str = ", ".join(sorted(tools_found)) if tools_found else "none"

        return CheckResult(
            name="Dependency scanning in CI",
            passed=passed,
            message=f"Dependency scanning in CI: {tools_str}"
            if passed
            else "Dependency scanning not configured in CI",
            severity=Severity.RECOMMENDED,
            level=4,
            metadata={"tools": tools_found},
        )

    def _check_encryption_indicators(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if encryption is indicated in the project."""
        indicators = sec["encryption_indicators"]
        passed = bool(indicators)
        indicators_str = ", ".join(sorted(indicators)) if indicators else "none"

        return CheckResult(
            name="Encryption indicators present",
            passed=passed,
            message=f"Encryption indicators found: {indicators_str}"
            if passed
            else "No encryption indicators found",
            severity=Severity.RECOMMENDED,
            level=4,
            metadata={"indicators": list(indicators)},
        )

    def _check_security_testing(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if security testing is present."""
        security_test_found = False

        auth_patterns = ["auth", "access", "permission", "login", "jwt"]

        for test_file in sec["test_files"]:
            try:
                content = Path(test_file).read_text(errors="ignore")
                for pattern in auth_patterns:
                    if pattern in content.lower():
                        security_test_found = True
                        break
            except Exception:
                pass
            if security_test_found:
                break

        return CheckResult(
            name="Security testing present",
            passed=security_test_found,
            message="Security tests found (auth, access control, etc.)"
            if security_test_found
            else "No security testing found",
            severity=Severity.RECOMMENDED,
            level=4,
            metadata={"test_files_checked": len(sec["test_files"])},
        )

    # Level 5: Autonomous

    def _check_secrets_scanning_in_ci(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if secrets scanning is in CI."""
        secrets_scanning_found = False

        secret_tools = ["git-secrets", "trufflehog", "detect-secrets", "gitleaks"]

        for ci_file in sec["ci_config"]:
            ci_path = target_dir / ci_file
            try:
                if ci_path.is_file():
                    content = ci_path.read_text(errors="ignore")
                    for tool in secret_tools:
                        if tool in content:
                            secrets_scanning_found = True
                            break
                elif ci_path.is_dir():
                    for workflow_file in ci_path.rglob("*.yml"):
                        content = workflow_file.read_text(errors="ignore")
                        for tool in secret_tools:
                            if tool in content:
                                secrets_scanning_found = True
                                break
            except Exception:
                pass
            if secrets_scanning_found:
                break

        # Check .pre-commit-config.yaml
        precommit_path = target_dir / ".pre-commit-config.yaml"
        if precommit_path.exists():
            try:
                content = precommit_path.read_text(errors="ignore")
                for tool in secret_tools:
                    if tool in content:
                        secrets_scanning_found = True
                        break
            except Exception:
                pass

        return CheckResult(
            name="Secrets scanning in CI",
            passed=secrets_scanning_found,
            message="Secrets scanning in CI (git-secrets, TruffleHog, etc.)"
            if secrets_scanning_found
            else "No secrets scanning in CI",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={},
        )

    def _check_automated_security_updates(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if automated security updates are configured."""
        tools_found = []

        # Check for Dependabot
        if (target_dir / ".github" / "dependabot.yml").exists():
            tools_found.append("dependabot")

        # Check for Renovate
        if (target_dir / ".renovaterc").exists():
            tools_found.append("renovate")
        if (target_dir / "renovate.json").exists():
            tools_found.append("renovate")

        passed = bool(tools_found)
        tools_str = ", ".join(sorted(set(tools_found))) if tools_found else "none"

        return CheckResult(
            name="Automated security updates configured",
            passed=passed,
            message=f"Automated updates configured: {tools_str}"
            if passed
            else "No automated dependency update configuration",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={"tools": list(set(tools_found))},
        )

    def _check_runtime_security(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if runtime security measures are indicated."""
        runtime_indicators = [
            "waf",
            "rate_limit",
            "rate-limit",
            "ratelimit",
            "intrusion",
            "security-header",
            "helmet",
            "cors",
            "csrf",
            "ddos",
        ]

        found = False

        # Check source files
        for source_file in sec["source_files"][:30]:
            try:
                content = source_file.read_text(errors="ignore")
                for indicator in runtime_indicators:
                    if indicator in content.lower():
                        found = True
                        break
            except Exception:
                pass
            if found:
                break

        # Check README
        readme = sec["readme_content"].lower()
        for indicator in runtime_indicators:
            if indicator in readme:
                found = True
                break

        return CheckResult(
            name="Runtime security measures present",
            passed=found,
            message="Runtime security measures found (WAF, rate limiting, etc.)"
            if found
            else "No runtime security measures indicated",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={},
        )

    def _check_threat_modeling(self, target_dir: Path, sec: dict) -> CheckResult:
        """Check if threat modeling is documented."""
        threat_model_found = False
        files_to_check = [
            "THREAT_MODEL.md",
            "ARCHITECTURE.md",
            "docs/THREAT_MODEL.md",
            "docs/ARCHITECTURE.md",
            "docs/security/THREAT_MODEL.md",
        ]

        for file_path in files_to_check:
            if (target_dir / file_path).exists():
                threat_model_found = True
                break

        # Check for architecture or security docs in general
        if not threat_model_found:
            docs_dir = target_dir / "docs"
            if docs_dir.exists():
                for doc_file in docs_dir.rglob("*.md"):
                    try:
                        content = doc_file.read_text(errors="ignore")
                        if any(
                            phrase in content.lower()
                            for phrase in [
                                "threat",
                                "architecture",
                                "attack",
                                "vulnerability",
                                "owasp",
                            ]
                        ):
                            threat_model_found = True
                            break
                    except Exception:
                        pass

        return CheckResult(
            name="Threat modeling documented",
            passed=threat_model_found,
            message="Threat model or security architecture documented"
            if threat_model_found
            else "No threat model or security architecture documented",
            severity=Severity.OPTIONAL,
            level=5,
            metadata={},
        )
