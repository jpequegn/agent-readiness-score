# Pillar 2: Build System - Design Document

**Date:** 2026-01-24
**Issue:** #3
**Pillar:** Build System

## Overview

Implementation of the second pillar for the agent readiness scoring system. This pillar evaluates build reproducibility and dependency management across multiple languages.

## Architecture

### Pillar Structure

The `BuildPillar` class inherits from `Pillar` and implements language-aware build checking:

1. **Language Detection**: Detect languages by package manager files (not just source files)
2. **Multi-language Support**: Check for appropriate build tooling for ALL detected languages
3. **Mixed Check Granularity**: Per-language checks (Levels 1-3) + Repository-wide checks (Levels 4-5)
4. **Semi-cumulative Scoring**: Higher levels require passing lower level checks with thresholds

### Scoring Model

Semi-cumulative scoring logic:
- **Level 1**: Any passing checks indicate basic functionality
- **Level 2**: 50% of (Level 1 + Level 2) checks passing
- **Level 3**: 80% of (Level 1 + Level 2) checks passing + Level 3 checks
- **Level 4**: 80% of (Level 1 + Level 2 + Level 3) checks passing + Level 4 checks
- **Level 5**: 90% of (Level 1 + Level 2 + Level 3 + Level 4) checks passing + Level 5 checks

### Language Detection

Detect languages by looking for package manager files:
- Python: `pyproject.toml`, `setup.py`, `requirements.txt`
- JavaScript/TypeScript: `package.json`
- Rust: `Cargo.toml`
- Go: `go.mod`

If multiple languages are present, check for appropriate build tooling for each language.

## Check Implementation

### Level 1 - Functional (Per-Language)

**Check: `check_package_manager_exists()`**
- **Purpose**: Verify each language has a package/dependency manager file
- **Detection**:
  - Python: `pyproject.toml`, `setup.py`, `requirements.txt`
  - JavaScript/TypeScript: `package.json`
  - Rust: `Cargo.toml`
  - Go: `go.mod`
- **Returns**: One CheckResult per detected language
- **Example**: "Python package manager" (passed), "JavaScript package manager" (passed)

### Level 2 - Documented (Per-Language)

**Check: `check_lock_file_exists()`**
- **Purpose**: Verify each language has dependency lock file for reproducibility
- **Detection**:
  - Python: `poetry.lock`, `Pipfile.lock`, `requirements.lock`
  - JavaScript: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
  - Rust: `Cargo.lock`
  - Go: `go.sum`
- **Returns**: One CheckResult per detected language
- **Example**: "Python lock file" (passed), "JavaScript lock file" (failed)

### Level 3 - Standardized (Per-Language)

**Check: `check_build_script_exists()`**
- **Purpose**: Verify single-command build is documented
- **Detection**:
  - Python: `[tool.poetry.scripts]` in pyproject.toml, or `Makefile` with build target
  - JavaScript: `"scripts": {"build": ...}` in package.json
  - Rust: Default `cargo build` (always passes if Cargo.toml exists)
  - Go: Default `go build` (always passes if go.mod exists), or `Makefile`
- **Returns**: One CheckResult per detected language
- **Example**: "Python build script" (passed), "JavaScript build script" (passed)

### Level 4 - Optimized (Repository-wide)

**Check: `check_build_caching()`**
- **Purpose**: Verify build caching is configured
- **Detection**:
  - CI config files with cache configurations
    - GitHub Actions: `- uses: actions/cache@v3` or similar
    - GitLab CI: `cache:` key in `.gitlab-ci.yml`
    - CircleCI: `save_cache` / `restore_cache` in config
  - Docker multi-stage builds with layer caching
  - Language-specific cache configuration mentioned in docs
- **Returns**: Single CheckResult for the repository
- **Example**: "Build caching configured" (passed)

**Check: `check_containerization()`**
- **Purpose**: Verify containerized build environment exists
- **Detection**:
  - `Dockerfile` or `Containerfile` exists
  - `.devcontainer/devcontainer.json` exists
  - `docker-compose.yml` with build services
- **Returns**: Single CheckResult for the repository
- **Example**: "Containerization configured" (passed)

### Level 5 - Autonomous (Repository-wide)

**Check: `check_dependency_automation()`**
- **Purpose**: Verify automatic dependency updates configured
- **Detection**:
  - `.github/dependabot.yml` exists
  - `renovate.json` or `.renovaterc` or `.github/renovate.json` exists
  - `.github/workflows/` contains dependency update automation
- **Returns**: Single CheckResult for the repository
- **Example**: "Dependency automation configured" (passed)

**Check: `check_reproducible_builds()`**
- **Purpose**: Verify hermetic/reproducible build configuration
- **Detection**:
  - All detected languages have lock files (cross-check with Level 2)
  - CI configuration uses pinned versions (not "latest" or floating tags)
  - Documentation mentions reproducible builds, build hash verification, or hermetic builds
  - Look for: `CONTRIBUTING.md`, `README.md`, `BUILD.md` with reproducibility mentions
- **Returns**: Single CheckResult for the repository
- **Example**: "Reproducible builds configured" (passed)

## File Organization

```
src/agent_readiness/
├── pillars/
│   ├── __init__.py
│   ├── style.py
│   └── build.py          # BuildPillar implementation
├── models.py
├── pillar.py
├── scanner.py
└── cli.py

tests/
└── pillars/
    ├── test_style.py
    └── test_build.py     # BuildPillar tests
```

## Testing Strategy

1. **Unit tests**: Test each check function individually with fixture directories
2. **Integration tests**: Test full pillar evaluation with sample repos
3. **Fixture repos**: Create test directories with various configurations:
   - `fixtures/python-minimal/` - Basic Python with pyproject.toml
   - `fixtures/python-full/` - Python with lock file, build scripts, caching
   - `fixtures/javascript-full/` - JavaScript with all Level 5 features
   - `fixtures/polyglot/` - Multi-language repo (Python + JavaScript)
   - `fixtures/rust-minimal/` - Rust with Cargo.toml
   - `fixtures/go-minimal/` - Go with go.mod

## Implementation Plan

1. Create `build.py` in pillars directory
2. Implement `BuildPillar` class skeleton
3. Implement language detection helper (by package manager files)
4. Implement Level 1 check (package manager exists)
5. Implement Level 2 check (lock file exists)
6. Implement Level 3 check (build script exists)
7. Implement Level 4 checks (caching + containerization)
8. Implement Level 5 checks (dependency automation + reproducible builds)
9. Write comprehensive tests
10. Update scanner to register BuildPillar (already supports multiple pillars)
11. Manual testing with real repositories

## Success Criteria

- [ ] All checks implemented and tested
- [ ] Supports Python, JavaScript/TypeScript, Go, Rust
- [ ] Correctly detects package managers and lock files
- [ ] Semi-cumulative scoring works as designed
- [ ] Tests achieve >90% coverage
- [ ] BuildPillar can be registered with Scanner
- [ ] Works on real-world repositories

## Future Enhancements

- Support for more languages (Java/Maven/Gradle, C++/CMake, Ruby/Bundler)
- Performance optimization for large repositories
- Caching of language detection results
- Build time estimation/measurement
- Integration with actual build execution to verify configuration validity
- Build matrix detection (checking for multi-platform builds in CI)
