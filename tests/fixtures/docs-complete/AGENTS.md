# AI Agent Readiness Guide

## Architecture Overview

This project follows a modular architecture with:
- `src/myproject/` - Core library code
- `tests/` - Test suite
- `examples/` - Usage examples
- `docs/` - Documentation

## Development Setup

1. Clone the repository
2. Install with `pip install -e ".[dev]"`
3. Run tests with `pytest`

## Key File Locations

- Main module: `src/myproject/__init__.py`
- Core logic: `src/myproject/core.py`
- Tests: `tests/test_*.py`
- Examples: `examples/`

## Running Tests

```bash
pytest
pytest tests/
pytest -v  # verbose
```

## Common Tasks

- Run linter: `make lint`
- Run tests: `make test`
- Build docs: `make docs`
