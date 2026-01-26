# Pillar 7: Security Design Document

**Date**: January 26, 2026
**Status**: In Progress
**Coverage Target**: 85%+
**Test Count Target**: 40+ tests

## Overview

The **Security Pillar** evaluates how well a codebase protects against vulnerabilities, manages secrets, and follows security best practices. Good security means:

- Dependencies are tracked and kept up-to-date
- Secrets and credentials are not exposed
- Code is scanned for vulnerabilities
- Access control and authentication are properly implemented
- Encryption is used for sensitive data
- Security testing is performed
- Compliance and audit requirements are met

## What We're Measuring

### Level 1: Functional (Basic Security)
**Goal**: Basic security practices and tools are in place

Checks:
- ✅ **Dependency file exists**: package.json, requirements.txt, Gemfile, Cargo.toml, go.mod, etc.
- ✅ **Secrets not in code**: No API keys or credentials visible in source files

### Level 2: Documented (Security Awareness)
**Goal**: Security practices are documented and team understands them

Checks:
- ✅ **Security documentation exists**: SECURITY.md or security section in README
- ✅ **Dependency management documented**: Instructions for updating dependencies
- ✅ **Secret management documented**: How to handle credentials/env vars
- ✅ **Access control documented**: Authentication/authorization approach documented

### Level 3: Standardized (Consistent Security)
**Goal**: Security practices are consistently applied across the codebase

Checks:
- ✅ **Dependency lock file present**: package-lock.json, requirements.lock, Cargo.lock, etc.
- ✅ **Vulnerability scanning configured**: npm audit, pip-audit, cargo audit, safety, etc.
- ✅ **Secrets management tool**: .env file structure, dotenv documented, vault hints
- ✅ **Input validation present**: Validation/sanitization in request handlers

### Level 4: Optimized (Advanced Security)
**Goal**: Production-ready security with automated checks and tools

Checks:
- ✅ **SAST configured**: SonarQube, Bandit, ESLint security rules, clippy, etc.
- ✅ **Dependency scanning in CI**: Dependabot, Snyk, or similar integrated
- ✅ **Encryption indicators**: TLS/SSL configuration, encrypted field handling
- ✅ **Security testing**: OWASP testing, integration tests for auth/access

### Level 5: Autonomous (Proactive Security)
**Goal**: Security is automated and continuously monitored

Checks:
- ✅ **Secrets scanning in CI**: git-secrets, TruffleHog, or similar in pipeline
- ✅ **Automated security updates**: Renovate, Dependabot auto-merge configured
- ✅ **Runtime security**: WAF, intrusion detection, runtime protection hints
- ✅ **Threat modeling**: Architecture diagram or threat model document present

## Architecture

### Class Structure

```python
class SecurityPillar(Pillar):
    name: str = "Security"
    weight: float = 1.0

    # Discovery
    def _discover_security_setup(target_dir: Path) -> dict

    # Level 1: Functional
    def _check_dependency_file_exists(target_dir: Path) -> CheckResult
    def _check_secrets_not_in_code(target_dir: Path) -> CheckResult

    # Level 2: Documented
    def _check_security_documentation(target_dir: Path) -> CheckResult
    def _check_dependency_management_documented(target_dir: Path) -> CheckResult
    def _check_secret_management_documented(target_dir: Path) -> CheckResult
    def _check_access_control_documented(target_dir: Path) -> CheckResult

    # Level 3: Standardized
    def _check_dependency_lock_file(target_dir: Path) -> CheckResult
    def _check_vulnerability_scanning_configured(target_dir: Path) -> CheckResult
    def _check_secrets_management_tool(target_dir: Path) -> CheckResult
    def _check_input_validation_present(target_dir: Path) -> CheckResult

    # Level 4: Optimized
    def _check_sast_configured(target_dir: Path) -> CheckResult
    def _check_dependency_scanning_in_ci(target_dir: Path) -> CheckResult
    def _check_encryption_indicators(target_dir: Path) -> CheckResult
    def _check_security_testing(target_dir: Path) -> CheckResult

    # Level 5: Autonomous
    def _check_secrets_scanning_in_ci(target_dir: Path) -> CheckResult
    def _check_automated_security_updates(target_dir: Path) -> CheckResult
    def _check_runtime_security(target_dir: Path) -> CheckResult
    def _check_threat_modeling(target_dir: Path) -> CheckResult
```

