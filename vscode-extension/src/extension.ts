/**
 * Agent Readiness Score - VS Code Extension
 *
 * Measures how ready your codebase is for AI coding agents.
 */

import * as vscode from 'vscode';
import { Scanner } from './scanner';
import { StatusBarManager } from './statusBar';
import { PillarsTreeProvider, FailedChecksTreeProvider } from './treeView';
import { ScanResult } from './types';

let scanner: Scanner;
let statusBar: StatusBarManager;
let pillarsTree: PillarsTreeProvider;
let failedChecksTree: FailedChecksTreeProvider;
let lastScanResult: ScanResult | null = null;

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext): void {
  console.log('Agent Readiness Score extension activating...');

  // Initialize components
  scanner = new Scanner();
  statusBar = new StatusBarManager();
  pillarsTree = new PillarsTreeProvider();
  failedChecksTree = new FailedChecksTreeProvider();

  // Register tree views
  const pillarsTreeView = vscode.window.createTreeView('agentReadiness.pillars', {
    treeDataProvider: pillarsTree,
    showCollapseAll: true,
  });

  const failedChecksTreeView = vscode.window.createTreeView('agentReadiness.failedChecks', {
    treeDataProvider: failedChecksTree,
  });

  // Register commands
  const scanCommand = vscode.commands.registerCommand('agentReadiness.scan', runScan);
  const showDetailsCommand = vscode.commands.registerCommand('agentReadiness.showDetails', showDetails);

  // Add to subscriptions
  context.subscriptions.push(
    scanner,
    statusBar,
    pillarsTreeView,
    failedChecksTreeView,
    scanCommand,
    showDetailsCommand
  );

  // Auto-scan on startup if configured
  const config = vscode.workspace.getConfiguration('agentReadiness');
  if (config.get<boolean>('scanOnOpen', true)) {
    // Delay slightly to let VS Code fully initialize
    setTimeout(() => {
      if (vscode.workspace.workspaceFolders?.length) {
        runScan();
      }
    }, 2000);
  }

  // Watch for workspace changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeWorkspaceFolders(() => {
      if (config.get<boolean>('scanOnOpen', true)) {
        runScan();
      }
    })
  );

  console.log('Agent Readiness Score extension activated');
}

/**
 * Run the agent readiness scan
 */
async function runScan(): Promise<void> {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  if (!workspaceFolder) {
    vscode.window.showWarningMessage('No workspace folder open');
    return;
  }

  // Check if CLI is available
  const cliAvailable = await scanner.checkCliAvailable();
  if (!cliAvailable) {
    const action = await vscode.window.showErrorMessage(
      'agent-readiness CLI not found. Please install it with: pip install agent-readiness-score',
      'Show Installation Instructions',
      'Configure CLI Path'
    );

    if (action === 'Configure CLI Path') {
      vscode.commands.executeCommand('workbench.action.openSettings', 'agentReadiness.cliPath');
    } else if (action === 'Show Installation Instructions') {
      vscode.env.openExternal(vscode.Uri.parse('https://github.com/jpequegn/agent-readiness-score#installation'));
    }
    return;
  }

  statusBar.setScanning();
  pillarsTree.clear();
  failedChecksTree.clear();

  try {
    const result = await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Running Agent Readiness scan...',
        cancellable: false,
      },
      async () => {
        return await scanner.scan(workspaceFolder.uri.fsPath);
      }
    );

    lastScanResult = result;
    statusBar.setResult(result);
    pillarsTree.update(result);
    failedChecksTree.update(result);

    // Show summary notification
    const score = Math.round(result.overall_score);
    const message = `Agent Readiness: ${score}% (Level ${result.maturity_level}) - ${result.summary.passed}/${result.summary.total_checks} checks passed`;

    if (result.overall_score >= 60) {
      vscode.window.showInformationMessage(message);
    } else if (result.overall_score >= 40) {
      vscode.window.showWarningMessage(message);
    } else {
      vscode.window.showWarningMessage(message, 'Show Failed Checks').then((action) => {
        if (action === 'Show Failed Checks') {
          vscode.commands.executeCommand('agentReadiness.failedChecks.focus');
        }
      });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    statusBar.setError(errorMessage);
    vscode.window.showErrorMessage(`Agent Readiness scan failed: ${errorMessage}`);
    scanner.showOutput();
  }
}

/**
 * Show detailed results in a webview
 */
function showDetails(): void {
  if (!lastScanResult) {
    vscode.window.showInformationMessage('No scan results available. Run a scan first.');
    return;
  }

  const panel = vscode.window.createWebviewPanel(
    'agentReadinessDetails',
    'Agent Readiness Details',
    vscode.ViewColumn.One,
    { enableScripts: true }
  );

  panel.webview.html = getWebviewContent(lastScanResult);
}

/**
 * Generate HTML content for the details webview
 */
function getWebviewContent(result: ScanResult): string {
  const pillarRows = result.pillars
    .map((p) => {
      const barWidth = Math.round(p.score);
      const barColor = p.score >= 60 ? '#28a745' : p.score >= 40 ? '#ffc107' : '#dc3545';
      return `
        <tr>
          <td>${p.name}</td>
          <td>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${barWidth}%; background: ${barColor}"></div>
            </div>
          </td>
          <td>${Math.round(p.score)}%</td>
          <td>${p.passed}/${p.total}</td>
        </tr>
      `;
    })
    .join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Readiness Details</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      padding: 20px;
      color: var(--vscode-foreground);
      background: var(--vscode-editor-background);
    }
    h1 { margin-bottom: 5px; }
    .subtitle { color: var(--vscode-descriptionForeground); margin-bottom: 20px; }
    .score-big {
      font-size: 48px;
      font-weight: bold;
      color: ${result.overall_score >= 60 ? '#28a745' : result.overall_score >= 40 ? '#ffc107' : '#dc3545'};
    }
    .level-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      background: var(--vscode-badge-background);
      color: var(--vscode-badge-foreground);
      margin-left: 10px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    th, td {
      padding: 10px;
      text-align: left;
      border-bottom: 1px solid var(--vscode-panel-border);
    }
    th { font-weight: 600; }
    .progress-bar {
      width: 200px;
      height: 8px;
      background: var(--vscode-progressBar-background);
      border-radius: 4px;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.3s;
    }
  </style>
</head>
<body>
  <h1>🦞 Agent Readiness Score</h1>
  <p class="subtitle">${result.target_directory}</p>

  <div>
    <span class="score-big">${Math.round(result.overall_score)}%</span>
    <span class="level-badge">Level ${result.maturity_level}</span>
  </div>

  <p>${result.summary.passed} of ${result.summary.total_checks} checks passed</p>

  <table>
    <thead>
      <tr>
        <th>Pillar</th>
        <th>Progress</th>
        <th>Score</th>
        <th>Checks</th>
      </tr>
    </thead>
    <tbody>
      ${pillarRows}
    </tbody>
  </table>
</body>
</html>`;
}

/**
 * Extension deactivation
 */
export function deactivate(): void {
  console.log('Agent Readiness Score extension deactivated');
}
