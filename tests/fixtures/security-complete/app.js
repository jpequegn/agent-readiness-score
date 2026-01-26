const express = require('express');
const helmet = require('helmet');
const app = express();

app.use(helmet());

app.post('/auth', (req, res) => {
  // Validate input
  if (!req.body.username || !req.body.password) {
    return res.status(400).json({ error: 'Missing credentials' });
  }

  // TODO: Authenticate user
  res.json({ token: 'jwt_token' });
});

module.exports = app;
