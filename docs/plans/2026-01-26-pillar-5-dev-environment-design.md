# Pillar 5: Dev Environment Design Document

**Date**: January 26, 2026
**Status**: In Progress
**Coverage Target**: 85%+
**Test Count Target**: 30+ tests

## Overview

The **Dev Environment Pillar** evaluates how well a codebase supports rapid onboarding and consistent development environments for AI coding agents. Good dev environment setup means:

- Developers can get started in minutes, not hours
- All environments (local, CI, devcontainer) are reproducible
- Dependencies are explicitly managed
- Setup scripts are automated where possible
- IDE/editor configuration is documented

## What We're Measuring

### Level 1: Functional (Basic Dev Environment)
**Goal**: Basic development can happen, though with friction

Checks:
- ✅ **Has setup instructions**: README or AGENTS.md mentions how to set up dev environment
- ✅ **Has dependency file**: pyproject.toml, package.json, Cargo.toml, or go.mod exists

### Level 2: Documented (Environment Documentation)
**Goal**: New developers can follow clear setup steps

Checks:
- ✅ **.env.example exists**: Template for environment variables
- ✅ **Setup steps documented**: Clear installation/setup section in README
- ✅ **Dependency groups documented**: Dev dependencies clearly separated from production
- ✅ **Python requirements documented**: requirements.txt, pyproject.toml, or Pipfile

### Level 3: Standardized (Reproducible Environment)
**Goal**: Development environment is reproducible and consistent

Checks:
- ✅ **Devcontainer exists**: .devcontainer/devcontainer.json configured
- ✅ **Dockerfile exists**: Multi-stage Dockerfile with development setup
- ✅ **Version pinning**: Dependencies have explicit versions in lock file or requirements
- ✅ **Setup script available**: setup.sh, Makefile, or script that automates setup

### Level 4: Optimized (Fast & Validated Environment)
**Goal**: Development environment setup is fast and validates its own health

Checks:
- ✅ **Devcontainer features**: Includes common extensions (linter, formatter, debugger)
- ✅ **Environment validation**: Script or makefile target that verifies setup
- ✅ **Quick start script**: One-command setup that handles all dependencies
- ✅ **IDE extensions documented**: Editor configurations for Python/JS/etc. setup

### Level 5: Autonomous (Self-Healing Environment)
**Goal**: Development environment auto-fixes problems and maintains itself

Checks:
- ✅ **Pre-commit hooks configured**: Automatic code quality checks before commits
- ✅ **Environment monitoring**: Script that detects and alerts about environment issues
- ✅ **Auto-setup on clone**: git clone → automatic environment setup
- ✅ **Containerized CI**: CI runs in same container as local dev for consistency

## Architecture

### Class Structure

```python
class DevEnvironmentPillar(Pillar):
    name: str = "Dev Environment"
    weight: float = 1.0

    # Discovery
    def _discover_dev_environment(target_dir: Path) -> dict

    # Level 1: Functional
    def _check_setup_instructions_exist(target_dir: Path) -> CheckResult
    def _check_dependency_file_exists(target_dir: Path) -> CheckResult

    # Level 2: Documented
    def _check_env_example_exists(target_dir: Path) -> CheckResult
    def _check_setup_steps_documented(target_dir: Path) -> CheckResult
    def _check_dependency_groups_documented(target_dir: Path) -> CheckResult
    def _check_python_requirements_documented(target_dir: Path) -> CheckResult

    # Level 3: Standardized
    def _check_devcontainer_exists(target_dir: Path) -> CheckResult
    def _check_dockerfile_exists(target_dir: Path) -> CheckResult
    def _check_version_pinning(target_dir: Path) -> CheckResult
    def _check_setup_script_available(target_dir: Path) -> CheckResult

    # Level 4: Optimized
    def _check_devcontainer_features(target_dir: Path) -> CheckResult
    def _check_environment_validation(target_dir: Path) -> CheckResult
    def _check_quick_start_script(target_dir: Path) -> CheckResult
    def _check_ide_extensions_documented(target_dir: Path) -> CheckResult

    # Level 5: Autonomous
    def _check_precommit_hooks(target_dir: Path) -> CheckResult
    def _check_environment_monitoring(target_dir: Path) -> CheckResult
    def _check_auto_setup_on_clone(target_dir: Path) -> CheckResult
    def _check_containerized_ci(target_dir: Path) -> CheckResult
```

### Discovery Logic (`_discover_dev_environment`)

