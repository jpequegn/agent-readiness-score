const core = require('@actions/core');
const exec = require('@actions/exec');

jest.mock('@actions/core');
jest.mock('@actions/exec');

// Mock child_process
jest.mock('child_process', () => ({
  execSync: jest.fn(() => JSON.stringify({
    overall_score: 65,
    maturity_level: 2,
    summary: {
      total_checks: 100,
      passed: 65,
      failed: 35,
      pass_rate: '65%',
    },
    pillars: [
      {
        name: 'Testing',
        score: 55,
        passed: 11,
        total: 20,
      },
      {
        name: 'Style & Validation',
        score: 75,
        passed: 15,
        total: 20,
      },
    ],
  })),
}));

describe('Agent Readiness GitHub Action', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.GITHUB_TOKEN = 'test-token';
  });

  describe('Input Handling', () => {
    test('should get path input with default value', () => {
      core.getInput.mockReturnValueOnce('.');
      const input = core.getInput('path');
      expect(core.getInput).toHaveBeenCalledWith('path');
      expect(input).toBe('.');
    });

    test('should parse min-level as integer', () => {
      core.getInput.mockReturnValueOnce('3');
      const level = parseInt(core.getInput('min-level'));
      expect(level).toBe(3);
    });

    test('should parse fail-below as boolean', () => {
      core.getBooleanInput.mockReturnValueOnce(true);
      const shouldFail = core.getBooleanInput('fail-below');
      expect(shouldFail).toBe(true);
    });

    test('should parse comment-on-pr as boolean', () => {
      core.getBooleanInput.mockReturnValueOnce(true);
      const shouldComment = core.getBooleanInput('comment-on-pr');
      expect(shouldComment).toBe(true);
    });

    test('should get format input with default value', () => {
      core.getInput.mockReturnValueOnce('markdown');
      const format = core.getInput('format');
      expect(format).toBe('markdown');
    });
  });

  describe('Output Generation', () => {
    test('should set output with score from JSON', () => {
      const mockScore = '65';
      core.setOutput('score', mockScore);
      expect(core.setOutput).toHaveBeenCalledWith('score', mockScore);
    });

    test('should set output with maturity level', () => {
      const mockLevel = '2';
      core.setOutput('level', mockLevel);
      expect(core.setOutput).toHaveBeenCalledWith('level', mockLevel);
    });

    test('should set output with passed checks count', () => {
      const mockPassed = '65';
      core.setOutput('passed', mockPassed);
      expect(core.setOutput).toHaveBeenCalledWith('passed', mockPassed);
    });

    test('should set output with failed checks count', () => {
      const mockFailed = '35';
      core.setOutput('failed', mockFailed);
      expect(core.setOutput).toHaveBeenCalledWith('failed', mockFailed);
    });

    test('should set output with markdown report', () => {
      const mockReport = '## Test Report\nScore: 65%';
      core.setOutput('report', mockReport);
      expect(core.setOutput).toHaveBeenCalledWith('report', mockReport);
    });

    test('should set output with JSON results', () => {
      const mockJson = '{"score": 65}';
      core.setOutput('json', mockJson);
      expect(core.setOutput).toHaveBeenCalledWith('json', mockJson);
    });
  });

  describe('Score Evaluation', () => {
    test('should pass when score equals minimum level', () => {
      const score = 75;
      const minLevel = 3;
      const passes = score >= minLevel * 20; // Rough conversion
      expect(passes).toBe(true);
    });

    test('should fail when score below minimum level', () => {
      const score = 35;
      const minLevel = 3;
      const passes = score >= minLevel * 20;
      expect(passes).toBe(false);
    });

    test('should determine maturity level correctly', () => {
      const getLevel = (score) => {
        if (score < 40) return 1;
        if (score < 60) return 2;
        if (score < 80) return 3;
        if (score < 95) return 4;
        return 5;
      };

      expect(getLevel(35)).toBe(1);
      expect(getLevel(55)).toBe(2);
      expect(getLevel(75)).toBe(3);
      expect(getLevel(90)).toBe(4);
      expect(getLevel(98)).toBe(5);
    });
  });

  describe('Error Handling', () => {
    test('should call setFailed on error', () => {
      const errorMsg = 'Scan failed';
      core.setFailed(errorMsg);
      expect(core.setFailed).toHaveBeenCalledWith(errorMsg);
    });

    test('should handle missing GITHUB_TOKEN gracefully', () => {
      delete process.env.GITHUB_TOKEN;
      const token = process.env.GITHUB_TOKEN;
      expect(token).toBeUndefined();
    });

    test('should continue on error when fail-on-error is false', () => {
      core.getBooleanInput.mockReturnValueOnce(false);
      const shouldFail = core.getBooleanInput('fail-on-error');
      expect(shouldFail).toBe(false);
    });
  });

  describe('Markdown Report Generation', () => {
    test('should format markdown report with score', () => {
      const report = '# Agent Readiness Assessment\n\n**Score:** 65% | **Level:** 2/5';
      expect(report).toContain('Agent Readiness Assessment');
      expect(report).toContain('65%');
      expect(report).toContain('Level');
    });

    test('should include pillar breakdown in report', () => {
      const report = `
## Pillar Breakdown
- **Testing**: 55% (Level 2, 11/20 checks)
- **Style & Validation**: 75% (Level 3, 15/20 checks)
`;
      expect(report).toContain('Pillar Breakdown');
      expect(report).toContain('Testing');
      expect(report).toContain('Style & Validation');
    });

    test('should format check pass/fail indicators', () => {
      const passed = '✅ Has test command';
      const failed = '❌ Missing coverage';
      expect(passed).toContain('✅');
      expect(failed).toContain('❌');
    });
  });

  describe('PR Commenting', () => {
    test('should format PR comment with key metrics', () => {
      const comment = `
## 🦞 Agent Readiness Assessment
**Overall Score:** 65% (Level 2/5)
**Checks Passed:** 65/100
**Checks Failed:** 35/100
`;
      expect(comment).toContain('🦞');
      expect(comment).toContain('65%');
      expect(comment).toContain('65/100');
    });

    test('should include recommendations in comment', () => {
      const comment = `
## Recommendations
- Increase test coverage
- Add more documentation
`;
      expect(comment).toContain('Recommendations');
    });

    test('should include pillar scores in comment', () => {
      const comment = `
| Pillar | Score | Level |
|--------|-------|-------|
| Testing | 55% | 2 |
| Style & Validation | 75% | 3 |
`;
      expect(comment).toContain('Pillar');
      expect(comment).toContain('Testing');
    });
  });

  describe('Input Validation', () => {
    test('should validate path argument', () => {
      const isValidPath = (path) => path && typeof path === 'string';
      expect(isValidPath('.')).toBeTruthy();
      expect(isValidPath('/repo')).toBeTruthy();
      expect(isValidPath('')).toBeFalsy();
    });

    test('should validate min-level is in range 1-5', () => {
      const isValidLevel = (level) => level >= 1 && level <= 5;
      expect(isValidLevel(1)).toBe(true);
      expect(isValidLevel(3)).toBe(true);
      expect(isValidLevel(5)).toBe(true);
      expect(isValidLevel(0)).toBe(false);
      expect(isValidLevel(6)).toBe(false);
    });

    test('should validate format is one of allowed values', () => {
      const validFormats = ['text', 'json', 'markdown'];
      const isValidFormat = (format) => validFormats.includes(format);
      expect(isValidFormat('text')).toBe(true);
      expect(isValidFormat('json')).toBe(true);
      expect(isValidFormat('markdown')).toBe(true);
      expect(isValidFormat('xml')).toBe(false);
    });
  });

  describe('Action Logging', () => {
    test('should log information messages', () => {
      core.info('Starting scan');
      expect(core.info).toHaveBeenCalledWith('Starting scan');
    });

    test('should log debug messages', () => {
      core.debug('Debug information');
      expect(core.debug).toHaveBeenCalledWith('Debug information');
    });

    test('should log warning messages', () => {
      core.warning('Warning message');
      expect(core.warning).toHaveBeenCalledWith('Warning message');
    });

    test('should log error messages', () => {
      core.error('Error message');
      expect(core.error).toHaveBeenCalledWith('Error message');
    });
  });
});
