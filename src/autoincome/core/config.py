"""Pydantic Settings v4 — production-grade configuration.

Changes from v3:
- PostgreSQL URL instead of SQLite path
- Redis URL for cache and task queue
- Celery broker/result backend URLs
- Structured logging configuration
- Multi-environment database support
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from autoincome.core.security import validate_secret_key_entropy


# Default scoring weights (centralized)
DEFAULT_SCORING_WEIGHTS: dict[str, float] = {
    "feasibility": 0.30,
    "timeliness": 0.25,
    "credibility": 0.20,
    "roi": 0.15,
    "replicability": 0.10,
}


class Settings(BaseSettings):
    """Application settings with strict validation."""

    model_config = SettingsConfigDict(
        env_prefix="AUTOINCOME_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Core ──────────────────────────────────────────────────────
    env: Literal["development", "staging", "production", "testing"] = "development"
    debug: bool = Field(default=False, description="Enable debug mode")
    secret_key: str = Field(description="Cryptographically secure random key")

    # ── Server ────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = Field(default=8080, ge=1, le=65535)
    workers: int = Field(default=1, ge=1, le=32)

    # ── Database (PostgreSQL) ─────────────────────────────────────
    db_url: str = Field(
        default="postgresql+asyncpg://autoincome:changeme@localhost:5432/autoincome",
        description="PostgreSQL connection URL",
    )
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=20, ge=0, le=100)

    # ── Cache (Redis) ─────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_pool_size: int = Field(default=50, ge=1, le=500)

    # ── Task Queue (Celery + Redis) ───────────────────────────────
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL",
    )

    # ── Security ──────────────────────────────────────────────────
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8080"])
    rate_limit: str = Field(default="100/minute")
    max_request_size: int = Field(default=1_048_576, ge=1024, le=100_485_760)
    jwt_expiry_minutes: int = Field(default=60, ge=5, le=10080)
    password_min_length: int = Field(default=12, ge=8, le=128)
    max_concurrent_requests: int = Field(default=100, ge=10, le=10000)
    trusted_hosts: list[str] = Field(default_factory=lambda: ["*"])

    # ── Features ──────────────────────────────────────────────────
    enable_registration: bool = True
    enable_notifications: bool = False
    scan_interval_minutes: int = Field(default=240, ge=15, le=10080)
    min_score_threshold: float = Field(default=7.0, ge=0.0, le=10.0)
    high_score_threshold: float = Field(default=8.5, ge=0.0, le=10.0)

    # ── Logging ───────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "json"

    # ── Admin ─────────────────────────────────────────────────────
    admin_email: str | None = None
    admin_password_hash: str | None = None

    # ── Notifications ─────────────────────────────────────────────
    pushover_token: str | None = None
    pushover_user: str | None = None
    webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_tls: bool = True
    smtp_from: str | None = None

    # ── Spider Configuration ──────────────────────────────────────
    spider_request_timeout: int = Field(default=30, ge=5, le=300)
    spider_max_retries: int = Field(default=3, ge=0, le=10)
    spider_retry_delay: float = Field(default=1.0, ge=0.1, le=60.0)
    spider_user_agent: str = (
        "AutoIncome-Bot/4.0 (https://github.com/dfhhvc/auto92811)"
    )
    spider_rate_limit_per_second: float = Field(default=1.0, ge=0.1, le=10.0)

    # ── Validation ────────────────────────────────────────────────
    @field_validator("secret_key")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        validate_secret_key_entropy(v, min_bits=3.5)
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("trusted_hosts", mode="before")
    @classmethod
    def _parse_hosts(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    @field_validator("db_url")
    @classmethod
    def _validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError("Only postgresql+asyncpg or sqlite+aiosqlite URLs are supported")
        return v

    # Security: hide sensitive fields in repr
    def __repr__(self) -> str:
        return (
            f"Settings(env={self.env}, debug={self.debug}, "
            f"host={self.host}, port={self.port})"
        )

    # ── Methods ───────────────────────────────────────────────────
    def get_scoring_weights(self) -> dict[str, float]:
        """Return scoring weights (may be loaded from DB in future)."""
        return DEFAULT_SCORING_WEIGHTS.copy()

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == "production"

    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.env == "testing"


# Global singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the global settings instance (lazy-loaded)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
