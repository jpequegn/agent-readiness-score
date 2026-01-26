# Agent Readiness Score GitHub Action

Automatically check your repository's agent readiness score in GitHub Actions CI/CD pipelines.

## Features

- **Automated Scanning**: Run comprehensive readiness checks on every push/PR
- **Quality Gates**: Enforce minimum readiness levels for your codebase
- **PR Comments**: Automatic comments on pull requests with detailed reports
- **Flexible Configuration**: Customize which pillars to check and minimum requirements
- **Multiple Formats**: JSON, Markdown, or text output
- **Structured Outputs**: Get score, level, and counts for further processing

## Quick Start

### Basic Usage

```yaml
- name: Check Agent Readiness
  uses: jpequegn/agent-readiness-score@v1
  with:
    path: .
    min-level: 3
    fail-below: true
```

### With PR Comments

```yaml
- name: Check Agent Readiness
  uses: jpequegn/agent-readiness-score@v1
  with:
    path: .
    min-level: 3
    fail-below: true
    comment-on-pr: true
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `path` | Directory to scan | false | `.` |
| `min-level` | Minimum required maturity level (1-5) | false | `3` |
| `fail-below` | Fail if score below min-level | false | `true` |
| `pillars` | Comma-separated pillar names to check | false | `` (all) |
| `format` | Output format: text, json, markdown | false | `markdown` |
| `comment-on-pr` | Post results as PR comment | false | `true` |
| `fail-on-error` | Fail if scan encounters error | false | `false` |

## Outputs

| Output | Description |
|--------|-------------|
| `score` | Overall readiness score (0-100) |
| `level` | Maturity level (1-5) |
| `passed` | Number of passing checks |
| `failed` | Number of failing checks |
| `report` | Markdown-formatted report |
| `json` | Full results as JSON |

## Examples

### Example 1: Enforce Level 3+ on Main Branch

```yaml
name: Readiness Check

on:
  push:
    branches: [main]

jobs:
  readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install agent-readiness-score
      - uses: jpequegn/agent-readiness-score@v1
        with:
          path: .
          min-level: 3
          fail-below: true
```

### Example 2: Security Pillar Only

```yaml
- name: Security Check
  uses: jpequegn/agent-readiness-score@v1
  with:
    path: .
    pillars: Security
    min-level: 3
    fail-below: true
```

### Example 3: Report Only (No Failure)

```yaml
- name: Generate Report
  uses: jpequegn/agent-readiness-score@v1
  with:
    path: .
    fail-below: false
    format: markdown
```

### Example 4: JSON Output for Analysis

```yaml
- name: Check Readiness
  uses: jpequegn/agent-readiness-score@v1
  id: readiness
  with:
    format: json
    fail-below: false

- name: Use Results
  run: |
    echo "Score: ${{ steps.readiness.outputs.score }}"
    echo "Level: ${{ steps.readiness.outputs.level }}"
    echo "Passed: ${{ steps.readiness.outputs.passed }}"
    echo "Failed: ${{ steps.readiness.outputs.failed }}"
```

### Example 5: Upload Reports as Artifacts

```yaml
- name: Check Readiness
  uses: jpequegn/agent-readiness-score@v1
  id: readiness
  with:
    format: markdown

- name: Upload Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: readiness-report
    path: readiness-report.md
```

## Maturity Levels

- **Level 1** (Initial): Ad-hoc, unpredictable processes
- **Level 2** (Developing): Basic processes in place
- **Level 3** (Defined): Documented and standardized ✓ (recommended minimum)
- **Level 4** (Managed): Measured and controlled
- **Level 5** (Optimizing): Continuous improvement

## The 8 Pillars

The action checks across 8 key pillars:

1. **Style & Validation** - Linting, formatting, and code standards
2. **Build System** - Build automation and dependency management
3. **Testing** - Test coverage and CI integration
4. **Documentation** - README, CONTRIBUTING, API docs
5. **Dev Environment** - Setup reproducibility and devcontainers
6. **Debugging & Observability** - Logging, monitoring, profiling
7. **Security** - Secret scanning, vulnerability checks
8. **Task Discovery** - Issues, PR templates, project boards

## PR Comments

When `comment-on-pr: true` (default), the action will:

- Post a comprehensive report on each PR
- Show score and maturity level
- List pillar scores
- Highlight top failed checks
- Provide actionable recommendations
- Update the comment on subsequent runs

## Environment Variables

- `GITHUB_TOKEN`: Required for posting PR comments (typically `${{ secrets.GITHUB_TOKEN }}`)

## Fail Conditions

The action fails (exits with code 1) when:

- `fail-below: true` AND `level < min-level`
- `fail-on-error: true` AND an error occurs during scanning

## Tips & Best Practices

### 1. Run on PRs for Quick Feedback

```yaml
on:
  pull_request:
    paths:
      - '**.py'
      - '**.js'
      - 'pyproject.toml'
      - 'package.json'
```

### 2. Use Different Thresholds per Branch

```yaml
- name: Check Readiness
  uses: jpequegn/agent-readiness-score@v1
  with:
    path: .
    min-level: ${{ github.ref == 'refs/heads/main' && 4 || 3 }}
```

### 3. Comment Only on PRs (Not Push)

```yaml
- name: Check Readiness
  uses: jpequegn/agent-readiness-score@v1
  with:
    comment-on-pr: ${{ github.event_name == 'pull_request' }}
```

### 4. Save Results for Tracking

```yaml
- name: Save Results
  run: |
    mkdir -p readiness-reports
    echo "${{ steps.readiness.outputs.json }}" > readiness-reports/report-${{ github.run_id }}.json

- name: Upload
  uses: actions/upload-artifact@v3
  with:
    name: reports
    path: readiness-reports/
```

## Troubleshooting

### Action not finding agent-readiness

Ensure you install the package before running the action:

```yaml
- run: pip install agent-readiness-score
```

### PR comments not posting

Check that:
1. `GITHUB_TOKEN` is provided (set in env)
2. Action has permission to write comments (check workflow permissions)
3. You're in a pull request context

### Action timeout

For large repositories, increase the timeout in your workflow:

```yaml
- uses: jpequegn/agent-readiness-score@v1
  timeout-minutes: 30
```

## Support

For issues, questions, or feature requests, see [GitHub Issues](https://github.com/jpequegn/agent-readiness-score/issues).

---

Made with 🦞 by the Agent Readiness Score team
