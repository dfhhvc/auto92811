"""Public configuration endpoint (no secrets)."""

from __future__ import annotations

from fastapi import APIRouter

from autoincome.core.config import get_settings

router = APIRouter(prefix="/config", tags=["Config"])


@router.get("")
async def get_public_config():
    """Return safe, non-sensitive configuration."""
    s = get_settings()
    return {
        "version": "3.0.0",
        "env": s.env,
        "features": {
            "registration": s.enable_registration,
            "notifications": s.enable_notifications,
        },
        "scoring": {
            "min_score": s.min_score_threshold,
            "high_score": s.high_score_threshold,
            "weights": s.get_scoring_weights(),
        },
        "limits": {
            "rate_limit": s.rate_limit,
            "max_request_size": s.max_request_size,
        },
    }
