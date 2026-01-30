module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/action/**/*.test.js'],
  collectCoverageFrom: [
    'action/index.js',
    '!action/jest.config.js',
  ],
  coveragePathIgnorePatterns: ['/node_modules/'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
