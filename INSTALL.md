# Installation Guide

## Prerequisites

- Python 3.11 or higher
- pip and venv (included with Python)

## Quick Start (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/jpequegn/agent-readiness-score.git
cd agent-readiness-score

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 3. Install with locked dependencies
pip install -r requirements.txt

# 4. Verify installation
agent-readiness --help
```

## Installation Options

### Option 1: Production Use (Recommended)

Install only core runtime dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Use case**: Running the CLI tool, GitHub Action, or MCP server

### Option 2: Development

Install all development tools (testing, linting, type checking):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

**Use case**: Contributing to the project, running tests, code quality checks

### Option 3: Editable Development

For modifying source code with immediate effect:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

**Use case**: Active development, debugging, experimenting

### Option 4: Complete Lock File

For exact reproducibility with all dependencies mapped:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --requirement requirements.lock
```

**Use case**: CI/CD, Docker builds, exact environment matching

## Lock Files Explained

### `requirements.txt`
- **Size**: 172 bytes
- **Dependencies**: 5 core packages
- **Use**: Production, minimal installations
- **Updated**: After adding/removing dependencies

```bash
pip install -r requirements.txt
```

### `requirements-dev.txt`
- **Size**: 587 bytes
- **Dependencies**: 23 packages (runtime + dev)
- **Use**: Local development, all tools included
- **Includes**: pytest, ruff, black, mypy, coverage

```bash
pip install -r requirements-dev.txt
```

### `requirements.lock`
- **Size**: 1.2K
- **Format**: Comprehensive lock with dependency tree
- **Use**: Exact reproducibility, CI/CD pipelines, scanner compliance
- **Tool**: Generated with `uv pip compile`
- **Recognized by**: Build System, Security, Dev Environment pillars

```bash
pip install --requirement requirements.lock
```

## Reproducing Environments

### On Same Machine

```bash
# Same setup, same versions
pip install -r requirements.txt
```

### Across Different Machines

```bash
# Guaranteed exact environment
pip install --requirement requirements.lock
```

### In Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["agent-readiness"]
```

### In CI/CD

```yaml
- name: Install dependencies
  run: |
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

## Using the CLI

### After Installation

```bash
# Make sure venv is activated
source venv/bin/activate

# Scan current directory
agent-readiness .

# Scan specific path
agent-readiness /path/to/repo

# Output as JSON
agent-readiness . --format json

# Check specific pillar
agent-readiness . --pillar "Testing"

# Quality gate check
agent-readiness . --level 3 --fail-below
```

## Updating Dependencies

### Check for Updates

```bash
source venv/bin/activate
pip list --outdated
```

### Update Core Dependencies

```bash
# Update requirements.txt
pip install --upgrade click rich

# Regenerate lock file
uv pip freeze > requirements.txt
```

### Update Dev Dependencies

```bash
# Update requirements-dev.txt
pip install --upgrade pytest ruff black mypy

# Regenerate lock file
uv pip freeze > requirements-dev.txt
```

### Regenerate All Lock Files

```bash
source venv/bin/activate
pip install -e ".[dev]"

# Generate all lock files
uv pip freeze > requirements-dev.txt
uv pip freeze | grep -v "^-e" > requirements.txt
uv pip compile pyproject.toml --all-extras -o requirements.lock
```

## Troubleshooting

### "externally managed environment" Error

This is a Python 3.11+ safety feature. Use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "command not found: agent-readiness"

Make sure the virtual environment is activated:

```bash
source venv/bin/activate
agent-readiness --help
```

### Permission Denied

Use the `--user` flag:

```bash
pip install --user -r requirements.txt
```

### ModuleNotFoundError

Install all dependencies:

```bash
pip install -r requirements-dev.txt
```

### Different Python Version

Create new venv with specific Python version:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development Workflow

### First Time Setup

```bash
# Clone and setup
git clone https://github.com/jpequegn/agent-readiness-score.git
cd agent-readiness-score

# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Check code quality
ruff check .
black --check .
mypy src/
```

### Daily Development

```bash
# Activate environment
cd agent-readiness-score
source venv/bin/activate

# Make changes and test
pytest tests/

# Check quality
ruff check .
black .

# Run CLI
agent-readiness /path/to/repo
```

### Before Committing

```bash
# Run all checks
pytest --cov
ruff check .
black .
mypy src/

# If all pass, commit
git add .
git commit -m "description"
```

## Deactivating Virtual Environment

```bash
deactivate
```

## System-Wide Installation (Not Recommended)

To install system-wide (requires `sudo`):

```bash
sudo pip install agent-readiness-score
agent-readiness --help
```

**⚠️ Not recommended** as it can conflict with system packages.

## Platform-Specific Notes

### macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Linux (Ubuntu/Debian)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Windows (Command Prompt)

```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Support

For issues:
1. Check [GitHub Issues](https://github.com/jpequegn/agent-readiness-score/issues)
2. Create a new issue with:
   - Python version: `python3 --version`
   - Output of: `pip list`
   - Error message and traceback

---

**Happy scanning! 🦞**
