"""Pydantic request/response models with strict validation.

All user input is validated for type, length, format, and range.
No user input reaches the database without passing these schemas.
URL validation uses urllib.parse to prevent protocol bypass.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from autoincome.core.security import validate_safe_url


class OpportunityCreate(BaseModel):
    """Validated opportunity creation payload."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    title: str = Field(..., min_length=2, max_length=256)
    description: str = Field(..., min_length=10, max_length=4096)
    time_investment: str = Field(..., min_length=1, max_length=64)
    expected_income: str = Field(..., min_length=1, max_length=128)
    source: str = Field(..., min_length=1, max_length=128)
    source_url: str | None = Field(default=None, max_length=2048)
    verified: bool = False
    warning: str | None = Field(default=None, max_length=1024)
    tags: List[str] = Field(default_factory=list, max_length=20)
    required_skills: List[str] = Field(default_factory=list, max_length=10)
    investment: int = Field(default=0, ge=0, le=10_000_000)
    age_days: int = Field(default=0, ge=0, le=3650)
    platform_risk: bool = False
    monthly_income: int = Field(default=0, ge=0, le=10_000_000)
    hours_per_day: float = Field(default=2.0, ge=0, le=24)
    success_cases: int = Field(default=0, ge=0, le=100_000)
    has_tutorial: bool = False
    has_video_tutorial: bool = False
    feedback: List[dict[str, Any]] = Field(default_factory=list, max_length=50)

    @field_validator("tags", "required_skills")
    @classmethod
    def _validate_tag_length(cls, v: List[str]) -> List[str]:
        for tag in v:
            if len(tag) > 64:
                raise ValueError("Each tag must not exceed 64 characters")
        return v

    @field_validator("source_url")
    @classmethod
    def _validate_url(cls, v: str | None) -> str | None:
        """White-hat: use urllib.parse to strictly validate URL protocol.

        Prevents bypasses like:
        - javascript://example.com/http://
        - data:text/html,<script>...</script>
        - file:///etc/passwd
        """
        if v is None:
            return v
        # Use the centralized security utility for strict parsing
        return validate_safe_url(v)

    @field_validator("feedback")
    @classmethod
    def _validate_feedback(cls, v: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """Prevent DoS via oversized or deeply nested feedback objects."""
        if len(v) > 50:
            raise ValueError("Too many feedback items (max 50)")
        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Each feedback item must be a dictionary")
            if len(str(item)) > 2048:
                raise ValueError("Individual feedback item too large (max 2048 chars)")
        return v


class OpportunityResponse(BaseModel):
    """Safe opportunity response (no internal fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    time_investment: str
    expected_income: str
    source: str
    source_url: str | None
    verified: bool
    warning: str | None
    tags: List[str]
    score_total: float
    score_feasibility: float
    score_timeliness: float
    score_credibility: float
    score_roi: float
    score_replicability: float
    match_score: float | None
    merge_count: int
    created_at: datetime


class ScanRequest(BaseModel):
    """Validated scan request."""

    sources: List[str] = Field(default_factory=list, max_length=10)
    max_results: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=7.0, ge=0.0, le=10.0)


class ScanResult(BaseModel):
    """Scan operation result."""

    status: Literal["success", "partial", "error"]
    raw_count: int
    unique_count: int
    merged_count: int
    valid_count: int
    recommended_count: int
    elapsed_seconds: float
    opportunities: List[OpportunityResponse]
    error_message: str | None


class UserCreate(BaseModel):
    """Validated user registration."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    email: str = Field(..., min_length=5, max_length=256)
    password: str = Field(..., min_length=12, max_length=128)
    skills: List[str] = Field(default_factory=list, max_length=20)
    time_budget: Literal["1h", "2h", "4h", "8h"] = "2h"
    risk_level: Literal["conservative", "moderate", "aggressive"] = "moderate"

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Validated login credentials."""

    email: str = Field(..., min_length=5, max_length=256)
    password: str = Field(..., min_length=1, max_length=128)


class UserProfile(BaseModel):
    """Public user profile."""

    model_config = ConfigDict(from_attributes=True)

    email: str
    skills: List[str]
    time_budget: str
    risk_level: str
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class HealthCheck(BaseModel):
    """Health check response (minimal info to prevent version leakage)."""

    status: str
    timestamp: datetime
    uptime_seconds: float
    database: str