### Discovery Logic (`_discover_security_setup`)

Returns dict with keys:
- `dependency_files`: List of dependency files found (package.json, requirements.txt, etc.)
- `lock_files`: List of lock files found (package-lock.json, Cargo.lock, etc.)
- `secret_patterns_found`: Dict of potential secrets patterns detected in code
- `has_security_doc`: Whether SECURITY.md exists
- `sast_config`: SAST tools configured (SonarQube, Bandit, ESLint, clippy)
- `dependency_scanning_tools`: Security scanning tools in use (npm audit, pip-audit, etc.)
- `env_file_patterns`: .env files and dotenv patterns found
- `ci_config`: CI configuration files (.github/workflows, .gitlab-ci.yml, etc.)
- `encryption_indicators`: TLS/encryption setup found
- `test_files`: Security test files found
- `readme_content`: README.md content
- `agents_content`: AGENTS.md content
- `source_files`: Main source code files

## Detailed Check Implementations

### Level 1

#### _check_dependency_file_exists
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Look for dependency files by language:
    - Python: requirements.txt, setup.py, pyproject.toml, Pipfile
    - Node.js: package.json
    - Ruby: Gemfile
    - Rust: Cargo.toml
    - Go: go.mod
    - Java: pom.xml, build.gradle
  - At least one must exist
- **Failure message**: "No dependency management file found"
- **Pass message**: "Dependency file found (package.json, requirements.txt, etc.)"

#### _check_secrets_not_in_code
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Scan source files for common secret patterns:
    - AWS_SECRET_ACCESS_KEY, PRIVATE_KEY, API_KEY values
    - Private keys (-----BEGIN RSA PRIVATE KEY-----)
    - Database credentials in connection strings
    - Exclude test files and config examples
  - Look for actual values (not examples with fake data)
  - Sample ~100 source files
- **Failure message**: "Potential secrets detected in code"
- **Pass message**: "No obvious secrets detected in code"

### Level 2

#### _check_security_documentation
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Look for SECURITY.md file
  - Or check README.md for "security" section (case-insensitive)
  - Content should be > 200 characters
- **Failure message**: "No security documentation found"
- **Pass message**: "Security documentation found (SECURITY.md or README section)"

#### _check_dependency_management_documented
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Check README.md or AGENTS.md for documentation about:
    - How to add new dependencies
    - How to update dependencies
    - Dependency management workflow
  - Or check if dependency management is mentioned in SECURITY.md
- **Failure message**: "Dependency management process not documented"
- **Pass message**: "Dependency management documented in README or SECURITY.md"

#### _check_secret_management_documented
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Look for documentation about:
    - Environment variables (.env, .env.example)
    - Secret management approach
    - Vault/secrets manager setup
  - Check for .env.example file
  - Or check README/SECURITY.md for env var documentation
- **Failure message**: "Secret management approach not documented"
- **Pass message**: "Secret management documented (.env.example, README, etc.)"

#### _check_access_control_documented
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Check README, AGENTS.md, or SECURITY.md for:
    - Authentication mechanism (JWT, OAuth, API keys, etc.)
    - Authorization/permission model
    - User role documentation
  - Or look for auth-related comments in code
- **Failure message**: "Access control approach not documented"
- **Pass message**: "Access control/authentication approach documented"

### Level 3

