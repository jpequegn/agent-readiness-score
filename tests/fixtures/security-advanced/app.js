const express = require('express');
const helmet = require('helmet');
const { body, validationResult } = require('express-validator');

const app = express();
app.use(helmet());
app.use(express.json());

app.post('/auth', [
  body('username').trim().isLength({ min: 3 }),
  body('password').isLength({ min: 8 })
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  // JWT token generation
  const token = generateToken(req.body.username);
  res.json({ token });
});

function generateToken(username) {
  // TODO: Generate JWT with expiration
  return 'jwt_token';
}

module.exports = app;
