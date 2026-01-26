const core = require('@actions/core');
const github = require('@actions/github');
const exec = require('@actions/exec');
const fs = require('fs');
const path = require('path');

async function run() {
  try {
    // Get inputs
    const scanPath = core.getInput('path') || '.';
    const minLevel = parseInt(core.getInput('min-level') || '3');
    const failBelow = core.getInput('fail-below') === 'true';
    const pillars = core.getInput('pillars') || '';
    const format = core.getInput('format') || 'markdown';
    const commentOnPr = core.getInput('comment-on-pr') === 'true';
    const failOnError = core.getInput('fail-on-error') === 'true';

    core.info(`🦞 Agent Readiness Score Scanner`);
    core.info(`Scanning: ${scanPath}`);
    core.info(`Min Level: ${minLevel}`);
    core.info(`Fail if below: ${failBelow}`);

    // Build agent-readiness command
    let cmd = ['agent-readiness', scanPath];

    if (pillars) {
      const pillarList = pillars.split(',').map(p => p.trim());
      for (const pillar of pillarList) {
        cmd.push('--pillar', pillar);
      }
    }

    cmd.push('--format', 'json');

    // Run scanner and capture output
    let scanOutput = '';
    const options = {
      listeners: {
        stdout: (data) => {
          scanOutput += data.toString();
        },
      },
      ignoreReturnCode: true,
    };

    core.info(`Running: ${cmd.join(' ')}`);
    const exitCode = await exec.exec(cmd[0], cmd.slice(1), options);

    // Parse JSON output
    let result;
    try {
      result = JSON.parse(scanOutput);
    } catch (e) {
      core.error(`Failed to parse scan output as JSON`);
      core.error(`Output: ${scanOutput}`);
      if (failOnError) {
        core.setFailed(`Failed to parse scan results: ${e.message}`);
      }
      return;
    }

    // Extract results
    const score = Math.round(result.overall_score);
    const level = result.maturity_level;
    const passed = result.summary.passed;
    const failed = result.summary.failed;
    const summary = result.summary;

    core.info(`✅ Scan completed`);
    core.info(`Score: ${score}% (Level ${level})`);
    core.info(`Checks: ${passed} passed, ${failed} failed`);

    // Set outputs
    core.setOutput('score', score.toString());
    core.setOutput('level', level.toString());
    core.setOutput('passed', passed.toString());
    core.setOutput('failed', failed.toString());
    core.setOutput('json', JSON.stringify(result, null, 2));

    // Generate markdown report
    const report = generateReport(result, score, level, minLevel);
    core.setOutput('report', report);

    // Post PR comment if applicable
    if (commentOnPr && github.context.payload.pull_request) {
      await postPrComment(report, score, level, minLevel);
    }

    // Determine if we should fail
    let shouldFail = false;
    let failMessage = '';

    if (failBelow && level < minLevel) {
      shouldFail = true;
      failMessage = `Readiness score ${score}% (Level ${level}) is below minimum required level ${minLevel}`;
    }

    if (shouldFail) {
      core.setFailed(failMessage);
    } else {
      core.info(`✅ Passed readiness check: Level ${level} >= ${minLevel}`);
    }

  } catch (error) {
    if (core.getInput('fail-on-error') === 'true') {
      core.setFailed(`Action failed: ${error.message}`);
    } else {
      core.warning(`Action warning: ${error.message}`);
    }
  }
}

