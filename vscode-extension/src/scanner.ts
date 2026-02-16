/**
 * Scanner module - runs the agent-readiness CLI and parses results
 */

import { spawn } from 'child_process';
import * as vscode from 'vscode';
import { ScanResult } from './types';

export class Scanner {
  private outputChannel: vscode.OutputChannel;

  constructor() {
    this.outputChannel = vscode.window.createOutputChannel('Agent Readiness');
  }

  /**
   * Run the agent-readiness scan on a directory
   */
  async scan(targetDir: string): Promise<ScanResult> {
    const config = vscode.workspace.getConfiguration('agentReadiness');
    const cliPath = config.get<string>('cliPath', 'agent-readiness');

    return new Promise((resolve, reject) => {
      this.outputChannel.appendLine(`Running: ${cliPath} ${targetDir} --format json`);

      const proc = spawn(cliPath, [targetDir, '--format', 'json'], {
        cwd: targetDir,
        shell: true,
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data: Buffer) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
        this.outputChannel.appendLine(`stderr: ${data.toString()}`);
      });

      proc.on('error', (error: Error) => {
        this.outputChannel.appendLine(`Error: ${error.message}`);
        reject(new Error(`Failed to run agent-readiness: ${error.message}`));
      });

      proc.on('close', (code: number | null) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout) as ScanResult;
            this.outputChannel.appendLine(`Scan complete: ${result.overall_score.toFixed(1)}%`);
            resolve(result);
          } catch (parseError) {
            this.outputChannel.appendLine(`Parse error: ${parseError}`);
            this.outputChannel.appendLine(`Raw output: ${stdout}`);
            reject(new Error(`Failed to parse scan results: ${parseError}`));
          }
        } else {
          this.outputChannel.appendLine(`Exit code: ${code}`);
          reject(new Error(`Scan failed with exit code ${code}: ${stderr}`));
        }
      });
    });
  }

  /**
   * Check if the CLI is available
   */
  async checkCliAvailable(): Promise<boolean> {
    const config = vscode.workspace.getConfiguration('agentReadiness');
    const cliPath = config.get<string>('cliPath', 'agent-readiness');

    return new Promise((resolve) => {
      const proc = spawn(cliPath, ['--version'], { shell: true });

      proc.on('error', () => resolve(false));
      proc.on('close', (code) => resolve(code === 0));
    });
  }

  /**
   * Show the output channel
   */
  showOutput(): void {
    this.outputChannel.show();
  }

  dispose(): void {
    this.outputChannel.dispose();
  }
}
