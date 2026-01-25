# Pillar 3: Testing - Design Document

**Date:** 2026-01-25
**Issue:** #4
**Pillar:** Testing

## Overview

Implementation of the third pillar for the agent readiness scoring system. This pillar evaluates test infrastructure, coverage, and automation across multiple languages.

## Architecture

### Pillar Structure

The `TestingPillar` class inherits from `Pillar` and implements test-aware checking:

1. **Test Directory Detection**: Find test directories and files to detect test infrastructure
2. **Language Detection**: Infer languages from test file extensions in test directories
3. **Hybrid Verification**: Check configs for capabilities, parse reports when available
4. **Mixed Check Granularity**: Repository-wide checks (Levels 1-2) + Per-language checks (Levels 3-5)

### Language Detection Strategy

**Test Directory Approach** (TestingPillar-specific):
- Look for test directories first: `tests/`, `test/`, `__tests__/`, `spec/`, `*_test/`, `*Test/`
- Also check non-standard locations: `src/**/test/`, `lib/**/test/`
- Infer language from test file extensions in those directories
- Pro: Directly finds tests, works even without package managers
- Works for projects with tests but no package manager files

### Data Structure

```python
@dataclass
class TestInfrastructure:
    languages: set[str]  # Detected test languages
    test_dirs: list[Path]  # Found test directories
    test_files: dict[str, list[Path]]  # Test files per language
```

### Test File Patterns

- **Python**: `test_*.py`, `*_test.py`
- **JavaScript/TypeScript**: `*.test.js`, `*.spec.js`, `*.test.ts`, `*.spec.ts`
- **Go**: `*_test.go`
- **Rust**: `*_test.rs`, files in `tests/` directory

## Check Implementation

### Level 1 - Functional (Repository-wide)

**Check: `check_tests_exist()`**
- **Purpose**: Verify that some tests exist in the repository
- **Detection**:
  - Look for test directories (tests/, test/, __tests__/, spec/)
  - Look for test files matching patterns
  - Count total test files found
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: At least 1 test file found
- **Example**: "Found 45 test files in 3 directories"

### Level 2 - Documented (Repository-wide)

**Check: `check_test_directory_structure()`**
- **Purpose**: Verify tests are organized in standard directory structure
- **Detection**:
  - Check if standard test directory exists (tests/, test/, __tests__/)
  - Verify >50% of test files are in standard directories (not scattered)
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Standard directory exists with majority of tests
- **Example**: "Tests organized in tests/ directory (42/45 files)"

**Check: `check_test_command_documented()`**
- **Purpose**: Verify test commands are documented in README
- **Detection**:
  - Search README.md for "Testing" or "Tests" section
  - Look for test commands in code blocks (pytest, npm test, go test, cargo test)
  - Check for explicit instructions
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Test command found and documented
- **Example**: "Test command documented in README.md: 'pytest'"

### Level 3 - Standardized (Repository-wide + Per-language)

**Check: `check_tests_in_ci()`**
- **Purpose**: Verify tests run in CI pipeline
- **Detection**:
  - Scan CI config files (.github/workflows/, .gitlab-ci.yml, .circleci/config.yml)
  - Look for test commands in workflow steps
  - Detect test framework commands (pytest, npm test, go test, cargo test)
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Test commands found in CI configuration
- **Example**: "Tests run in CI: GitHub Actions (ci.yml)"

**Check: `check_coverage_measured()`**
- **Purpose**: Verify test coverage is being measured
- **Detection**:
  - Python: pytest-cov in pyproject.toml, .coveragerc exists, coverage section in pytest.ini
  - JavaScript: coverage config in jest.config.js or package.json
  - Go: -cover flag in test commands or config
  - Rust: tarpaulin in dependencies or llvm-cov config
- **Returns**: One CheckResult per detected language
- **Pass Criteria**: Coverage tool configured for the language
- **Example**: "Python coverage measured (pytest-cov configured)"

