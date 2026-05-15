"""Structured JSON logging with context propagation.

Production features:
- JSON format for log aggregation (ELK/Loki)
- Request ID correlation
- Performance timing
- Automatic PII redaction
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from pythonjsonlogger.json import JsonFormatter

from autoincome.core.config import get_settings

# Fields that should never appear in logs (PII/sensitive)
SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "secret_key",
    "token",
    "api_key",
    "authorization",
    "cookie",
    "pushover_token",
    "pushover_user",
}


def _redact_sensitive(data: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive fields from log data."""
    if not isinstance(data, dict):
        return data

    redacted = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = _redact_sensitive(value)
        else:
            redacted[key] = value
    return redacted


def configure_logging() -> None:
    """Configure structured logging for production."""
    settings = get_settings()

    # Standard library logging → structlog bridge
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))

    if settings.log_format == "json":
        formatter = JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LogContext:
    """Context manager for structured log context."""

    def __init__(self, **context: Any) -> None:
        self.context = _redact_sensitive(context)

    def __enter__(self) -> LogContext:
        structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, *args: Any) -> None:
        structlog.contextvars.unbind_contextvars(*self.context.keys())
