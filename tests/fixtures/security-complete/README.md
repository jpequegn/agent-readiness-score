# Security Complete Project

## Installation

```bash
npm install
```

## Security

This project implements comprehensive security practices:

- JWT-based authentication
- Password hashing with bcrypt
- Environment variable management
- Helmet for security headers
- npm audit for vulnerability scanning
- ESLint for code quality

### Dependencies

Dependencies are locked in package-lock.json. Update with:

```bash
npm audit
npm update
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Testing

```bash
npm test
```
