"""FastAPI application v4 — production-grade.

Upgrades from v3:
- PostgreSQL + connection pooling
- Redis cache layer
- Celery task queue integration
- Prometheus metrics endpoint
- Structured JSON logging
- Lifecycle management (startup/shutdown)
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import SQLAlchemyError
from starlette_prometheus import PrometheusMiddleware, metrics

from autoincome import __version__
from autoincome.api.routers import (
    admin,
    auth,
    community,
    config as config_router,
    health,
    income,
    opportunities,
    scan,
)
from autoincome.core.cache import cache
from autoincome.core.config import get_settings
from autoincome.core.database import close_db, init_db
from autoincome.core.logging_config import configure_logging, get_logger
from autoincome.core.metrics import measure_http_request
from autoincome.core.rate_limit import limiter
from autoincome.core.security import generate_secure_token

_settings = get_settings()
_start_time = time.time()

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    logger.info("app_startup", version=__version__, env=_settings.env)

    await init_db()
    await cache.connect()

    logger.info("app_ready", uptime=time.time() - _start_time)

    yield

    # Shutdown
    logger.info("app_shutdown")
    await cache.close()
    await close_db()


app = FastAPI(
    title="AutoIncome API",
    description="AI-powered passive income opportunity aggregator — v4",
    version=__version__,
    docs_url="/api/docs" if _settings.debug else None,
    redoc_url="/api/redoc" if _settings.debug else None,
    openapi_url="/api/openapi.json" if _settings.debug else None,
    lifespan=lifespan,
)

app.state.limiter = limiter

# ── Middleware ────────────────────────────────────────────────────

# Prometheus metrics middleware (must be early)
app.add_middleware(PrometheusMiddleware)

@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down."},
        headers={"Retry-After": "60"},
    )


@app.exception_handler(RequestValidationError)
async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors with structured response."""
    errors = []
    for err in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in err.get("loc", [])),
            "message": err.get("msg", ""),
            "type": err.get("type", ""),
        })
    logger.warning("validation_error", path=request.url.path, errors=errors)
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.exception_handler(SQLAlchemyError)
async def _db_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors without leaking internal details."""
    logger.error("database_error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed. Please try again later."},
    )


@app.exception_handler(Exception)
async def _global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler: log full stack trace, return safe generic response."""
    logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
    detail = "Internal server error"
    if _settings.debug:
        detail = f"Internal server error: {exc}"
    return JSONResponse(
        status_code=500,
        content={"detail": detail},
    )

# CORS
_cors_origins = list(_settings.cors_origins)
if "*" in _cors_origins:
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

# Trusted Host (skip in testing to allow testserver)
if not _settings.is_testing():
    _trusted = list(_settings.trusted_hosts)
    if _settings.is_production() and "*" in _trusted:
        _trusted = ["localhost", "127.0.0.1"]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=_trusted,
    )

# Request ID + Timing + Security Headers
@app.middleware("http")
async def _request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or generate_secure_token(16)
    request.state.request_id = request_id

    method = request.method
    endpoint = request.url.path

    with measure_http_request(method, endpoint):
        response = await call_next(request)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

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

    if _settings.is_production():
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    return response


# Body size limit
@app.middleware("http")
async def _body_size_limit(request: Request, call_next):
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


# ── Routers ───────────────────────────────────────────────────────

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(opportunities.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")
app.include_router(config_router.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")
app.include_router(income.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Prometheus metrics endpoint
app.add_route("/metrics", metrics)

# ── Web UI ────────────────────────────────────────────────────────

_WEB_UI_PATH = Path(__file__).parent.parent / "web" / "index.html"


@app.get("/", response_class=HTMLResponse)
async def _root():
    if _WEB_UI_PATH.exists():
        with _WEB_UI_PATH.open("r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>AutoIncome API v4</h1><p>Visit /api/docs for documentation.</p>")


@app.get("/app")
async def _app_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")


@app.get("/api/v1/version")
async def _version():
    return {
        "version": __version__,
        "env": _settings.env,
        "uptime": round(time.time() - _start_time, 2),
    }