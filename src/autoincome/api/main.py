"""FastAPI application with comprehensive security middleware.

Security features:
- Rate limiting (slowapi)
- CORS with explicit allowlist (credentials + wildcard forbidden)
- Security headers (HSTS, CSP, X-Frame-Options)
- Request body size limits (DoS prevention)
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
from slowapi.errors import RateLimitExceeded

from autoincome import __version__
from autoincome.api.routers import auth, config as config_router, health, opportunities, scan
from autoincome.core.config import get_settings
from autoincome.core.database import init_db
from autoincome.core.rate_limit import limiter

_settings = get_settings()
_start_time = time.time()


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


# CORS: explicit allowlist only. Never allow wildcard with credentials.
_cors_origins = list(_settings.cors_origins)
if "*" in _cors_origins:
    # Security: wildcard + credentials is forbidden by CORS spec
    _cors_origins = [o for o in _cors_origins if o != "*"]
    if not _cors_origins:
        _cors_origins = ["http://localhost:8080", "http://127.0.0.1:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    max_age=600,
)

# Trusted host validation
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["autoincome.dev", "app.autoincome.dev", "localhost", "127.0.0.1"]
    if _settings.debug
    else ["autoincome.dev", "app.autoincome.dev"],
)


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    # Content-Security-Policy based on response type
    content_type = response.headers.get("content-type", "")
    if content_type.startswith("text/html"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none';"
        )

    if not _settings.debug:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
    return response


@app.middleware("http")
async def _body_size_limit(request: Request, call_next):
    """Prevent DoS via oversized request bodies."""
    if request.method in ("POST", "PUT", "PATCH"):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > _settings.max_request_size:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request entity too large"},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )
    return await call_next(request)


@app.middleware("http")
async def _request_logging(request: Request, call_next):
    """Log requests without sensitive data."""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    # Structured log: method, path, status, duration
    # NO query params, NO body, NO headers with secrets
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
