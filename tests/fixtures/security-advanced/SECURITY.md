# Security Policy

## Overview

This project implements advanced security practices including automated dependency updates, secrets scanning, and comprehensive security testing.

## Dependency Management

All dependencies are pinned in package-lock.json. Renovate automatically creates pull requests for security updates.

```bash
npm audit
npm update
```

## Secret Management

Never commit secrets. Use `.env.example` as a template and create `.env` with real values.

### Secrets Scanning

We use TruffleHog and detect-secrets in CI to prevent accidental secret commits.

### Pre-commit Hooks

Pre-commit hooks automatically scan for secrets:

```bash
pip install pre-commit
pre-commit install
```

## Authentication & Authorization

JWT-based authentication with role-based access control.

## Encryption

- Passwords hashed with bcrypt (12 rounds)
- TLS for all connections
- Field-level encryption for sensitive data

## Testing

Security testing is automated:

```bash
npm test
npm run lint
```

## Threat Model

See ARCHITECTURE.md for system design and threat considerations.
