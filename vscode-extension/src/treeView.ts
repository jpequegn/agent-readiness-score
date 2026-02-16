/**
 * Tree view providers for the sidebar
 */

import * as vscode from 'vscode';
import { ScanResult, PillarResult, CheckResult, getScoreEmoji } from './types';

/**
 * Tree item representing a pillar or check
 */
export class ReadinessTreeItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly pillar?: PillarResult,
    public readonly check?: CheckResult
  ) {
    super(label, collapsibleState);

    if (pillar) {
      // Pillar item
      const emoji = getScoreEmoji(pillar.score);
      this.label = `${emoji} ${pillar.name}`;
      this.description = `${Math.round(pillar.score)}% (${pillar.passed}/${pillar.total})`;
      this.tooltip = `${pillar.name}: ${pillar.score.toFixed(1)}%\n${pillar.passed} passed, ${pillar.failed} failed`;
      this.contextValue = 'pillar';
    } else if (check) {
      // Check item
      const icon = check.passed ? '$(check)' : '$(x)';
      this.label = `${icon} ${check.name}`;
      this.description = `L${check.level}`;
      this.tooltip = check.message;
      this.contextValue = check.passed ? 'checkPassed' : 'checkFailed';
      this.iconPath = check.passed
        ? new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'))
        : new vscode.ThemeIcon('x', new vscode.ThemeColor('testing.iconFailed'));
    }
  }
}

/**
 * Provides tree data for the pillars view
 */
export class PillarsTreeProvider implements vscode.TreeDataProvider<ReadinessTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<ReadinessTreeItem | undefined | null | void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private scanResult: ScanResult | null = null;

  /**
   * Update with new scan results
   */
  update(result: ScanResult): void {
    this.scanResult = result;
    this._onDidChangeTreeData.fire();
  }

  /**
   * Clear the tree
   */
  clear(): void {
    this.scanResult = null;
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: ReadinessTreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: ReadinessTreeItem): ReadinessTreeItem[] {
    if (!this.scanResult) {
      return [];
    }

    if (!element) {
      // Root level - show pillars
      return this.scanResult.pillars.map(
        (pillar) =>
          new ReadinessTreeItem(
            pillar.name,
            vscode.TreeItemCollapsibleState.Collapsed,
            pillar
          )
      );
    }

    if (element.pillar) {
      // Pillar level - show checks
      return element.pillar.checks.map(
        (check) =>
          new ReadinessTreeItem(
            check.name,
            vscode.TreeItemCollapsibleState.None,
            undefined,
            check
          )
      );
    }

    return [];
  }
}

/**
 * Provides tree data for the failed checks view
 */
export class FailedChecksTreeProvider implements vscode.TreeDataProvider<ReadinessTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<ReadinessTreeItem | undefined | null | void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private scanResult: ScanResult | null = null;

  /**
   * Update with new scan results
   */
  update(result: ScanResult): void {
    this.scanResult = result;
    this._onDidChangeTreeData.fire();
  }

  /**
   * Clear the tree
   */
  clear(): void {
    this.scanResult = null;
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: ReadinessTreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: ReadinessTreeItem): ReadinessTreeItem[] {
    if (!this.scanResult || element) {
      return [];
    }

    // Collect all failed checks across pillars
    const failedChecks: { pillar: string; check: CheckResult }[] = [];

    for (const pillar of this.scanResult.pillars) {
      for (const check of pillar.checks) {
        if (!check.passed) {
          failedChecks.push({ pillar: pillar.name, check });
        }
      }
    }

    // Sort by level (most important first)
    failedChecks.sort((a, b) => a.check.level - b.check.level);

    return failedChecks.map(({ pillar, check }) => {
      const item = new ReadinessTreeItem(
        check.name,
        vscode.TreeItemCollapsibleState.None,
        undefined,
        check
      );
      item.description = `${pillar} • L${check.level}`;
      return item;
    });
  }
}
