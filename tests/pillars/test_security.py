"""Tests for the Security pillar."""

import json
from pathlib import Path

import pytest

from agent_readiness.models import Severity
from agent_readiness.pillars.security import SecurityPillar


@pytest.fixture
def security_pillar():
    """Create a SecurityPillar instance."""
    return SecurityPillar()


def test_security_pillar_name(security_pillar):
    """Test that the pillar has the correct name."""
    assert security_pillar.name == "Security"


def test_security_pillar_weight(security_pillar):
    """Test that the pillar has the correct weight."""
    assert security_pillar.weight == 1.0


def test_discover_security_setup_none(tmp_path, security_pillar):
    """Test discovery with no security setup."""
    result = security_pillar._discover_security_setup(tmp_path)
    assert result["dependency_files"] == []
    assert result["lock_files"] == []
    assert result["has_security_doc"] is False


def test_discover_security_setup_with_package_json(tmp_path, security_pillar):
    """Test discovery finds package.json."""
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "test", "dependencies": {}})
    )
    result = security_pillar._discover_security_setup(tmp_path)
    assert "package.json" in result["dependency_files"]


def test_discover_security_setup_with_lock_file(tmp_path, security_pillar):
    """Test discovery finds lock files."""
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "test", "dependencies": {}})
    )
    (tmp_path / "package-lock.json").write_text("{}")
    result = security_pillar._discover_security_setup(tmp_path)
    assert "package-lock.json" in result["lock_files"]


def test_discover_security_setup_with_security_md(tmp_path, security_pillar):
    """Test discovery finds SECURITY.md."""
    (tmp_path / "SECURITY.md").write_text("# Security Policy")
    result = security_pillar._discover_security_setup(tmp_path)
    assert result["has_security_doc"] is True


def test_discover_security_setup_with_security_in_readme(tmp_path, security_pillar):
    """Test discovery finds security mention in README."""
    (tmp_path / "README.md").write_text("# Project\n\nSecurity is important.")
    result = security_pillar._discover_security_setup(tmp_path)
    assert result["has_security_doc"] is True


# Level 1 Tests

def test_check_dependency_file_exists_found(tmp_path, security_pillar):
    """Test dependency file detection when present."""
    (tmp_path / "package.json").write_text(json.dumps({"name": "test"}))
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_file_exists(tmp_path, sec)
    assert result.passed is True
    assert "found" in result.message.lower()


def test_check_dependency_file_exists_not_found(tmp_path, security_pillar):
    """Test dependency file detection when absent."""
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_file_exists(tmp_path, sec)
    assert result.passed is False
    assert "No dependency" in result.message


