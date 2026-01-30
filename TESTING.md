# Testing Guide

This document explains how to write, run, and maintain tests in the agent-readiness-score project.

## Quick Start

### Running Python Tests

```bash
# Run all Python tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=agent_readiness --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run tests matching a pattern
pytest tests/ -k "test_cli"

# Run with verbose output
pytest tests/ -v

# Run tests in parallel (faster)
pytest tests/ -n auto
```

### Running JavaScript Tests

```bash
# Run all Jest tests for the GitHub Action
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## Test Structure

### Python Tests

The project uses **pytest** for Python testing. Test files are organized by functionality:

```
tests/
├── test_cli.py                    # CLI functionality tests
├── test_clawdbot_skill.py         # Clawdbot skill tests
├── test_integration.py            # Integration tests
├── pillars/                       # Pillar-specific tests
│   ├── test_build.py             # Build System pillar
│   ├── test_debugging_observability.py
│   ├── test_dev_environment.py
│   ├── test_documentation.py
│   ├── test_security.py
│   ├── test_style.py
│   ├── test_task_discovery.py
│   └── test_testing.py
├── action/                        # GitHub Action tests
│   ├── index.test.js             # Jest tests
│   └── __mocks__/                # Test mocks
│       └── @actions/core.js
└── fixtures/                      # Test data and fixtures
    ├── dev-env-docker/
    ├── dev-env-complete/
    ├── docs-with-examples/
    └── ...
```

### JavaScript Tests

Jest tests for the GitHub Action are located in `tests/action/`:

```
tests/action/
├── index.test.js        # Action unit tests
├── __mocks__/           # Mock implementations
│   └── @actions/core.js
└── fixtures/            # Test data (if needed)
```

## Writing Tests

### Python Test Example

```python
import pytest
from agent_readiness.cli import main
from pathlib import Path

class TestCLIBasic:
    """Test basic CLI functionality."""

    def test_scan_current_directory(self):
        """Test scanning current directory."""
        result = main(['.'])
        assert result is not None

    def test_json_output_format(self, tmp_path):
        """Test JSON output format."""
        # Create a test directory
        test_dir = tmp_path / "test_repo"
        test_dir.mkdir()

        # Run CLI with JSON format
        result = main([str(test_dir), '--format', 'json'])

        # Verify JSON output
        assert 'overall_score' in result
```

### JavaScript Test Example (Jest)

```javascript
const core = require('@actions/core');

jest.mock('@actions/core');

describe('GitHub Action', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should get input with name', () => {
    core.getInput.mockReturnValueOnce('.');
    const input = core.getInput('path');
    expect(core.getInput).toHaveBeenCalledWith('path');
    expect(input).toBe('.');
  });
});
```

## Test Coverage

### Current Coverage
- **Python:** 10% (target: 25%+)
- **JavaScript:** 0% initially (target: 70%+)
- **Overall:** Target 20%+ for Level 3 readiness

### Measuring Coverage

**Python:**
```bash
# Generate HTML coverage report
pytest tests/ --cov=agent_readiness --cov-report=html

# View report
open htmlcov/index.html
```

**JavaScript:**
```bash
# Generate coverage report
npm run test:coverage

# View report
open coverage/lcov-report/index.html
```

## CI/CD Testing

### GitHub Actions Workflow

Tests run automatically on:
- **Pull Requests:** When Python, JavaScript, JSON, markdown, or TOML files change
- **Push to main:** On every commit to main branch

The workflow:
1. Installs Python 3.11
2. Installs dependencies
3. Runs pytest with coverage threshold (minimum 15%)
4. Runs parallel tests for speed
5. Generates coverage reports
6. Runs agent-readiness check

See `.github/workflows/agent-readiness-check.yml` for details.

## Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names that explain what is tested
- Keep test files focused on one component

### 2. Fixtures and Setup
- Use `@pytest.fixture` for reusable test data
- Use `tmp_path` fixture for temporary directories
- Mock external dependencies (files, networks, etc.)

### 3. Mocking
- Mock file system operations with `tmp_path`
- Mock GitHub Actions API with jest.mock()
- Mock external commands with `monkeypatch`

### 4. Test Isolation
- Each test should be independent
- Clean up resources in teardown
- Use fixtures for common setup

### 5. Coverage
- Aim for >80% coverage of critical paths
- Test both success and failure cases
- Test edge cases and error conditions

## Running Tests Locally

### Development Workflow

```bash
# 1. Install development dependencies
pip install -e ".[dev]"
npm install

# 2. Run all tests
pytest tests/
npm test

# 3. Run with coverage
pytest tests/ --cov=agent_readiness --cov-report=term-missing
npm run test:coverage

# 4. Run tests in watch mode (for development)
pytest tests/ --watch
npm run test:watch

# 5. Run specific tests
pytest tests/test_cli.py -v
npm test -- index.test.js
```

### Pre-commit Testing

Before committing:

```bash
# Run all tests
pytest tests/ -n auto

# Check coverage threshold
pytest tests/ --cov=agent_readiness --cov-fail-under=15

# Run Jest tests
npm test
```

## Continuous Integration

### Coverage Thresholds

The project enforces minimum coverage:
- **Python:** Minimum 15% for CI/CD (locally aim for 25%+)
- **JavaScript:** Minimum 70% for action code (when applicable)

To fail CI if coverage is below threshold:
```bash
pytest --cov=agent_readiness --cov-fail-under=15
```

### Parallel Test Execution

Tests run in parallel using `pytest-xdist`:
```bash
pytest tests/ -n auto
```

This significantly speeds up test execution on multi-core systems.

## Troubleshooting

### Issue: Tests fail with "ModuleNotFoundError"
```bash
# Solution: Install development dependencies
pip install -e ".[dev]"
```

### Issue: Coverage threshold too low
```bash
# Write more tests focusing on uncovered lines
# View coverage report to identify gaps
pytest tests/ --cov=agent_readiness --cov-report=html
open htmlcov/index.html
```

### Issue: Jest tests not found
```bash
# Ensure jest.config.js exists and is correct
# Check test file naming: *.test.js
npm test -- --debug
```

### Issue: Flaky tests (intermittent failures)
- Check for test interdependencies
- Verify no shared state between tests
- Use `monkeypatch` to isolate changes
- Check for timing issues in async operations

## Contributing Tests

When adding features:
1. **Write tests first** (TDD) or **write tests alongside code**
2. Ensure new tests pass locally
3. Run full test suite before submitting PR
4. Maintain or improve code coverage
5. Update this guide if adding new test patterns

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [GitHub Actions Testing Guide](https://docs.github.com/en/actions/creating-actions/testing-your-action)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
