---
name: AgentReadiness
description: Check if a repository is ready for AI agents to work on it. Provides readiness scores across 8 pillars (Style, Build, Testing, Documentation, Dev Environment, Debugging, Security, Task Discovery) and returns detailed recommendations. USE WHEN user wants to evaluate code quality for AI agents, check repo readiness, scan codebase structure, OR needs agent-readiness assessment.
---

# AgentReadiness Skill

**Evaluate any codebase's readiness for AI coding agents.**

Clawdbot can assess how well-prepared a repository is for autonomous AI development using the Agent Readiness Score framework. The assessment covers 8 critical infrastructure pillars and returns actionable recommendations.

## Workflow Routing

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **ScanRepository** | "check if my repo is agent-ready", "evaluate codebase" | Full readiness scan |
| **ScanPillar** | "check testing setup", "what about security?" | Single pillar assessment |
| **GetRecommendations** | "how do I improve?", "what should I fix first?" | Actionable improvements |

## The 8 Pillars

1. **Style & Validation** — Linting, formatting, code standards
2. **Build System** — Build automation, dependency management
3. **Testing** — Test coverage, CI integration, test speed
4. **Documentation** — AGENTS.md, README quality, API docs
5. **Dev Environment** — Devcontainer, .env.example, reproducibility
6. **Debugging & Observability** — Logging, error messages, profiling
7. **Security** — Secret scanning, vulnerability checks
8. **Task Discovery** — Issue templates, PR templates, contribution guides

## Maturity Levels

| Level | Name | What It Means |
|-------|------|---------------|
| 1 | Functional | Basic functionality, agents struggle |
| 2 | Documented | Some docs exist, agents can navigate |
| 3 | Standardized | Consistent patterns, agents productive ✓ **TARGET** |
| 4 | Optimized | Fast feedback, agents highly effective |
| 5 | Autonomous | Self-healing, agents work independently |

**Target: Level 3** — Where AI agents become genuinely productive.

## Usage Examples

### Example 1: Quick Repository Assessment

```
User: "Can you check if my repo is agent-ready?"

Larry: *scanning repository...*

🦞 **Agent Readiness Assessment**

**Overall Score:** 67% (Level 3 - Standardized)
Your repository is ready for AI agents! Consistent infrastructure patterns allow agents to work productively.

📊 **Pillar Breakdown:**
- Style & Validation: 85% (Level 4) ✅
- Build System: 70% (Level 3) ✅
- Testing: 65% (Level 3) ✅
- Documentation: 55% (Level 2) ⚠️
- Dev Environment: 60% (Level 3) ✅
- Debugging & Observability: 50% (Level 2) ⚠️
- Security: 75% (Level 3) ✅
- Task Discovery: 45% (Level 2) ⚠️

🎯 **Top Recommendations:**
1. Add AGENTS.md with dev setup instructions
2. Document debugging approach (logging, error handling)
3. Create issue templates for better task discovery
```

### Example 2: Specific Pillar Check

```
User: "What about security in my repo?"

Larry:

🔒 **Security Pillar Assessment**

**Score:** 75% (Level 3)

✅ Checks Passing:
- Dependency vulnerability scanning configured
- Secret scanning enabled via pre-commit hooks
- CODEOWNERS file present

❌ Checks Failing:
- Security policy document missing
- No automated dependency updates

**Recommendations:**
- Create SECURITY.md with vulnerability reporting process
- Set up Dependabot for automatic dependency updates
```

### Example 3: Improvement Path

```
User: "How do I improve my repo for agents?"

Larry:

📈 **Improvement Recommendations**

**Highest Impact (Do First):**
1. Add AGENTS.md — Helps agents understand project structure
2. Document dev environment setup
3. Create issue templates

**Medium Impact:**
1. Improve code documentation quality
2. Add observable error messages and logging
3. Configure dependency scanning

**Nice to Have:**
1. Performance profiling setup
2. Architectural decision records (ADRs)
3. Cross-repo consistency dashboard
```

## Installation

The skill is available in the agent-readiness-score repository:

```bash
# Install the package first
pip install agent-readiness-score

# Or install from source
git clone https://github.com/jpequegn/agent-readiness-score
cd agent-readiness-score
pip install -e .
```

## How It Works

1. **Scan** — Repository files analyzed across 8 pillars
2. **Score** — Each pillar scored on 5-level maturity scale
3. **Recommend** — AI-friendly improvements identified
4. **Report** — Natural language summary with actionable steps

## Technical Details

- **Language**: Python 3.11+
- **Framework**: Click CLI + Rich terminal formatting
- **Output**: JSON (structured data), Markdown (reports), Natural Language (Clawdbot)
- **Speed**: Typical scan completes in <5 seconds
- **No Dependencies**: Scans don't require repo to be installed

## Advanced Features

### Track Over Time

Larry can monitor your repository's readiness across multiple scans:

```
User: "How has my repo improved?"

Larry: *analyzing scan history*

📈 **Agent Readiness Trend (Last 3 Months)**

67% → 72% → 78%

You're making great progress! Security and documentation improved significantly.
```

### Compare Repositories

```
User: "How does my repo compare to [other-repo]?"

Larry: *comparing readiness scores*

📊 **Comparative Analysis**

Your Repo vs Other Repo:
- Overall: 67% vs 82% (+15 points other-repo)
- Testing: 65% vs 90% (+25 points other-repo)
- Documentation: 55% vs 60% (+5 points other-repo)

Other Repo excels at testing and security. Your strengths: Build System and Style consistency.
```

## Capabilities

- ✅ Full repository readiness assessment
- ✅ Individual pillar deep-dives
- ✅ Actionable improvement recommendations
- ✅ Natural language output formatting
- ✅ JSON structured data for programmatic use
- ✅ CI/CD integration support
- ✅ Cross-repository comparison
- ✅ Trend tracking over time

## Integration Points

This skill integrates with:
- **GitHub Action** — Automatic PR checks
- **CLI Tool** — Standalone scanning
- **MCP Server** — Claude Code IDE integration
- **Clawdbot** — Natural language interface (this skill)

---

**Made with 🦞 by the Agent Readiness Score team**
