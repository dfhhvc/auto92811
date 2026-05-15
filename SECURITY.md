# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Security Features

AutoIncome implements the following security measures:

- **OWASP Top 10** compliance
- **Input validation** via Pydantic models
- **SQL injection prevention** via parameterized queries (SQLAlchemy)
- **XSS prevention** via input sanitization and output encoding
- **CSRF protection** via SameSite cookies and CORS allowlist
- **Rate limiting** via slowapi
- **Secure password hashing** via bcrypt (12 rounds)
- **JWT tokens** with HS256 and expiration
- **Security headers** (HSTS, CSP, X-Frame-Options)
- **No hardcoded secrets** - all via environment variables

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email security@autoincome.dev with details
3. Allow 90 days for remediation before public disclosure

## Secure Deployment Checklist

- [ ] Use strong `AUTOINCOME_SECRET_KEY` (≥32 chars, random)
- [ ] Run behind HTTPS with TLS 1.3
- [ ] Set `AUTOINCOME_ENV=production`
- [ ] Disable debug mode
- [ ] Configure CORS with explicit origins
- [ ] Enable rate limiting
- [ ] Use Docker with read-only rootfs and non-root user
- [ ] Keep dependencies updated (`pip install --upgrade`)
- [ ] Enable audit logging