def test_check_secrets_not_in_code_clean(tmp_path, security_pillar):
    """Test secret detection in clean code."""
    (tmp_path / "app.py").write_text(
        """
import logging
def process_data(x):
    return x * 2
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_not_in_code(tmp_path, sec)
    assert result.passed is True


def test_check_secrets_not_in_code_with_secret(tmp_path, security_pillar):
    """Test secret detection when secrets present."""
    (tmp_path / "config.py").write_text(
        """
API_KEY = "sk-1234567890"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_not_in_code(tmp_path, sec)
    assert result.passed is False


# Level 2 Tests

def test_check_security_documentation_found(tmp_path, security_pillar):
    """Test security documentation detection when present."""
    (tmp_path / "SECURITY.md").write_text("# Security Policy")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_security_documentation(tmp_path, sec)
    assert result.passed is True


def test_check_security_documentation_not_found(tmp_path, security_pillar):
    """Test security documentation detection when absent."""
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_security_documentation(tmp_path, sec)
    assert result.passed is False


def test_check_dependency_management_documented_in_readme(tmp_path, security_pillar):
    """Test dependency management documentation in README."""
    (tmp_path / "README.md").write_text(
        "# Project\n\nTo update dependencies, run `npm update`."
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_management_documented(tmp_path, sec)
    assert result.passed is True


def test_check_dependency_management_documented_not_found(tmp_path, security_pillar):
    """Test dependency management documentation when absent."""
    (tmp_path / "README.md").write_text("# Project\n\nThis is a project.")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_management_documented(tmp_path, sec)
    assert result.passed is False


def test_check_secret_management_documented_with_env_example(
    tmp_path, security_pillar
):
    """Test secret management documentation with .env.example."""
    (tmp_path / ".env.example").write_text("API_KEY=\nDATABASE_URL=")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secret_management_documented(tmp_path, sec)
    assert result.passed is True


def test_check_secret_management_documented_in_readme(tmp_path, security_pillar):
    """Test secret management documentation in README."""
    (tmp_path / "README.md").write_text(
        "# Project\n\nSet environment variables in .env file."
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secret_management_documented(tmp_path, sec)
    assert result.passed is True


def test_check_secret_management_documented_not_found(tmp_path, security_pillar):
    """Test secret management documentation when absent."""
    (tmp_path / "README.md").write_text("# Project\n\nThis is a project.")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secret_management_documented(tmp_path, sec)
    assert result.passed is False


def test_check_access_control_documented_in_readme(tmp_path, security_pillar):
    """Test access control documentation in README."""
    (tmp_path / "README.md").write_text(
        "# Project\n\nAuthentication uses JWT tokens."
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_access_control_documented(tmp_path, sec)
    assert result.passed is True


def test_check_access_control_documented_not_found(tmp_path, security_pillar):
    """Test access control documentation when absent."""
    (tmp_path / "README.md").write_text("# Project")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_access_control_documented(tmp_path, sec)
    assert result.passed is False


# Level 3 Tests

def test_check_dependency_lock_file_found(tmp_path, security_pillar):
    """Test dependency lock file detection when present."""
    (tmp_path / "package.json").write_text(json.dumps({"name": "test"}))
    (tmp_path / "package-lock.json").write_text("{}")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_lock_file(tmp_path, sec)
    assert result.passed is True


def test_check_dependency_lock_file_not_found(tmp_path, security_pillar):
    """Test dependency lock file detection when absent."""
    (tmp_path / "package.json").write_text(json.dumps({"name": "test"}))
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_lock_file(tmp_path, sec)
    assert result.passed is False


def test_check_vulnerability_scanning_configured_npm_audit(
    tmp_path, security_pillar
):
    """Test vulnerability scanning detection with npm audit."""
    pkg = {
        "name": "test",
        "scripts": {"audit": "npm audit"},
        "dependencies": {"express": "^4.0.0"},
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_vulnerability_scanning_configured(tmp_path, sec)
    assert result.passed is True


def test_check_vulnerability_scanning_configured_not_found(tmp_path, security_pillar):
    """Test vulnerability scanning detection when absent."""
    pkg = {"name": "test", "dependencies": {"express": "^4.0.0"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_vulnerability_scanning_configured(tmp_path, sec)
    assert result.passed is False


def test_check_secrets_management_tool_with_env_file(tmp_path, security_pillar):
    """Test secrets management detection with .env file."""
    (tmp_path / ".env").write_text("API_KEY=test")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_management_tool(tmp_path, sec)
    assert result.passed is True


def test_check_secrets_management_tool_with_dotenv_pattern(tmp_path, security_pillar):
    """Test secrets management detection with dotenv pattern."""
    (tmp_path / "app.py").write_text(
        """
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ.get('API_KEY')
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_management_tool(tmp_path, sec)
    assert result.passed is True


def test_check_secrets_management_tool_not_found(tmp_path, security_pillar):
    """Test secrets management detection when absent."""
    (tmp_path / "app.py").write_text("print('hello')")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_management_tool(tmp_path, sec)
    assert result.passed is False


def test_check_input_validation_present_pydantic(tmp_path, security_pillar):
    """Test input validation detection with pydantic."""
    (tmp_path / "models.py").write_text(
        """
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_input_validation_present(tmp_path, sec)
    assert result.passed is True


def test_check_input_validation_present_joi(tmp_path, security_pillar):
    """Test input validation detection with joi."""
    (tmp_path / "schema.js").write_text(
        """
const schema = joi.object({
  email: joi.string().email(),
  password: joi.string().min(8)
});
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_input_validation_present(tmp_path, sec)
    assert result.passed is True


def test_check_input_validation_present_not_found(tmp_path, security_pillar):
    """Test input validation detection when absent."""
    (tmp_path / "app.py").write_text("def process(data): return data")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_input_validation_present(tmp_path, sec)
    assert result.passed is False


# Level 4 Tests

def test_check_sast_configured_eslint(tmp_path, security_pillar):
    """Test SAST detection with eslint."""
    (tmp_path / ".eslintrc.json").write_text(json.dumps({"extends": "eslint:recommended"}))
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_sast_configured(tmp_path, sec)
    assert result.passed is True


def test_check_sast_configured_bandit(tmp_path, security_pillar):
    """Test SAST detection with bandit."""
    (tmp_path / ".bandit").write_text("[bandit]\nskips = B101")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_sast_configured(tmp_path, sec)
    assert result.passed is True


def test_check_sast_configured_not_found(tmp_path, security_pillar):
    """Test SAST detection when absent."""
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_sast_configured(tmp_path, sec)
    assert result.passed is False


def test_check_dependency_scanning_in_ci_workflow(tmp_path, security_pillar):
    """Test dependency scanning in CI detection with GitHub workflow."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "security.yml").write_text(
        """
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - run: npm audit
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_scanning_in_ci(tmp_path, sec)
    assert result.passed is True


def test_check_dependency_scanning_in_ci_not_found(tmp_path, security_pillar):
    """Test dependency scanning in CI detection when absent."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "test.yml").write_text("jobs:\n  test:\n    runs-on: ubuntu")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_dependency_scanning_in_ci(tmp_path, sec)
    assert result.passed is False


def test_check_encryption_indicators_bcrypt(tmp_path, security_pillar):
    """Test encryption detection with bcrypt."""
    pkg = {
        "name": "test",
        "dependencies": {"bcrypt": "^5.0.0"},
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_encryption_indicators(tmp_path, sec)
    assert result.passed is True


def test_check_encryption_indicators_cryptography_import(tmp_path, security_pillar):
    """Test encryption detection with cryptography import."""
    (tmp_path / "crypto.py").write_text(
        """
from cryptography.fernet import Fernet

def encrypt(data):
    return Fernet(key).encrypt(data)
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_encryption_indicators(tmp_path, sec)
    assert result.passed is True


def test_check_encryption_indicators_not_found(tmp_path, security_pillar):
    """Test encryption detection when absent."""
    (tmp_path / "app.py").write_text("print('hello')")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_encryption_indicators(tmp_path, sec)
    assert result.passed is False


def test_check_security_testing_found(tmp_path, security_pillar):
    """Test security testing detection when present."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_auth.py").write_text(
        """
def test_authentication():
    assert True
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_security_testing(tmp_path, sec)
    assert result.passed is True


def test_check_security_testing_not_found(tmp_path, security_pillar):
    """Test security testing detection when absent."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_basic.py").write_text(
        """
def test_addition():
    assert 1 + 1 == 2
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_security_testing(tmp_path, sec)
    assert result.passed is False


# Level 5 Tests

def test_check_secrets_scanning_in_ci_trufflehog(tmp_path, security_pillar):
    """Test secrets scanning in CI with TruffleHog."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "security.yml").write_text(
        """
jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: trufflesecurity/trufflehog@main
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_scanning_in_ci(tmp_path, sec)
    assert result.passed is True


def test_check_secrets_scanning_in_ci_precommit(tmp_path, security_pillar):
    """Test secrets scanning with pre-commit hooks."""
    (tmp_path / ".pre-commit-config.yaml").write_text(
        """
repos:
  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_scanning_in_ci(tmp_path, sec)
    assert result.passed is True


def test_check_secrets_scanning_in_ci_not_found(tmp_path, security_pillar):
    """Test secrets scanning detection when absent."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "test.yml").write_text("jobs:\n  test:\n    runs-on: ubuntu")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_secrets_scanning_in_ci(tmp_path, sec)
    assert result.passed is False


def test_check_automated_security_updates_dependabot(tmp_path, security_pillar):
    """Test automated updates detection with Dependabot."""
    (tmp_path / ".github").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".github" / "dependabot.yml").write_text(
        """version: 2
updates:
  - package-ecosystem: npm
    directory: /
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_automated_security_updates(tmp_path, sec)
    assert result.passed is True


def test_check_automated_security_updates_renovate(tmp_path, security_pillar):
    """Test automated updates detection with Renovate."""
    (tmp_path / ".renovaterc").write_text('{"extends": ["config:base"]}')
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_automated_security_updates(tmp_path, sec)
    assert result.passed is True


def test_check_automated_security_updates_not_found(tmp_path, security_pillar):
    """Test automated updates detection when absent."""
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_automated_security_updates(tmp_path, sec)
    assert result.passed is False


def test_check_runtime_security_found(tmp_path, security_pillar):
    """Test runtime security detection when present."""
    (tmp_path / "app.py").write_text(
        """
from flask_limiter import Limiter

def apply_rate_limit():
    limiter = Limiter()
    return limiter
    """
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_runtime_security(tmp_path, sec)
    assert result.passed is True


def test_check_runtime_security_not_found(tmp_path, security_pillar):
    """Test runtime security detection when absent."""
    (tmp_path / "app.py").write_text("print('hello')")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_runtime_security(tmp_path, sec)
    assert result.passed is False


def test_check_threat_modeling_found(tmp_path, security_pillar):
    """Test threat model detection when present."""
    (tmp_path / "THREAT_MODEL.md").write_text("# Threat Model\n\nOWASP Top 10 analysis")
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_threat_modeling(tmp_path, sec)
    assert result.passed is True


def test_check_threat_modeling_architecture_doc(tmp_path, security_pillar):
    """Test threat model detection in architecture docs."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "architecture.md").write_text(
        "# Architecture\n\nThreat mitigation strategies discussed here."
    )
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_threat_modeling(tmp_path, sec)
    assert result.passed is True


def test_check_threat_modeling_not_found(tmp_path, security_pillar):
    """Test threat model detection when absent."""
    sec = security_pillar._discover_security_setup(tmp_path)
    result = security_pillar._check_threat_modeling(tmp_path, sec)
    assert result.passed is False


# Fixture-based integration tests

def test_security_pillar_with_minimal_fixture(
    security_pillar,
):
    """Test security pillar against minimal fixture."""
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "security-minimal"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")

    results = security_pillar.evaluate(fixture_dir)
    assert len(results) == 18
    assert all(hasattr(r, "passed") for r in results)


def test_security_pillar_with_complete_fixture(
    security_pillar,
):
    """Test security pillar against complete fixture."""
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "security-complete"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")

    results = security_pillar.evaluate(fixture_dir)
    assert len(results) == 18
    passed_count = sum(1 for r in results if r.passed)
    # Complete fixture should pass more checks
    assert passed_count >= 8


def test_security_pillar_with_advanced_fixture(
    security_pillar,
):
    """Test security pillar against advanced fixture."""
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "security-advanced"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")

    results = security_pillar.evaluate(fixture_dir)
    assert len(results) == 18
    passed_count = sum(1 for r in results if r.passed)
    # Advanced fixture should pass most checks
    assert passed_count >= 14


def test_security_pillar_importable():
    """Test that SecurityPillar is importable from pillars module."""
    from agent_readiness.pillars import SecurityPillar as ImportedPillar

    assert ImportedPillar is not None
    assert ImportedPillar().name == "Security"


def test_evaluate_returns_correct_structure(security_pillar, tmp_path):
    """Test that evaluate returns properly structured results."""
    (tmp_path / "package.json").write_text('{"name": "test"}')

    results = security_pillar.evaluate(tmp_path)

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