Returns dict with keys:
- `env_example`: Path to .env.example if exists
- `devcontainer_json`: Path to .devcontainer/devcontainer.json if exists
- `dockerfile`: Path to Dockerfile if exists
- `setup_scripts`: List of setup.sh, Makefile, docker-compose.yml
- `dependency_files`: Dict of language → dependency file path
- `precommit_config`: Path to .pre-commit-config.yaml if exists
- `readme_content`: Content of README.md for text searching
- `agents_content`: Content of AGENTS.md for text searching

## Detailed Check Implementations

### Level 1

#### _check_setup_instructions_exist
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Look for "install", "setup", "development" sections in README or AGENTS.md
  - Accept case-insensitive section headers
  - Minimum 50 characters of content
- **Failure message**: "No setup instructions found in README or AGENTS.md"
- **Pass message**: "Setup instructions documented in README or AGENTS.md"

#### _check_dependency_file_exists
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Check for: pyproject.toml, setup.py, requirements.txt (Python)
  - Check for: package.json (Node)
  - Check for: Cargo.toml (Rust)
  - Check for: go.mod (Go)
  - At least one must exist
- **Failure message**: "No dependency file found (pyproject.toml, package.json, etc.)"
- **Pass message**: "Dependency file found: {filename}"

### Level 2

#### _check_env_example_exists
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Look for .env.example, .env.sample, .env.template
  - Minimum 20 bytes (not empty)
- **Failure message**: "No .env.example file found"
- **Pass message**: ".env.example file found"

#### _check_setup_steps_documented
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Look for "pip install", "npm install", "cargo build" commands in README
  - Or look for numbered steps in setup section
  - Minimum 100 characters of setup documentation
- **Failure message**: "Setup steps not clearly documented"
- **Pass message**: "Setup steps clearly documented with commands"

#### _check_dependency_groups_documented
- **Severity**: OPTIONAL
- **Level**: 2
- **Logic**:
  - For Python: Check pyproject.toml for [tool.poetry.group.dev] or extras in [project.optional-dependencies]
  - For Node: Check package.json for devDependencies vs dependencies
  - For others: Look for documentation in README
- **Failure message**: "Development dependencies not separated from production"
- **Pass message**: "Development dependencies properly separated"

#### _check_python_requirements_documented
- **Severity**: OPTIONAL
- **Level**: 2
- **Logic**:
  - If Python project: Check for requirements.txt, requirements-dev.txt, or pyproject.toml
  - If found, validate syntax (can parse as requirements)
- **Failure message**: "Python requirements not properly documented"
- **Pass message**: "Python requirements documented in {filename}"

### Level 3

#### _check_devcontainer_exists
- **Severity**: RECOMMENDED
- **Level**: 3
- **Logic**:
  - Check for .devcontainer/devcontainer.json
  - Validate it's valid JSON
  - Check for "image" or "build" key
- **Failure message**: "No .devcontainer/devcontainer.json found"
- **Pass message**: "Devcontainer configuration found"

#### _check_dockerfile_exists
- **Severity**: OPTIONAL
- **Level**: 3
- **Logic**:
  - Check for Dockerfile in root
  - Check for multi-stage build (FROM...AS pattern)
  - Look for development stage
- **Failure message**: "No Dockerfile found"
- **Pass message**: "Dockerfile configured"

#### _check_version_pinning
- **Severity**: RECOMMENDED
- **Level**: 3
- **Logic**:
  - For Python: Check if requirements.txt has pinned versions (==) or poetry.lock exists
  - For Node: Check if package-lock.json or yarn.lock exists
  - For Go: Check if go.sum exists
  - For Rust: Check if Cargo.lock exists
- **Failure message**: "No version lock file found"
- **Pass message**: "Version pinning detected via lock file"

#### _check_setup_script_available
- **Severity**: OPTIONAL
- **Level**: 3
- **Logic**:
  - Look for setup.sh, scripts/setup.sh, Makefile with dev target
  - Check if script has execute permissions
  - Script must be > 100 bytes
- **Failure message**: "No automated setup script found"
- **Pass message**: "Setup script available: {filename}"

### Level 4

#### _check_devcontainer_features
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Parse .devcontainer/devcontainer.json
  - Check for "customizations.vscode.extensions" with linting/formatting tools
  - Look for common extensions: ruff, prettier, python, eslint
  - Look for "features" with git, docker, common dev tools
- **Failure message**: "Devcontainer lacks common development extensions"
- **Pass message**: "Devcontainer configured with development extensions"

#### _check_environment_validation
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for verify.sh, validate.sh, or Makefile target like "check-env"
  - Script must check: Python version, Node version, tool availability
  - Script should validate environment by running sample commands
- **Failure message**: "No environment validation script found"
- **Pass message**: "Environment validation script available"