#### _check_dependency_lock_file
- **Severity**: REQUIRED
- **Level**: 3
- **Logic**:
  - Look for lock files:
    - Python: requirements.lock, poetry.lock, Pipfile.lock
    - Node.js: package-lock.json, yarn.lock, pnpm-lock.yaml
    - Rust: Cargo.lock
    - Go: go.sum
    - Ruby: Gemfile.lock
    - Java: pom.lock, gradle.lock
  - At least one should exist when dependency file exists
- **Failure message**: "No dependency lock file found"
- **Pass message**: "Dependency lock file present"

#### _check_vulnerability_scanning_configured
- **Severity**: REQUIRED
- **Level**: 3
- **Logic**:
  - Look for vulnerability scanning tools:
    - Python: pip-audit, safety config, bandit
    - Node.js: npm audit, snyk config
    - Rust: cargo-audit
    - Go: nancy
    - Java: dependency-check config
  - Check package.json scripts, setup.cfg, pyproject.toml, etc.
- **Failure message**: "No vulnerability scanning tool configured"
- **Pass message**: "Vulnerability scanning tool found (npm audit, pip-audit, etc.)"

#### _check_secrets_management_tool
- **Severity**: REQUIRED
- **Level**: 3
- **Logic**:
  - Look for secrets management approach:
    - .env file (check pyproject.toml, .npmrc, or env config)
    - .env.example file showing expected variables
    - Vault/secrets manager hints in code
    - Environment variable loading (python-dotenv, dotenv, process.env patterns)
  - At least one pattern should exist
- **Failure message**: "No secrets management approach found"
- **Pass message**: "Secrets management configured (.env pattern, vault, etc.)"

#### _check_input_validation_present
- **Severity**: REQUIRED
- **Level**: 3
- **Logic**:
  - Scan source files for validation patterns:
    - Python: pydantic, marshmallow, django validators
    - Node.js: joi, yup, zod, express-validator
    - Go: govalidator, ozzo/validation
    - Rust: serde validation
  - Or check for manual validation (len checks, type checks)
  - Look in ~50 source files for at least one validation pattern
- **Failure message**: "No input validation detected"
- **Pass message**: "Input validation/sanitization found in code"

### Level 4

#### _check_sast_configured
- **Severity**: RECOMMENDED
- **Level**: 4
- **Logic**:
  - Look for SAST tool configurations:
    - Python: .bandit, sonarqube config, pylint config
    - Node.js: .eslintrc with security rules, sonarqube config
    - Go: golangci-lint config with security linters
    - Rust: clippy configuration
    - Any: sonarqube-project.properties, .codeclimate.yml
  - Check for code quality tool configs
- **Failure message**: "No SAST tool configured"
- **Pass message**: "SAST tool configured (Bandit, ESLint, Clippy, etc.)"

