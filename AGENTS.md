# AGENTS.md — Agent Readiness Score

This file helps AI coding agents understand and work with this codebase.

## Project Overview

An open-source CLI tool that evaluates codebases for AI agent readiness across 8 pillars.

## Tech Stack

- **Language**: Python 3.11+
- **CLI**: Click or Typer
- **Output**: JSON, Markdown, terminal
- **Testing**: pytest
- **Packaging**: pip (pyproject.toml)

## Directory Structure

```
agent-readiness-score/
├── src/
│   └── agent_readiness/
│       ├── __init__.py
│       ├── cli.py           # CLI entry point
│       ├── scanner.py       # Core scanning logic
│       └── pillars/         # One module per pillar
│           ├── style.py
│           ├── build.py
│           ├── testing.py
│           ├── documentation.py
│           ├── dev_environment.py
│           ├── debugging.py
│           ├── security.py
│           └── task_discovery.py
├── tests/
├── README.md
├── AGENTS.md
├── pyproject.toml
└── LICENSE
```

### Pillar 1: Style & Validation (`pillars/style.py`)

Checks for:
- **Level 1**: Any linter configuration (ruff, eslint, etc.)
- **Level 2**: Formatter configuration (black, prettier, etc.)
- **Level 3**: Pre-commit hooks, CI linting/formatting
- **Level 4**: Editor integration documentation
- **Level 5**: Style guide for AI agents

**Language Support**: Python, JavaScript/TypeScript, Go, Rust
**CI Detection**: GitHub Actions, GitLab CI, CircleCI, Jenkins, Travis CI

## Key Commands

```bash
# Install in dev mode
pip install -e .

# Run tests
pytest

# Run linting
ruff check .

# Run the CLI
agent-readiness /path/to/repo
```

## Contributing

1. Each pillar is a separate module in `src/agent_readiness/pillars/`
2. Each check returns a `CheckResult` with pass/fail and explanation
3. Pillars aggregate checks into a pillar score
4. Main scanner aggregates pillars into overall score

## Code Style

- Use type hints everywhere
- Docstrings for public functions
- One check per function
- Checks should be fast (<1 second each)
