# 🦞 Agent Readiness Score

**An open-source framework to measure how ready your codebase is for AI coding agents.**

Inspired by [Factory.ai's Agent Readiness](https://factory.ai/agent-readiness) methodology, this project aims to create a transparent, community-driven tool for evaluating and improving codebase readiness for autonomous AI development.

## Why Agent Readiness?

AI coding agents (Claude Code, Cursor, Copilot, Codex, etc.) work better on some codebases than others. The difference isn't magic — it's **infrastructure**:

- Clear documentation and AGENTS.md files
- Fast feedback loops (pre-commit hooks, quick tests)
- Reproducible environments (devcontainers, .env.example)
- Good task discovery (issue templates, clear contribution guides)

This tool helps you measure and improve these factors.

## The 8 Pillars

We evaluate codebases across 8 technical pillars:

| # | Pillar | What it Measures |
|---|--------|------------------|
| 1 | **Style & Validation** | Linting, formatting, pre-commit hooks |
| 2 | **Build System** | Build reproducibility, dependency management |
| 3 | **Testing** | Test coverage, test speed, test isolation |
| 4 | **Documentation** | AGENTS.md, README quality, inline docs |
| 5 | **Dev Environment** | Devcontainer, .env.example, setup scripts |
| 6 | **Debugging & Observability** | Logging, error messages, debugging tools |
| 7 | **Security** | Secret scanning, dependency auditing |
| 8 | **Task Discovery** | Issue templates, PR templates, contribution guides |

## Maturity Levels

| Level | Name | Description |
|-------|------|-------------|
| 1 | Functional | Basic functionality, agents struggle |
| 2 | Documented | Some docs exist, agents can navigate |
| 3 | Standardized | Consistent patterns, agents productive |
| 4 | Optimized | Fast feedback, agents highly effective |
| 5 | Autonomous | Self-healing, agents work independently |

**Target: Level 3** — This is where agents become genuinely productive.

## Installation

```bash
# Coming soon!
pip install agent-readiness-score
```

## Usage

```bash
# Scan current directory
agent-readiness .

# Scan specific repo
agent-readiness /path/to/repo

# Output JSON for CI integration
agent-readiness . --format json
```

## Contributing

We're building this in the open! Check the [Issues](https://github.com/jpequegn/agent-readiness-score/issues) for ways to contribute.

Each pillar has its own tracking issue with specific metrics to implement.

## Roadmap

- [x] Core scanning framework
- [x] Pillar 1: Style & Validation checks
- [ ] Pillar 2: Build System checks
- [x] Pillar 3: Testing checks
- [ ] Pillar 4: Documentation checks
- [ ] Pillar 5: Dev Environment checks
- [ ] Pillar 6: Debugging & Observability checks
- [ ] Pillar 7: Security checks
- [ ] Pillar 8: Task Discovery checks
- [ ] CLI tool
- [ ] GitHub Action
- [ ] VS Code extension

## License

MIT

---

*"Why did the lobster refuse to share its code? Because it was too shellfish!"* 🦞
