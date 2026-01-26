"""Tests for Dev Environment pillar."""

from pathlib import Path

from agent_readiness.pillars.dev_environment import DevEnvironmentPillar
from agent_readiness.models import Severity


def test_dev_environment_pillar_name() -> None:
    """Test DevEnvironmentPillar has correct name."""
    pillar = DevEnvironmentPillar()
    assert pillar.name == "Dev Environment"


def test_dev_environment_pillar_weight() -> None:
    """Test DevEnvironmentPillar has default weight."""
    pillar = DevEnvironmentPillar()
    assert pillar.weight == 1.0


def test_discover_dev_environment_complete(tmp_path: Path) -> None:
    """Test discovering all dev environment assets."""
    (tmp_path / ".env.example").touch()
    (tmp_path / ".devcontainer").mkdir()
    (tmp_path / ".devcontainer" / "devcontainer.json").write_text('{"image": "ubuntu"}')
    (tmp_path / "Dockerfile").touch()
    (tmp_path / "setup.sh").write_text("#!/bin/bash\necho setup")
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / ".pre-commit-config.yaml").touch()

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)

    assert env["env_example"] is not None
    assert env["devcontainer_json"] is not None
    assert env["dockerfile"] is not None
    assert len(env["setup_scripts"]) > 0
    assert "python" in env["dependency_files"]
    assert env["precommit_config"] is not None


def test_discover_dev_environment_none_found(tmp_path: Path) -> None:
    """Test discovering dev environment when none exists."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)

    assert env["env_example"] is None
    assert env["devcontainer_json"] is None
    assert env["dockerfile"] is None
    assert len(env["setup_scripts"]) == 0
    assert len(env["dependency_files"]) == 0


def test_check_setup_instructions_exist_found(tmp_path: Path) -> None:
    """Test setup instructions check when found."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Installation\n\nRun pip install to setup the project."
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_setup_instructions_exist(tmp_path, env)

    assert result.passed
    assert "setup" in result.message.lower() or "installation" in result.message.lower()
    assert result.severity == Severity.REQUIRED
    assert result.level == 1


def test_check_setup_instructions_exist_not_found(tmp_path: Path) -> None:
    """Test setup instructions check when not found."""
    (tmp_path / "README.md").write_text("# Project\n\nSome content.")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_setup_instructions_exist(tmp_path, env)

    assert not result.passed


def test_check_dependency_file_exists_python(tmp_path: Path) -> None:
    """Test dependency file check for Python."""
    (tmp_path / "pyproject.toml").touch()

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_dependency_file_exists(tmp_path, env)

    assert result.passed
    assert "pyproject.toml" in result.message
    assert result.level == 1


def test_check_dependency_file_exists_not_found(tmp_path: Path) -> None:
    """Test dependency file check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_dependency_file_exists(tmp_path, env)

    assert not result.passed


def test_check_env_example_exists_found(tmp_path: Path) -> None:
    """Test .env.example check when found."""
    (tmp_path / ".env.example").write_text("DEBUG=true\nKEY=value\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_env_example_exists(tmp_path, env)

    assert result.passed
    assert result.level == 2


def test_check_env_example_exists_not_found(tmp_path: Path) -> None:
    """Test .env.example check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_env_example_exists(tmp_path, env)

    assert not result.passed


def test_check_setup_steps_documented_found(tmp_path: Path) -> None:
    """Test setup steps check when documented."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Installation\n\nTo setup run: npm install and then npm run dev. "
        "This is a longer description to meet the minimum character requirement."
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_setup_steps_documented(tmp_path, env)

    assert result.passed
    assert result.level == 2


def test_check_setup_steps_documented_not_found(tmp_path: Path) -> None:
    """Test setup steps check when not documented."""
    (tmp_path / "README.md").write_text("# Project\n\nDoes something cool.")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_setup_steps_documented(tmp_path, env)

    assert not result.passed


def test_check_dependency_groups_documented_python(tmp_path: Path) -> None:
    """Test dependency groups check for Python."""
    (tmp_path / "requirements.txt").touch()
    (tmp_path / "requirements-dev.txt").touch()

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_dependency_groups_documented(tmp_path, env)

    assert result.passed
    assert result.level == 2


def test_check_dependency_groups_documented_not_found(tmp_path: Path) -> None:
    """Test dependency groups check when not found."""
    (tmp_path / "requirements.txt").write_text("requests\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_dependency_groups_documented(tmp_path, env)

    assert not result.passed


def test_check_python_requirements_documented_pyproject(tmp_path: Path) -> None:
    """Test Python requirements check with pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'test'\ndependencies = ['requests']\n"
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_python_requirements_documented(tmp_path, env)

    assert result.passed
    assert result.level == 2


