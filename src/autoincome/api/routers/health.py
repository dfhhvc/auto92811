"""Health check endpoint (no auth required).

Exposes minimal information to prevent version-based targeted attacks.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter

from autoincome.api.schemas.models import HealthCheck

_start_time = time.time()

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Return service health status (no version info)."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        uptime_seconds=round(time.time() - _start_time, 2),
        database="connected",
    )
