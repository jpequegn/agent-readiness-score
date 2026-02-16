/**
 * Types for Agent Readiness Score extension
 */

export interface CheckResult {
  name: string;
  passed: boolean;
  message: string;
  severity: 'required' | 'recommended' | 'optional' | 'info' | 'warning';
  level: number;
  metadata: Record<string, unknown>;
}

export interface PillarResult {
  name: string;
  checks: CheckResult[];
  score: number;
  weight: number;
  passed: number;
  failed: number;
  total: number;
}

export interface ScanSummary {
  total_checks: number;
  passed: number;
  failed: number;
  pass_rate: string;
}

export interface ScanResult {
  target_directory: string;
  overall_score: number;
  maturity_level: number;
  summary: ScanSummary;
  pillars: PillarResult[];
}

export function getMaturityLabel(level: number): string {
  const labels: Record<number, string> = {
    1: 'Functional',
    2: 'Documented',
    3: 'Standardized',
    4: 'Optimized',
    5: 'Autonomous',
  };
  return labels[level] || 'Unknown';
}

export function getScoreEmoji(score: number): string {
  if (score >= 80) return '🟢';
  if (score >= 60) return '🟡';
  if (score >= 40) return '🟠';
  return '🔴';
}
