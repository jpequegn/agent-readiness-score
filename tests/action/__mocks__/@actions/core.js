module.exports = {
  getInput: jest.fn((name) => {
    const inputs = {
      'path': '.',
      'min-level': '3',
      'fail-below': 'true',
      'comment-on-pr': 'true',
      'format': 'markdown',
      'fail-on-error': 'false',
    };
    return inputs[name] || '';
  }),
  setOutput: jest.fn(),
  setFailed: jest.fn(),
  info: jest.fn(),
  error: jest.fn(),
  warning: jest.fn(),
  debug: jest.fn(),
  getBooleanInput: jest.fn((name) => {
    return module.exports.getInput(name).toLowerCase() === 'true';
  }),
};
