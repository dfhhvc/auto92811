"""Spider registry for dynamic loading.

Usage:
    from autoincome.core.spiders import registry
    spider_class = registry.get("v2ex")
    spider = spider_class()
    results = await spider.fetch()
"""

from __future__ import annotations

from typing import Type

from autoincome.core.spiders.base import BaseSpider
from autoincome.core.spiders.v2ex import V2EXSpider
from autoincome.core.spiders.zhihu import ZhihuSpider
from autoincome.core.spiders.github import GitHubSpider
from autoincome.core.spiders.jike import JikeSpider
from autoincome.core.spiders.rss import RSSSpider


class SpiderRegistry:
    """Registry for spider classes."""

    def __init__(self) -> None:
        self._spiders: dict[str, Type[BaseSpider]] = {}

    def register(self, name: str, spider_class: Type[BaseSpider]) -> None:
        """Register a spider class."""
        self._spiders[name] = spider_class

    def get(self, name: str) -> Type[BaseSpider] | None:
        """Get spider class by name."""
        return self._spiders.get(name)

    def list_spiders(self) -> list[str]:
        """List all registered spider names."""
        return list(self._spiders.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._spiders


# Global registry
registry = SpiderRegistry()

# Register built-in spiders
registry.register("v2ex", V2EXSpider)
registry.register("zhihu", ZhihuSpider)
registry.register("github", GitHubSpider)
registry.register("jike", JikeSpider)
registry.register("rss", RSSSpider)

# Backwards-compatible registry dict
ALL_SPIDERS = {
    "v2ex": V2EXSpider,
    "zhihu": ZhihuSpider,
    "github": GitHubSpider,
    "jike": JikeSpider,
    "rss": RSSSpider,
}

__all__ = ["registry", "BaseSpider", "ALL_SPIDERS"]