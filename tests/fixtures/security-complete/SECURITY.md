# Security Policy

## Dependency Management

All dependencies are pinned in package-lock.json. To update dependencies:

```bash
npm audit
npm update
```

## Secret Management

Never commit secrets. Use `.env.example` as a template and create `.env` with real values.

All secrets should be managed through environment variables.

## Authentication

The application uses JWT tokens for authentication. Tokens are validated on each request.

## Encryption

Passwords are hashed using bcrypt with 12 rounds.