#### _check_dependency_scanning_in_ci
- **Severity**: RECOMMENDED
- **Level**: 4
- **Logic**:
  - Check CI configuration files:
    - .github/workflows/*.yml
    - .gitlab-ci.yml
    - .circleci/config.yml
    - .travis.yml
    - Jenkinsfile
  - Look for:
    - "npm audit", "pip-audit", "cargo audit", "safety"
    - Snyk, Dependabot, BlackDuck
    - Renovate config
  - At least one should be configured
- **Failure message**: "Dependency scanning not configured in CI"
- **Pass message**: "Dependency scanning in CI (npm audit, pip-audit, Snyk, etc.)"

#### _check_encryption_indicators
- **Severity**: RECOMMENDED
- **Level**: 4
- **Logic**:
  - Look for encryption patterns:
    - TLS/SSL: tls config, https, cert files
    - Encryption libraries: cryptography, bcrypt, argon2, sodium
    - Encrypted fields: AES, RSA patterns in code
    - Database encryption: encryption at rest hints
  - Check requirements/package files and source code
- **Failure message**: "No encryption indicators found"
- **Pass message**: "Encryption indicators found (TLS, bcrypt, cryptography, etc.)"

#### _check_security_testing
- **Severity**: RECOMMENDED
- **Level**: 4
- **Logic**:
  - Look for security test patterns:
    - Auth tests: test_*.py or *.test.js with auth/access patterns
    - OWASP testing indicators
    - Integration tests checking access control
    - Security-focused test directories
  - Sample test files for security-related content
- **Failure message**: "No security testing found"
- **Pass message**: "Security tests found (auth, access control, etc.)"

### Level 5

#### _check_secrets_scanning_in_ci
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Check CI configuration for:
    - git-secrets, TruffleHog, detect-secrets
    - Secrets scanning step in pipeline
    - Pre-commit hooks for secrets detection
  - Look in CI files and .pre-commit-config.yaml
- **Failure message**: "No secrets scanning in CI"
- **Pass message**: "Secrets scanning in CI (git-secrets, TruffleHog, etc.)"

#### _check_automated_security_updates
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for automated update configuration:
    - Dependabot config (.github/dependabot.yml)
    - Renovate config (.renovaterc or renovate.json)
    - Auto-merge configuration
  - Check package.json for automatic update hints
- **Failure message**: "No automated dependency update configuration"
- **Pass message**: "Automated security updates configured (Dependabot, Renovate)"

#### _check_runtime_security
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for runtime security indicators:
    - WAF configuration hints
    - Rate limiting patterns
    - Intrusion detection setup
    - Security headers configuration
    - DDoS protection hints
  - Check source code and config files
- **Failure message**: "No runtime security measures indicated"
- **Pass message**: "Runtime security measures found (WAF, rate limiting, etc.)"

#### _check_threat_modeling
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for threat modeling artifacts:
    - THREAT_MODEL.md file
    - Architecture diagram with security notes
    - Security architecture documentation
    - OWASP threat model documentation
  - Check docs/ directory for architecture/threat docs
- **Failure message**: "No threat model or security architecture documented"
- **Pass message**: "Threat model or security architecture documented"

## Test Fixture Strategy

Create 5 fixture directories with increasing security maturity:

### `tests/fixtures/security-none/`
Empty project - no security setup

### `tests/fixtures/security-minimal/`
- `requirements.txt` or `package.json` (minimal)
- No lock file
- No secrets management
- No SAST

### `tests/fixtures/security-basic/`
- `requirements.txt` or `package.json`
- `requirements.lock` or `package-lock.json`
- `.env.example` file
- `README.md` with security section
- `setup.py` or `package.json` with pip-audit or npm audit script

### `tests/fixtures/security-complete/`
- Complete dependency management
- Lock files
- `.env.example` with documented variables
- `SECURITY.md` documentation
- `.bandit` or `.eslintrc` with security rules
- `.github/workflows/security.yml` with vulnerability scanning
- Input validation in code
- Encryption library imports

### `tests/fixtures/security-advanced/`
- All from `security-complete` plus:
- `.renovaterc` or `.github/dependabot.yml` for automated updates
- `.pre-commit-config.yaml` with secrets scanning
- Threat model documentation
- WAF/rate limiting configuration hints
- OWASP testing indicators

## Implementation Notes

1. **Secret Detection**: Use conservative patterns that minimize false positives
2. **Language Support**: Python, JavaScript/TypeScript, Go, Rust (with fallbacks for others)
3. **CI Detection**: Support GitHub Actions, GitLab CI, CircleCI, Travis CI, Jenkins
4. **Tool Discovery**: Detect both presence and configuration of security tools
5. **Content Scanning**: Sample files efficiently to avoid performance issues
6. **Metadata Tracking**: Include which tools/patterns were detected for transparency

## Success Criteria

- All 18 checks implemented and working correctly
- 40+ unit tests with 85%+ coverage
- Test fixtures demonstrate progression through maturity levels
- Clear failure messages guide improvement
- No false positives in secret detection
- Efficient file scanning (< 1s for large projects)