function generateReport(result, score, level, minLevel) {
  const lines = [];

  // Header
  lines.push('## 🦞 Agent Readiness Score Report');
  lines.push('');

  // Summary box
  const levelLabel = getLevelLabel(level);
  const passEmoji = level >= minLevel ? '✅' : '⚠️';
  lines.push(`${passEmoji} **Score:** ${score}% | **Level:** ${level}/5 (${levelLabel})`);
  lines.push('');

  // Summary stats
  lines.push('### Summary');
  lines.push(`- **Total Checks:** ${result.summary.total_checks}`);
  lines.push(`- **Passed:** ${result.summary.passed} ✅`);
  lines.push(`- **Failed:** ${result.summary.failed} ❌`);
  lines.push(`- **Pass Rate:** ${result.summary.pass_rate}`);
  lines.push('');

  // Pillar scores
  lines.push('### Pillar Scores');
  lines.push('');
  lines.push('| Pillar | Score | Level | Checks |');
  lines.push('|--------|-------|-------|--------|');

  for (const pillar of result.pillars) {
    const pillarScore = Math.round(pillar.score);
    const pillarLevel = getLevelFromScore(pillar.score);
    const checks = `${pillar.passed}/${pillar.total}`;
    lines.push(`| ${pillar.name} | ${pillarScore}% | ${pillarLevel} | ${checks} |`);
  }
  lines.push('');

  // Failed checks summary
  const failedChecks = [];
  for (const pillar of result.pillars) {
    for (const check of pillar.checks) {
      if (!check.passed) {
        failedChecks.push({ pillar: pillar.name, check });
      }
    }
  }

  if (failedChecks.length > 0) {
    lines.push('### Failed Checks');
    lines.push('');
    const topFailed = failedChecks.slice(0, 10);
    for (const item of topFailed) {
      lines.push(`- ❌ **${item.pillar}**: ${item.check.name}`);
      lines.push(`  - Level ${item.check.level}: ${item.check.message}`);
    }
    if (failedChecks.length > 10) {
      lines.push(`- ... and ${failedChecks.length - 10} more`);
    }
    lines.push('');
  }

  // Recommendations
  lines.push('### Next Steps');
  if (level < minLevel) {
    lines.push(`⚠️ **Below Minimum:** Current level ${level} is below required level ${minLevel}`);
    lines.push('');
  }

  if (failedChecks.length > 0) {
    const bySeverity = {};
    for (const item of failedChecks) {
      const severity = item.check.severity;
      if (!bySeverity[severity]) {
        bySeverity[severity] = [];
      }
      bySeverity[severity].push(item);
    }

    if (bySeverity.critical && bySeverity.critical.length > 0) {
      lines.push(`🔴 **Critical Issues:** ${bySeverity.critical.length} critical checks need attention`);
    }
    if (bySeverity.error && bySeverity.error.length > 0) {
      lines.push(`🟠 **Errors:** ${bySeverity.error.length} error-level checks to fix`);
    }
    if (bySeverity.warning && bySeverity.warning.length > 0) {
      lines.push(`🟡 **Warnings:** ${bySeverity.warning.length} warnings to address`);
    }
  } else {
    lines.push('✅ All checks passing!');
  }

  lines.push('');
  lines.push('---');
  lines.push('_Generated by [Agent Readiness Score](https://github.com/jpequegn/agent-readiness-score)_');

  return lines.join('\n');
}

function getLevelLabel(level) {
  const labels = {
    1: 'Initial - Ad-hoc',
    2: 'Developing - Basic',
    3: 'Defined - Standardized',
    4: 'Managed - Measured',
    5: 'Optimizing - Continuous',
  };
  return labels[level] || 'Unknown';
}

function getLevelFromScore(score) {
  if (score < 40) return 1;
  if (score < 60) return 2;
  if (score < 80) return 3;
  if (score < 95) return 4;
  return 5;
}

async function postPrComment(report, score, level, minLevel) {
  try {
    const token = core.getInput('token') || process.env.GITHUB_TOKEN;
    if (!token) {
      core.warning('GITHUB_TOKEN not available, skipping PR comment');
      return;
    }

    const octokit = github.getOctokit(token);
    const context = github.context;
    const pullNumber = context.payload.pull_request?.number;

    if (!pullNumber) {
      core.info('Not a pull request, skipping comment');
      return;
    }

    // Check if comment already exists
    const comments = await octokit.rest.issues.listComments({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: pullNumber,
    });

    const existingComment = comments.data.find(
      comment => comment.user.type === 'Bot' &&
                  comment.body.includes('🦞 Agent Readiness Score Report')
    );

    const body = report;

    if (existingComment) {
      // Update existing comment
      await octokit.rest.issues.updateComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        comment_id: existingComment.id,
        body,
      });
      core.info('✅ Updated PR comment');
    } else {
      // Create new comment
      await octokit.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: pullNumber,
        body,
      });
      core.info('✅ Posted PR comment');
    }
  } catch (error) {
    core.warning(`Failed to post PR comment: ${error.message}`);
  }
}

// Run the action
run();
