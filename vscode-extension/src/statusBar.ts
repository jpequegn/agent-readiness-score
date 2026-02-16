/**
 * Status bar integration - shows overall score
 */

import * as vscode from 'vscode';
import { ScanResult, getScoreEmoji } from './types';

export class StatusBarManager {
  private statusBarItem: vscode.StatusBarItem;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = 'agentReadiness.scan';
    this.statusBarItem.tooltip = 'Click to run Agent Readiness scan';
    this.setIdle();
  }

  /**
   * Show idle state (no scan results)
   */
  setIdle(): void {
    this.statusBarItem.text = '$(beaker) ARS';
    this.statusBarItem.backgroundColor = undefined;
    this.statusBarItem.show();
  }

  /**
   * Show scanning state
   */
  setScanning(): void {
    this.statusBarItem.text = '$(sync~spin) Scanning...';
    this.statusBarItem.backgroundColor = undefined;
  }

  /**
   * Show scan results
   */
  setResult(result: ScanResult): void {
    const emoji = getScoreEmoji(result.overall_score);
    const score = Math.round(result.overall_score);
    this.statusBarItem.text = `${emoji} ${score}% L${result.maturity_level}`;
    this.statusBarItem.tooltip = `Agent Readiness: ${score}% (Level ${result.maturity_level})\n` +
      `${result.summary.passed}/${result.summary.total_checks} checks passed\n` +
      `Click to re-scan`;

    // Set background color based on score
    if (result.overall_score < 40) {
      this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    } else if (result.overall_score < 60) {
      this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    } else {
      this.statusBarItem.backgroundColor = undefined;
    }
  }

  /**
   * Show error state
   */
  setError(message: string): void {
    this.statusBarItem.text = '$(error) ARS Error';
    this.statusBarItem.tooltip = message;
    this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
  }

  dispose(): void {
    this.statusBarItem.dispose();
  }
}
