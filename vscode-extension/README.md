# Agent Readiness Score - VS Code Extension

Measure how ready your codebase is for AI coding agents directly in VS Code.

## Features

- **Status Bar Score**: See your overall readiness score at a glance
- **Pillar Breakdown**: Explore scores across 8 technical pillars
- **Failed Checks View**: Quickly identify what needs improvement
- **Auto-scan**: Automatically scan when you open a workspace

## Requirements

This extension requires the `agent-readiness` CLI tool:

```bash
pip install agent-readiness-score
```

## Usage

1. Open a workspace in VS Code
2. The extension will automatically scan (or click the status bar item)
3. View results in the sidebar under "Agent Readiness"
4. Click on pillars to see individual checks

## Extension Settings

- `agentReadiness.scanOnOpen`: Auto-scan when workspace opens (default: true)
- `agentReadiness.cliPath`: Path to agent-readiness CLI (default: "agent-readiness")
- `agentReadiness.targetLevel`: Target maturity level (default: 3)

## The 8 Pillars

| # | Pillar | What it Measures |
|---|--------|------------------|
| 1 | Style & Validation | Linting, formatting, pre-commit hooks |
| 2 | Build System | Build reproducibility, dependency management |
| 3 | Testing | Test coverage, test speed, test isolation |
| 4 | Documentation | AGENTS.md, README quality, inline docs |
| 5 | Dev Environment | Devcontainer, .env.example, setup scripts |
| 6 | Debugging & Observability | Logging, error messages, debugging tools |
| 7 | Security | Secret scanning, dependency auditing |
| 8 | Task Discovery | Issue templates, PR templates, contribution guides |

## Maturity Levels

- **Level 1 - Functional**: Basic functionality, agents struggle
- **Level 2 - Documented**: Some docs exist, agents can navigate
- **Level 3 - Standardized**: Consistent patterns, agents productive
- **Level 4 - Optimized**: Fast feedback, agents highly effective
- **Level 5 - Autonomous**: Self-healing, agents work independently

**Target: Level 3** — This is where agents become genuinely productive.

## Links

- [GitHub Repository](https://github.com/jpequegn/agent-readiness-score)
- [Report Issues](https://github.com/jpequegn/agent-readiness-score/issues)

---

*"Why did the lobster refuse to share its code? Because it was too shellfish!"* 🦞