#### _check_quick_start_script
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for "quick start", "quickstart", or single documented command
  - In README or AGENTS.md, find a code block with:
    - git clone + cd + one more command that sets up everything
  - Or find a script like quick-start.sh
- **Failure message**: "No quick-start command documented"
- **Pass message**: "Quick-start setup documented"

#### _check_ide_extensions_documented
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for "VS Code" or "editor" or ".vscode" mention in README or AGENTS.md
  - Check for .vscode/extensions.json file
  - Should list recommended extensions
- **Failure message**: "No IDE extension recommendations found"
- **Pass message**: "IDE extension recommendations documented"

### Level 5

#### _check_precommit_hooks
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Check for .pre-commit-config.yaml
  - Validate it's valid YAML
  - Should have at least 2 hooks configured (linting, formatting)
- **Failure message**: "No pre-commit hooks configured"
- **Pass message**: "Pre-commit hooks configured with {count} hooks"

#### _check_environment_monitoring
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for script named "monitor.sh", "health-check.sh", or similar
  - Script should check for:
    - Outdated dependencies
    - Environment variable mismatches
    - Missing development tools
- **Failure message**: "No environment monitoring script found"
- **Pass message**: "Environment monitoring available"

#### _check_auto_setup_on_clone
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for .git/hooks/post-checkout or post-clone hook installation
  - Or look for script documented that auto-runs after clone
  - Check if setup script is in post-merge hooks
- **Failure message**: "No automatic setup on clone configured"
- **Pass message**: "Automatic setup on clone configured"

#### _check_containerized_ci
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Check CI config (.github/workflows/*.yml, .gitlab-ci.yml, etc.)
  - Look for "docker" or "container" directive
  - Ideally uses same container image as devcontainer
- **Failure message**: "CI does not use containerized environment"
- **Pass message**: "CI uses containerized environment for consistency"

## Test Fixtures

Create 5 fixture directories under `tests/fixtures/`:

### 1. `dev-env-complete/`
A project with excellent dev environment setup:
- .env.example with variables
- .devcontainer/devcontainer.json with extensions
- setup.sh script
- Makefile with dev target
- requirements.txt with pinned versions + requirements-dev.txt
- .pre-commit-config.yaml
- AGENTS.md with setup section
- README with quick start

### 2. `dev-env-minimal/`
Bare minimum working dev environment:
- README with setup instructions
- requirements.txt (unpinned)
- .env.example (basic)
- pyproject.toml for dependencies

### 3. `dev-env-none/`
No dev environment setup:
- Only source code, no setup files
- No dependency files besides what's needed for imports

### 4. `dev-env-docker/`
Docker-focused dev environment:
- Dockerfile with development stage
- docker-compose.yml for local dev
- .dockerignore
- No devcontainer, but docker setup available

### 5. `dev-env-node/`
Node.js project with full setup:
- package.json with dev dependencies
- package-lock.json
- .devcontainer/devcontainer.json for Node
- README with npm install instructions
- .vscode/extensions.json with recommended extensions

## Testing Strategy

### Unit Tests (30+ tests)
1. Discovery tests (2): All files found, none found
2. Level 1 tests (4): Setup instructions, dependency files
3. Level 2 tests (8): .env.example, setup steps, dependency groups, python requirements
4. Level 3 tests (8): Devcontainer, Dockerfile, version pinning, setup scripts
5. Level 4 tests (8): Devcontainer features, validation, quick start, IDE extensions
6. Level 5 tests (8): Pre-commit, monitoring, auto-setup, containerized CI
7. Integration test (1): Full evaluate() with realistic project
8. Import test (1): DevEnvironmentPillar importable from pillars package

### Fixture Usage
Each test uses appropriate fixture from the 5 fixture directories above.

## Implementation Checklist

- [ ] Create design document (this file)
- [ ] Create `src/agent_readiness/pillars/dev_environment.py` (350+ lines)
- [ ] Update `src/agent_readiness/pillars/__init__.py` to import and export DevEnvironmentPillar
- [ ] Create 5 test fixture directories with realistic projects
- [ ] Create `tests/pillars/test_dev_environment.py` (450+ lines, 30+ tests)
- [ ] Run tests and ensure 85%+ coverage
- [ ] Verify all tests pass (should add ~30 tests to suite)
- [ ] Commit with message: "feat(dev-environment): implement Pillar 5"

## Success Criteria

- ✅ All 30+ new tests pass
- ✅ 85%+ code coverage for DevEnvironmentPillar
- ✅ All 120+ existing tests still pass
- ✅ Each check returns clear pass/fail with actionable guidance
- ✅ Supports Python, Node, Go, Rust projects
- ✅ Fixture tests reflect realistic development scenarios