**Check: `check_unit_tests_isolated()`**
- **Purpose**: Verify tests use isolation patterns (mocking, fixtures)
- **Detection**:
  - Python: Check test files for pytest fixtures, unittest.mock imports
  - JavaScript: Look for jest.mock, vi.mock in test files
  - Go: Check for testify/mock, gomock imports
  - Rust: Look for mockall in dependencies
- **Returns**: One CheckResult per detected language
- **Pass Criteria**: Isolation patterns found in test files
- **Example**: "Python tests use isolation (pytest fixtures found)"

### Level 4 - Optimized (Per-language + Repository-wide)

**Check: `check_parallel_test_config()`**
- **Purpose**: Verify tests can run in parallel
- **Detection**:
  - Python: pytest-xdist in dependencies, -n flag in config
  - JavaScript: maxWorkers in jest.config, parallel in package.json scripts
  - Go: Always passes (parallel by default)
  - Rust: --test-threads in config, or default parallel behavior
- **Returns**: One CheckResult per detected language
- **Pass Criteria**: Parallel test configuration detected
- **Example**: "Python tests configured for parallel execution (pytest-xdist)"

**Check: `check_test_speed()`**
- **Purpose**: Verify tests run fast or have speed optimization
- **Detection**:
  - **Config approach**: Look for fast test markers (pytest -m "not slow", jest --onlyChanged)
  - **Report approach**: Parse test timing from .pytest_cache, jest results if modified <7 days
  - Check for test categorization (unit vs integration)
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Speed optimization configured OR actual timing <5min (if report available)
- **Message Format**: Indicates if based on config vs actual timing
- **Example**: "Fast test configuration detected (pytest markers)" or "Tests run in 2.3 minutes (from last run)"

**Check: `check_coverage_threshold()`**
- **Purpose**: Verify coverage threshold >=70% is enforced
- **Detection**:
  - **Config approach**: Check for minimum coverage in pytest.ini, jest.config, go.mod, Cargo.toml
  - **Report approach**: Parse coverage.xml, coverage.json, coverage.txt if modified <7 days
  - Validate report format before parsing
- **Returns**: One CheckResult per detected language
- **Pass Criteria**: Config sets >=70% OR actual coverage >=70%
- **Message Format**: Shows actual % if report found, otherwise config requirement
- **Example**: "Python coverage threshold: 85% (from coverage.xml)" or "JavaScript coverage threshold configured: 80%"

### Level 5 - Autonomous (Repository-wide + Per-language)

**Check: `check_tests_on_every_change()`**
- **Purpose**: Verify tests run automatically on every change
- **Detection**:
  - Look for pre-commit hooks with test commands (.pre-commit-config.yaml, .git/hooks/pre-commit)
  - Check CI for PR/push triggers with test steps
  - Check for git hooks that run tests
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Tests run on pre-commit OR on every PR/push
- **Example**: "Tests run on every change (pre-commit + CI on PR)"

**Check: `check_flaky_test_detection()`**
- **Purpose**: Verify flaky test detection/retry is configured
- **Detection**:
  - Python: pytest-flaky, pytest-rerunfailures in dependencies
  - JavaScript: jest-retry, @vitest/retry in package.json
  - Go: Check for retry logic in test helpers
  - Rust: Check for flaky crate or retry logic
- **Returns**: One CheckResult per detected language
- **Pass Criteria**: Flaky test tool/plugin configured
- **Example**: "Python flaky test detection enabled (pytest-rerunfailures)"

**Check: `check_property_based_testing()`**
- **Purpose**: Verify property-based testing support
- **Detection**:
  - Python: hypothesis in dependencies, @given decorators in test files
  - JavaScript: fast-check in package.json
  - Go: Check imports for gopter, rapid
  - Rust: proptest, quickcheck in dependencies
- **Returns**: One CheckResult per detected language
- **Pass Criteria**: Property-based testing library present
- **Example**: "Python property-based testing supported (hypothesis)"

## Error Handling & Edge Cases

### Graceful Degradation

