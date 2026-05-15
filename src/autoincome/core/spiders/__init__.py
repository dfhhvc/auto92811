"""Platform spiders for fetching real opportunity data."""

from autoincome.core.spiders.base import BaseSpider
from autoincome.core.spiders.github import GitHubSpider
from autoincome.core.spiders.jike import JikeSpider
from autoincome.core.spiders.rss import RSSSpider
from autoincome.core.spiders.v2ex import V2EXSpider
from autoincome.core.spiders.zhihu import ZhihuSpider

__all__ = [
    "BaseSpider",
    "GitHubSpider",
    "JikeSpider",
    "RSSSpider",
    "V2EXSpider",
    "ZhihuSpider",
]

# Registry of all available spiders
ALL_SPIDERS = {
    "v2ex": V2EXSpider,
    "zhihu": ZhihuSpider,
    "github": GitHubSpider,
    "jike": JikeSpider,
    "rss": RSSSpider,
}
