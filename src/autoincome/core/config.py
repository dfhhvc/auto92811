"""Pydantic Settings-based configuration with security validation.

All sensitive values are loaded exclusively from environment variables.
No hardcoded secrets. No plaintext credentials in files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from autoincome.core.security import validate_secret_key_entropy


# Default scoring weights (centralized, never hardcoded in business logic)
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
    env: Literal["development", "staging", "production"] = "development"
    debug: bool = Field(default=False, description="Enable debug mode (never in production)")
    secret_key: str = Field(description="Cryptographically secure random key for JWT/signing")
    
    # ── Server ────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = Field(default=8080, ge=1, le=65535)
    workers: int = Field(default=1, ge=1, le=32)
    
    # ── Database ──────────────────────────────────────────────────
    db_path: Path = Field(default=Path("./data/autoincome.db"))
    db_pool_size: int = Field(default=5, ge=1, le=100)
    
    # ── Security ──────────────────────────────────────────────────
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8080"])
    rate_limit: str = Field(default="100/minute", description="API rate limit string")
    max_request_size: int = Field(default=1_048_576, ge=1024, le=100_485_760)
    jwt_expiry_minutes: int = Field(default=60, ge=5, le=10080)
    password_min_length: int = Field(default=12, ge=8, le=128)
    max_concurrent_requests: int = Field(default=100, ge=10, le=10000)
    
    # ── Features ──────────────────────────────────────────────────
    enable_registration: bool = True
    enable_notifications: bool = False
    scan_interval_minutes: int = Field(default=240, ge=15, le=10080)
    min_score_threshold: float = Field(default=7.0, ge=0.0, le=10.0)
    high_score_threshold: float = Field(default=8.5, ge=0.0, le=10.0)
    
    # ── Logging ───────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: str = "json"
    
    # ── Admin ─────────────────────────────────────────────────────
    admin_email: str | None = None
    admin_password_hash: str | None = None
    
    # ── Notifications (optional) ──────────────────────────────────
    pushover_token: str | None = None
    pushover_user: str | None = None
    webhook_url: str | None = None
    
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
    
    @field_validator("db_path")
    @classmethod
    def _validate_db_path(cls, v: Path) -> Path:
        if not v.name or v.name in (".", ".."):
            raise ValueError("Invalid database path")
        return v
    
    # Security: hide sensitive fields in repr
    def __repr__(self) -> str:
        return (
            f"Settings(env={self.env}, debug={self.debug}, "
            f"host={self.host}, port={self.port})"
        )
    
    # ── Methods ───────────────────────────────────────────────────
    def get_scoring_weights(self) -> dict[str, float]:
        """Return the default scoring weights.
        
        In future versions, this may read from config file or database.
        """
        return DEFAULT_SCORING_WEIGHTS.copy()


# Global singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
