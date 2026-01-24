# Pillar 1: Style & Validation - Design Document

**Date:** 2026-01-24
**Issue:** #2
**Pillar:** Style & Validation

## Overview

Implementation of the first pillar for the agent readiness scoring system. This pillar evaluates code style enforcement and validation tooling across multiple languages.

## Architecture

### Pillar Structure

The `StylePillar` class inherits from `Pillar` and implements language-aware style checking:

1. **Language Detection**: Detect all languages in the repository (Python, JavaScript/TypeScript, Go, Rust, etc.)
2. **Multi-language Support**: Check for appropriate tooling for ALL detected languages
3. **Level-based Checks**: Organize checks by maturity level (1-5)
4. **Semi-cumulative Scoring**: Higher levels require passing lower level checks with thresholds

### Scoring Model

Semi-cumulative scoring logic:
- **Level 1**: Any passing checks indicate basic functionality
- **Level 2**: 50% of (Level 1 + Level 2) checks passing
- **Level 3**: 80% of (Level 1 + Level 2) checks passing + Level 3 checks
- **Level 4**: 80% of (Level 1 + Level 2 + Level 3) checks passing + Level 4 checks
- **Level 5**: 90% of (Level 1 + Level 2 + Level 3 + Level 4) checks passing + Level 5 checks

### Language Detection

Count file extensions and check for language-specific config files:
- Python: `.py` files
- JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx` files
- Go: `.go` files
- Rust: `.rs` files

If multiple languages are present, check for appropriate tooling for each language.

## Check Implementation

### Level 1 - Functional (Basic linting exists)

**Check: `check_any_linter_config()`**
- **Purpose**: Verify some form of linting is configured
- **Detection**:
  - Python: `.flake8`, `ruff.toml`, `pyproject.toml` with `[tool.ruff]`, `.pylintrc`
  - JavaScript/TypeScript: `.eslintrc*`, `eslint.config.js`, `package.json` with eslint
  - Go: `.golangci.yml`, `.golangci.yaml`
  - Rust: `rustfmt.toml`, `.rustfmt.toml`

### Level 2 - Documented (Explicit config files)

**Check: `check_linter_config_per_language()`**
- **Purpose**: Ensure each detected language has explicit linter configuration
- **Returns**: One CheckResult per detected language
- **Detection**: Language-specific linter config files (same as Level 1, but per-language)

**Check: `check_formatter_config_per_language()`**
- **Purpose**: Ensure each detected language has formatter configuration
- **Returns**: One CheckResult per detected language
- **Detection**:
  - Python: `pyproject.toml` with `[tool.black]`, `.black`, `ruff.toml` with format config
  - JavaScript/TypeScript: `.prettierrc*`, `prettier.config.js`
  - Go: Uses `gofmt` by default (always passes)
  - Rust: `rustfmt.toml`, `.rustfmt.toml`

### Level 3 - Standardized (Automation)

**Check: `check_precommit_hooks()`**
- **Purpose**: Verify pre-commit hooks are configured
- **Detection**: `.pre-commit-config.yaml` exists

**Check: `check_linting_in_ci()`**
- **Purpose**: Verify linting runs in CI pipeline
- **Detection**: Parse CI config files for lint commands

**Check: `check_formatting_in_ci()`**
- **Purpose**: Verify formatting runs in CI pipeline
- **Detection**: Parse CI config files for format/formatting commands

### Level 4 - Optimized (Performance & Integration)

**Check: `check_precommit_performance()`**
- **Purpose**: Ensure pre-commit hooks run fast (<30 seconds estimated)
- **Detection**: Parse `.pre-commit-config.yaml`, flag slow hooks like pylint without caching
- **Heuristic**: Check for known fast tools (ruff, eslint with cache), flag slow ones

**Check: `check_autofix_available()`**
- **Purpose**: Verify auto-fix is configured for common issues
- **Detection**: Check if linters support `--fix` flag in pre-commit config or package scripts
- **Look for**: `ruff --fix`, `eslint --fix`, prettier (auto-fixes by default)

**Check: `check_editor_integration_documented()`**
- **Purpose**: Verify editor integration is documented
- **Detection**:
  - `.vscode/settings.json` with linter/formatter settings
  - `.editorconfig` exists
  - `CONTRIBUTING.md` or `README.md` mentions editor setup

### Level 5 - Autonomous (Agent-optimized)

**Check: `check_style_guide_for_agents()`**
- **Purpose**: Verify style guidelines are documented for AI agents
- **Detection**:
  - `AGENTS.md` has style section
  - `STYLE.md` exists
  - `CONTRIBUTING.md` has detailed style guidelines

**Check: `check_custom_rules()`**
- **Purpose**: Verify custom rules for project-specific patterns
- **Detection**:
  - Custom ESLint plugins in config
  - Custom ruff rules in `pyproject.toml`
  - Project-specific linting rules defined

**Check: `check_automatic_pr_enforcement()`**
- **Purpose**: Verify automatic style enforcement on PRs
- **Detection**:
  - GitHub Actions that comment on PRs with style issues
  - Required status checks for linting in branch protection
  - Bot integration (renovate, dependabot with auto-fix)

## CI Detection

Support major CI platforms:

```python
CI_PATTERNS = {
    'github': '.github/workflows/*.yml',
    'gitlab': '.gitlab-ci.yml',
    'circleci': '.circleci/config.yml',
    'jenkins': 'Jenkinsfile',
    'travis': '.travis.yml'
}
```

**CI Parsing Strategy:**
- Read YAML/config files
- Search for keywords: `lint`, `format`, `ruff`, `eslint`, `prettier`, `black`, `flake8`
- Check job/step names and command strings
- Return True if any CI file contains linting/formatting steps

## File Organization

```
src/agent_readiness/
├── pillars/
│   ├── __init__.py
│   └── style.py          # StylePillar implementation
├── models.py
├── pillar.py
├── scanner.py
└── cli.py

tests/
└── pillars/
    └── test_style.py     # StylePillar tests
```

## Testing Strategy

1. **Unit tests**: Test each check function individually with fixture directories
2. **Integration tests**: Test full pillar evaluation with sample repos
3. **Fixture repos**: Create test directories with various configurations:
   - `fixtures/python-minimal/` - Basic Python with ruff
   - `fixtures/python-full/` - Python with all Level 5 features
   - `fixtures/javascript-full/` - JavaScript with ESLint + Prettier
   - `fixtures/polyglot/` - Multi-language repo

## Implementation Plan

1. Create `pillars/` directory and `__init__.py`
2. Implement `StylePillar` class skeleton
3. Implement language detection helper
4. Implement Level 1 checks
5. Implement Level 2 checks
6. Implement Level 3 checks with CI detection
7. Implement Level 4 checks
8. Implement Level 5 checks
9. Write comprehensive tests
10. Update scanner to register StylePillar
11. Manual testing with real repositories

## Success Criteria

- [ ] All checks implemented and tested
- [ ] Supports Python, JavaScript/TypeScript, Go, Rust
- [ ] Correctly detects GitHub Actions, GitLab CI, CircleCI, Jenkins, Travis CI
- [ ] Semi-cumulative scoring works as designed
- [ ] Tests achieve >90% coverage
- [ ] StylePillar can be registered with Scanner
- [ ] Works on real-world repositories

## Future Enhancements

- Support for more languages (Java, C++, Ruby, etc.)
- Performance optimization for large repositories
- Caching of language detection results
- More granular CI detection (which specific tools run)
- Integration with actual tool execution to verify configuration validity
