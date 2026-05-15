"""Jike spider — API endpoint retired.

The official api.ruguoapp.com endpoint has been shut down.
This spider is kept as a placeholder with a clear failure mode
so the scheduler can skip it gracefully.

If Jike re-opens a public API in the future, re-implement here.
"""

from __future__ import annotations

import logging
from typing import Any

from autoincome.core.spiders.base import BaseSpider

logger = logging.getLogger(__name__)


class JikeSpider(BaseSpider):
    """Placeholder — Jike public API is no longer available."""

    name = "jike"
    base_url = ""

    async def fetch(self, limit: int = 20, **kwargs: Any) -> list[dict[str, Any]]:
        """No-op fetch — API retired."""
        logger.warning(
            "jike_api_retired",
            message="Jike public API (api.ruguoapp.com) is no longer available. "
            "Skipping fetch.",
        )
        return []

    async def health_check(self) -> bool:
        """Always returns False — API retired."""
        return False
