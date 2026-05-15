# Changelog

All notable changes to this project will be documented in this file.

## [4.0.0] - 2026-05-16

### 🔒 Security
- Fixed default `trusted_hosts` from `["*"]` to `["localhost", "127.0.0.1"]`
- Added structured logging with PII redaction to all spider modules

### 🕷️ Spider Fixes
- **V2EX**: Fixed node parameter not being passed to API (`/topics/show.json?node_name={name}`)
- **Jike**: Marked as retired — `api.ruguoapp.com` is no longer available
- **All spiders**: Replaced bare `except Exception: pass` with specific `httpx` exceptions + logging
- **All spiders**: Moved `import re` from function bodies to module top level

### 🧠 Scoring Honesty
- Updated docstrings to clarify that scoring is **rules-based**, not AI/ML
- Added explicit note: "Future versions may incorporate ML models if validated training data becomes available"

### 🏗️ Architecture
- Added SQLite (`sqlite+aiosqlite://`) as supported database URL for development

## [3.0.0] - 2026-05-15

### 🚀 Major Rewrite

**Security First**
- Full OWASP Top 10 compliance
- bcrypt password hashing (12 rounds)
- JWT authentication with expiration
- Rate limiting via slowapi
- Input sanitization (XSS/SQL injection prevention)
- Security headers (HSTS, CSP, X-Frame-Options)
- No hardcoded secrets (100% env vars)
- Docker security (non-root, read-only rootfs, cap_drop)

**Architecture**
- Migrated from CLI-only to FastAPI web application
- Async SQLite with SQLAlchemy 2.0
- Pydantic Settings for configuration
- Modular router structure
- RESTful API with auto-generated docs

**Cross-Platform**
- Docker support (single-command deployment)
- Docker Compose with persistent volumes
- Responsive web UI (mobile-first)
- pip installable package
- Windows / macOS / Linux / iOS / Android support

**Developer Experience**
- GitHub Actions CI/CD
- pytest with coverage enforcement
- ruff linting and formatting
- mypy strict type checking
- bandit security scanning
- pre-commit hooks

### Added
- Web UI at `/` (responsive, dark mode)
- API documentation (Swagger + ReDoc)
- User registration/login with JWT
- Async database with migration-ready structure
- Health check endpoint
- Public configuration endpoint

### Changed
- Replaced MD5 with SHA-256 for fingerprints
- Replaced dict configs with Pydantic Settings
- Replaced plain text logs with structured logging prep

### Removed
- Hardcoded sample data (now generated dynamically)
- Plain CLI mode (replaced by web + API)
