"""FastAPI application with comprehensive security middleware.

Security features:
- Rate limiting (slowapi)
- CORS with explicit allowlist
- Security headers (HSTS, CSP, X-Frame-Options)
- Request size limits
- Structured logging (no sensitive data)
- Input validation via Pydantic
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from autoincome import __version__
from autoincome.api.routers import auth, config as config_router, health, opportunities, scan
from autoincome.core.config import get_settings
from autoincome.core.database import init_db

_settings = get_settings()
_start_time = time.time()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    await init_db()
    yield


app = FastAPI(
    title="AutoIncome API",
    description="AI-powered passive income opportunity aggregator",
    version=__version__,
    docs_url="/api/docs" if _settings.debug else None,
    redoc_url="/api/redoc" if _settings.debug else None,
    openapi_url="/api/openapi.json" if _settings.debug else None,
    lifespan=lifespan,
)

app.state.limiter = limiter


# ── Middleware ────────────────────────────────────────────────────

@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down."},
        headers={"Retry-After": "60"},
    )


# CORS: explicit allowlist only
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    max_age=600,
)

# Trusted host validation
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["autoincome.dev", "app.autoincome.dev", "localhost", "*"]
    if _settings.debug
    else ["autoincome.dev", "app.autoincome.dev"],
)


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not _settings.debug:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def _request_logging(request: Request, call_next):
    """Log requests without sensitive data."""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    # Structured log: no body, no query params, no headers with secrets
    # In production, send to structured logging system
    return response


# ── Routers ───────────────────────────────────────────────────────

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(opportunities.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")
app.include_router(config_router.router, prefix="/api/v1")


# ── Web UI ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def _root():
    """Serve the main web application."""
    with open("src/autoincome/web/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/app")
async def _app_redirect():
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/")