- **Empty test directories**: Level 1 fails with clear message "Test directories found but empty"
- **Missing reports**: Pass based on config, message: "Coverage configured (threshold not verified)"
- **CI without tests**: Fail with suggestion "CI configuration found but no test commands detected"
- **Parse errors**: All file reads wrapped in try/except, continue scanning on parse errors

### Edge Cases

1. **Monorepo with multiple test dirs**: Count all as valid, aggregate file counts across all test directories
2. **Non-standard test locations**: Also check `src/**/test/`, `lib/**/test/` patterns
3. **Mixed language projects**: Run per-language checks for ALL detected languages
4. **Minimal projects**: Can pass Level 1-2 without CI, Level 3+ requires CI configuration

### Report Parsing Safety

- **Staleness check**: Only parse reports modified in last 7 days
- **Format validation**: Validate report structure before parsing
- **Error resilience**: Never fail check if report parsing fails, fall back to config-only detection
- **Clear messaging**: Always indicate whether check passed based on config or actual report

### Configuration Detection Priorities

1. **Language-specific configs**: pytest.ini, jest.config.js, go.mod test sections
2. **Tool sections in package files**: pyproject.toml [tool.pytest], package.json jest config
3. **Generic configs**: .coveragerc, coverage.json, .nycrc

## File Organization

```
src/agent_readiness/
├── pillars/
│   ├── __init__.py
│   ├── style.py
│   ├── build.py
│   └── testing.py         # TestingPillar implementation
├── models.py
├── pillar.py
├── scanner.py
└── cli.py

tests/
└── pillars/
    ├── test_style.py
    ├── test_build.py
    └── test_testing.py    # TestingPillar tests
```

## Testing Strategy

### Unit Tests

Test each check function individually with fixture directories:

```python
def test_check_tests_exist_pytest()
def test_check_tests_exist_jest()
def test_check_tests_exist_none_found()
def test_check_test_directory_structure_organized()
def test_check_test_directory_structure_scattered()
def test_check_coverage_threshold_from_config()
def test_check_coverage_threshold_from_report()
def test_check_coverage_threshold_both_sources()
def test_check_parallel_test_config_python()
def test_check_parallel_test_config_javascript()
```

### Integration Tests

Test full pillar evaluation with sample repos:

```python
def test_scanner_with_testing_pillar()
def test_scanner_with_all_three_pillars()
```

### Fixture Repos

Create test directories with various configurations:
- `fixtures/python-pytest-full/` - Python with full test setup (all levels)
- `fixtures/javascript-jest-minimal/` - JavaScript with basic tests
- `fixtures/go-testing-full/` - Go with complete test infrastructure
- `fixtures/rust-cargo-test/` - Rust with cargo test setup
- `fixtures/no-tests/` - Project with no test infrastructure
- `fixtures/scattered-tests/` - Tests not in standard directories

## Implementation Plan

1. Create `testing.py` in pillars directory
2. Implement `TestingPillar` class skeleton
3. Implement test directory detection and language inference
4. Implement Level 1 check (tests exist)
5. Implement Level 2 checks (directory structure, documentation)
6. Implement Level 3 checks (CI integration, coverage config, test isolation)
7. Implement Level 4 checks (parallel config, speed, coverage threshold)
8. Implement Level 5 checks (run on changes, flaky detection, property-based testing)
9. Write comprehensive tests
10. Update scanner to register TestingPillar
11. Manual testing with real repositories

## Success Criteria

- [ ] All checks implemented and tested
- [ ] Supports Python, JavaScript/TypeScript, Go, Rust
- [ ] Correctly detects test directories and infers languages
- [ ] Hybrid config + report parsing works as designed
- [ ] Tests achieve >90% coverage
- [ ] TestingPillar can be registered with Scanner
- [ ] Works on real-world repositories

## Future Enhancements

- Support for more languages (Java/JUnit, Ruby/RSpec, C++/GoogleTest)
- Mutation testing detection (mutmut, stryker)
- Visual regression testing detection
- Test quality metrics (assertion density, test complexity)
- Integration with actual test execution for verification
- Test categorization detection (unit, integration, e2e)
- Snapshot testing detection
