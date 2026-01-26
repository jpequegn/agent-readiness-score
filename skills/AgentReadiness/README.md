# AgentReadiness Clawdbot Skill

Evaluate any codebase's readiness for AI coding agents directly from Clawdbot.

## What It Does

The AgentReadiness skill helps you assess how well-prepared a repository is for autonomous AI development. It evaluates infrastructure across 8 critical pillars and provides actionable recommendations.

## Quick Start

### Installation

```bash
# Install agent-readiness-score
pip install agent-readiness-score

# Or install from source
git clone https://github.com/jpequegn/agent-readiness-score
cd agent-readiness-score
pip install -e .
```

### Using with Clawdbot

Ask Larry to evaluate your repository:

```
User: "Can you check if my repo is agent-ready?"
Larry: *scans repository*
🦞 Your repository scores 67% (Level 3 - Standardized)
```

## Commands

### Full Repository Assessment

```
User: "Check agent readiness for /path/to/repo"
```

Returns overall score, maturity level, and pillar breakdown.

### Specific Pillar Check

```
User: "What about security in my repo?"
```

Detailed assessment of a single pillar with passed/failed checks.

### Improvement Recommendations

```
User: "What should I fix first?"
```

Actionable recommendations prioritized by impact.

## The 8 Pillars

1. **Style & Validation** — Code linting, formatting, standards
2. **Build System** — Build automation, dependency management
3. **Testing** — Test coverage, CI integration, test speed
4. **Documentation** — AGENTS.md, README, API docs
5. **Dev Environment** — Devcontainer, .env.example, reproducibility
6. **Debugging & Observability** — Logging, error handling, profiling
7. **Security** — Secret scanning, vulnerability checks
8. **Task Discovery** — Issue templates, PR templates, contribution guides

## Maturity Levels

- **Level 1** (Functional): Basic functionality, agents struggle
- **Level 2** (Documented): Some docs exist, agents can navigate
- **Level 3** (Standardized): Consistent patterns, agents productive ✅
- **Level 4** (Optimized): Fast feedback, agents highly effective
- **Level 5** (Autonomous): Self-healing, agents work independently

## Output Formats

The skill supports three output formats:

### Natural Language (Default for Clawdbot)

Human-readable assessment with clear recommendations.

```
Larry: "Your repository is agent-ready! Score: 67% (Level 3)"
```

### JSON (Programmatic)

Structured data for integration with other tools.

```json
{
  "overall_score": 67,
  "maturity_level": 3,
  "pillars": [...]
}
```

### Markdown (Reports)

Report-ready format for documentation and dashboards.

## Files

- **SKILL.md** — Skill definition and usage guide
- **scan.py** — Wrapper script with formatting functions
- **README.md** — This file

## Testing

Run the test suite:

```bash
pytest tests/test_clawdbot_skill.py -v
```

Test coverage includes:
- Score-to-level conversion
- Output formatting (natural, markdown, JSON)
- Pillar assessment
- Recommendation generation
- Error handling

## Integration Points

This skill works with:

- **agent-readiness-score CLI** — Underlying scanning engine
- **GitHub Action** — Automatic PR checks
- **MCP Server** — Claude Code IDE integration
- **Clawdbot** — This integration point

## Examples

### Example 1: Full Assessment

```
User: "Evaluate my project for agent-readiness"

Larry:
🦞 Agent Readiness Assessment

Overall Score: 72% (Level 3 - Standardized)

📊 Pillar Breakdown:
  • Style & Validation: 85% (Level 4) ✅
  • Build System: 75% (Level 3) ✅
  • Testing: 70% (Level 3) ✅
  • Documentation: 60% (Level 2) ⚠️
  • Dev Environment: 65% (Level 3) ✅
  • Debugging & Observability: 55% (Level 2) ⚠️
  • Security: 80% (Level 3) ✅
  • Task Discovery: 50% (Level 2) ⚠️

🎯 Top Recommendations:
  • Add AGENTS.md with dev setup instructions
  • Document debugging approach
  • Create issue templates
```

### Example 2: Improvement Path

```
User: "How do I improve documentation?"

Larry:
📚 Documentation Pillar Analysis

Current Score: 60% (Level 2)

✅ What's Good:
  • README.md is comprehensive
  • API endpoints documented

❌ What's Missing:
  • AGENTS.md for agent integration
  • Inline code documentation
  • Architecture decision records

Recommendations:
  1. Create AGENTS.md with development setup
  2. Add docstrings to public functions (Level 3)
  3. Document development environment (Level 3)
```

## Advanced Usage

### Track Over Time

```
User: "Show me my repository's readiness trend"
```

Compare scores across multiple scans to see progress.

### Compare Repositories

```
User: "How does my repo compare to another-repo?"
```

Side-by-side readiness comparison for benchmarking.

## Troubleshooting

### "agent-readiness-score not installed"

```bash
pip install agent-readiness-score
```

### Invalid repository path

Ensure the path points to a valid Git repository or source code directory.

### Slow scans

For large repositories, initial scans may take 10-30 seconds. Subsequent scans are faster due to caching.

## Contributing

To improve this skill:

1. Report issues on GitHub
2. Submit pull requests with improvements
3. Add new output formats or pillars
4. Enhance recommendations based on pillar data

## License

MIT - See LICENSE file in agent-readiness-score repository

---

**Made with 🦞 by the Agent Readiness Score team**
