"""Base spider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseSpider(ABC):
    """Abstract base class for all platform spiders."""

    name: str = ""
    base_url: str = ""

    @abstractmethod
    async def fetch(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Fetch opportunities from the platform.

        Returns:
            List of opportunity dictionaries.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the platform is accessible.

        Returns:
            True if the platform is reachable.
        """
        pass