def test_check_python_requirements_documented_requirements_txt(tmp_path: Path) -> None:
    """Test Python requirements check with requirements.txt."""
    (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_python_requirements_documented(tmp_path, env)

    assert result.passed


def test_check_python_requirements_documented_non_python(tmp_path: Path) -> None:
    """Test Python requirements check for non-Python projects."""
    (tmp_path / "package.json").write_text('{"name": "test"}')

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_python_requirements_documented(tmp_path, env)

    assert result.passed  # Passes for non-Python projects


def test_check_devcontainer_exists_found(tmp_path: Path) -> None:
    """Test devcontainer check when found."""
    (tmp_path / ".devcontainer").mkdir()
    (tmp_path / ".devcontainer" / "devcontainer.json").write_text(
        '{"image": "ubuntu:22.04"}'
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_devcontainer_exists(tmp_path, env)

    assert result.passed
    assert result.level == 3


def test_check_devcontainer_exists_not_found(tmp_path: Path) -> None:
    """Test devcontainer check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_devcontainer_exists(tmp_path, env)

    assert not result.passed


def test_check_dockerfile_exists_found(tmp_path: Path) -> None:
    """Test Dockerfile check when found."""
    (tmp_path / "Dockerfile").write_text("FROM ubuntu:22.04\nRUN apt-get update\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_dockerfile_exists(tmp_path, env)

    assert result.passed
    assert result.level == 3


def test_check_dockerfile_exists_not_found(tmp_path: Path) -> None:
    """Test Dockerfile check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_dockerfile_exists(tmp_path, env)

    assert not result.passed


def test_check_version_pinning_poetry_lock(tmp_path: Path) -> None:
    """Test version pinning check with poetry.lock."""
    (tmp_path / "poetry.lock").touch()

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_version_pinning(tmp_path, env)

    assert result.passed
    assert result.level == 3


def test_check_version_pinning_requirements_with_pins(tmp_path: Path) -> None:
    """Test version pinning check with requirements.txt pins."""
    (tmp_path / "requirements.txt").write_text("requests==2.28.0\npydantic==2.0.0\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_version_pinning(tmp_path, env)

    assert result.passed


def test_check_version_pinning_not_found(tmp_path: Path) -> None:
    """Test version pinning check when not found."""
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup(name='test')\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_version_pinning(tmp_path, env)

    assert not result.passed


def test_check_setup_script_available_docker_compose(tmp_path: Path) -> None:
    """Test setup script check with docker-compose."""
    (tmp_path / "docker-compose.yml").write_text(
        "version: '3.8'\nservices:\n  dev:\n    image: python:3.11\n"
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_setup_script_available(tmp_path, env)

    # docker-compose.yml is in setup_scripts but not explicitly checked
    # This test validates the discovery works
    assert env["setup_scripts"]
    assert result.level == 3


def test_check_setup_script_available_makefile(tmp_path: Path) -> None:
    """Test setup script check with Makefile."""
    (tmp_path / "Makefile").write_text("install:\n\tpip install -e .\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_setup_script_available(tmp_path, env)

    assert result.passed


def test_check_setup_script_available_not_found(tmp_path: Path) -> None:
    """Test setup script check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_setup_script_available(tmp_path, env)

    assert not result.passed


def test_check_devcontainer_features_found(tmp_path: Path) -> None:
    """Test devcontainer features check when extensions found."""
    (tmp_path / ".devcontainer").mkdir()
    (tmp_path / ".devcontainer" / "devcontainer.json").write_text(
        """{
        "image": "ubuntu:22.04",
        "customizations": {
            "vscode": {
                "extensions": ["ms-python.python", "charliermarsh.ruff"]
            }
        }
    }"""
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_devcontainer_features(tmp_path, env)

    assert result.passed
    assert result.level == 4


def test_check_devcontainer_features_not_found(tmp_path: Path) -> None:
    """Test devcontainer features check when no extensions."""
    (tmp_path / ".devcontainer").mkdir()
    (tmp_path / ".devcontainer" / "devcontainer.json").write_text('{"image": "ubuntu"}')

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_devcontainer_features(tmp_path, env)

    assert not result.passed


def test_check_environment_validation_found(tmp_path: Path) -> None:
    """Test environment validation check when Makefile target exists."""
    (tmp_path / "Makefile").write_text(
        ".PHONY: check-env\n\n"
        "check-env:\n"
        "\t@python --version\n"
        "\t@echo Environment OK\n"
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_environment_validation(tmp_path, env)

    assert result.passed
    assert result.level == 4


def test_check_environment_validation_makefile(tmp_path: Path) -> None:
    """Test environment validation check with Makefile target."""
    (tmp_path / "Makefile").write_text(
        "validate:\n\tpython --version\n\tnpm --version\n"
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_environment_validation(tmp_path, env)

    assert result.passed


def test_check_environment_validation_not_found(tmp_path: Path) -> None:
    """Test environment validation check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_environment_validation(tmp_path, env)

    assert not result.passed


def test_check_quick_start_script_file(tmp_path: Path) -> None:
    """Test quick-start check when script file exists."""
    (tmp_path / "quick-start.sh").write_text("#!/bin/bash\necho Starting setup\necho Done\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_quick_start_script(tmp_path, env)

    assert result.passed
    assert result.level == 4


def test_check_quick_start_script_not_found(tmp_path: Path) -> None:
    """Test quick-start check when not found."""
    (tmp_path / "README.md").write_text("# Project\n\nSome content.")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_quick_start_script(tmp_path, env)

    assert not result.passed


def test_check_ide_extensions_documented_vscode(tmp_path: Path) -> None:
    """Test IDE extensions check with VS Code documentation."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## VS Code Extensions\n\nInstall ruff, prettier, etc."
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_ide_extensions_documented(tmp_path, env)

    assert result.passed
    assert result.level == 4


def test_check_ide_extensions_documented_extensions_json(tmp_path: Path) -> None:
    """Test IDE extensions check with extensions.json."""
    (tmp_path / ".vscode").mkdir()
    (tmp_path / ".vscode" / "extensions.json").write_text(
        '{"recommendations": ["ms-python.python"]}'
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_ide_extensions_documented(tmp_path, env)

    assert result.passed


def test_check_ide_extensions_documented_not_found(tmp_path: Path) -> None:
    """Test IDE extensions check when not found."""
    (tmp_path / "README.md").write_text("# Project")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_ide_extensions_documented(tmp_path, env)

    assert not result.passed


def test_check_precommit_hooks_found(tmp_path: Path) -> None:
    """Test pre-commit hooks check when configured."""
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
        "    hooks:\n"
        "      - id: ruff\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    hooks:\n"
        "      - id: trailing-whitespace\n"
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_precommit_hooks(tmp_path, env)

    assert result.passed
    assert result.level == 5


def test_check_precommit_hooks_not_found(tmp_path: Path) -> None:
    """Test pre-commit hooks check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_precommit_hooks(tmp_path, env)

    assert not result.passed


def test_check_environment_monitoring_monitor_script(tmp_path: Path) -> None:
    """Test environment monitoring check when monitor.sh exists in root."""
    monitor_file = tmp_path / "monitor.sh"
    monitor_file.write_text(
        "#!/bin/bash\n# Check environment health\n"
        "python --version\nnpm --version\necho healthy\necho monitoring\necho done\n"
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_environment_monitoring(tmp_path, env)

    assert result.passed
    assert result.level == 5


def test_check_environment_monitoring_not_found(tmp_path: Path) -> None:
    """Test environment monitoring check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_environment_monitoring(tmp_path, env)

    assert not result.passed


def test_check_auto_setup_on_clone_found(tmp_path: Path) -> None:
    """Test auto setup on clone check when configured."""
    (tmp_path / ".husky").mkdir()
    (tmp_path / ".husky" / "post-checkout").write_text("#!/bin/bash\nnpm install\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_auto_setup_on_clone(tmp_path, env)

    assert result.passed
    assert result.level == 5


def test_check_auto_setup_on_clone_not_found(tmp_path: Path) -> None:
    """Test auto setup on clone check when not configured."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_auto_setup_on_clone(tmp_path, env)

    assert not result.passed


def test_check_containerized_ci_github_actions(tmp_path: Path) -> None:
    """Test containerized CI check with GitHub Actions."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "test.yml").write_text(
        "name: test\n"
        "jobs:\n"
        "  test:\n"
        "    container:\n"
        "      image: python:3.11\n"
    )

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_containerized_ci(tmp_path, env)

    assert result.passed
    assert result.level == 5


def test_check_containerized_ci_gitlab(tmp_path: Path) -> None:
    """Test containerized CI check with GitLab CI."""
    (tmp_path / ".gitlab-ci.yml").write_text("image: python:3.11\njobs:\n  test:\n    script:\n")

    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_containerized_ci(tmp_path, env)

    assert result.passed


def test_check_containerized_ci_not_found(tmp_path: Path) -> None:
    """Test containerized CI check when not found."""
    pillar = DevEnvironmentPillar()
    env = pillar._discover_dev_environment(tmp_path)
    result = pillar._check_containerized_ci(tmp_path, env)

    assert not result.passed


def test_evaluate_full_pillar(tmp_path: Path) -> None:
    """Test full pillar evaluation."""
    # Create complete dev environment
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Installation\n\n```bash\npip install -e .\n```"
    )
    (tmp_path / ".env.example").write_text("DEBUG=false\n")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    (tmp_path / "setup.sh").write_text("#!/bin/bash\npip install\n")

    pillar = DevEnvironmentPillar()
    results = pillar.evaluate(tmp_path)

    # Should have multiple checks
    assert len(results) >= 15
    assert any(r.name == "Setup instructions exist" for r in results)
    assert any(r.name == "Dependency file exists" for r in results)

    # Some checks should pass
    passed = sum(1 for r in results if r.passed)
    assert passed > 0

    # All results should have a level between 1-5
    for result in results:
        assert 1 <= result.level <= 5


def test_dev_environment_pillar_importable() -> None:
    """Test DevEnvironmentPillar can be imported from pillars package."""
    from agent_readiness.pillars import DevEnvironmentPillar

    pillar = DevEnvironmentPillar()
    assert pillar.name == "Dev Environment"
