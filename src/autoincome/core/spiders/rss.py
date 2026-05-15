"""RSS spider - fetches opportunities from RSS feeds."""

from __future__ import annotations

from typing import Any, Dict, List

import httpx

from autoincome.core.spiders.base import BaseSpider


class RSSSpider(BaseSpider):
    """Fetch opportunities from configured RSS feeds."""

    name = "rss"
    base_url = ""

    # Pre-configured RSS feeds related to side hustles
    DEFAULT_FEEDS = [
        "https://www.v2ex.com/feed/tab/create.xml",
        "https://www.v2ex.com/feed/tab/jobs.xml",
    ]

    async def fetch(self, limit: int = 20, **kwargs: Any) -> List[Dict[str, Any]]:
        """Fetch RSS feeds and parse entries."""
        feeds = kwargs.get("feeds", self.DEFAULT_FEEDS)
        opportunities: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for feed_url in feeds:
                try:
                    items = await self._fetch_feed(client, feed_url, limit)
                    opportunities.extend(items)
                except Exception:
                    continue

        return opportunities

    async def _fetch_feed(
        self, client: httpx.AsyncClient, feed_url: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch and parse a single RSS feed."""
        response = await client.get(feed_url)
        response.raise_for_status()
        content = response.text

        # Simple XML parsing for RSS items
        import re

        opportunities = []

        # Extract items using regex (lightweight, no XML dependency)
        items = re.findall(
            r'<item>.*?</item>',
            content,
            re.DOTALL,
        )[:limit]

        for item_xml in items:
            title = self._extract_tag(item_xml, "title")
            description = self._extract_tag(item_xml, "description")
            link = self._extract_tag(item_xml, "link")
            pub_date = self._extract_tag(item_xml, "pubDate")

            if not title:
                continue

            # Strip HTML from description
            desc_text = re.sub(r'<[^>]+>', '', description or title)

            opp = {
                "title": title[:256],
                "description": desc_text[:4096],
                "source": f"RSS/{self._get_feed_name(feed_url)}",
                "source_url": link,
                "verified": False,
                "warning": "信息来自 RSS 订阅，请自行验证",
                "tags": ["RSS"],
                "required_skills": [],
                "investment": 0,
                "age_days": 0,
                "platform_risk": False,
                "monthly_income": 0,
                "hours_per_day": 2.0,
                "success_cases": 0,
                "has_tutorial": False,
                "has_video_tutorial": False,
                "feedback": [],
            }
            opportunities.append(opp)

        return opportunities

    def _extract_tag(self, xml: str, tag: str) -> str:
        """Extract content between XML tags."""
        import re
        match = re.search(
            rf'<{tag}[^>]*>(.*?)</{tag}>',
            xml,
            re.DOTALL,
        )
        if match:
            return match.group(1).strip()
        return ""

    def _get_feed_name(self, url: str) -> str:
        """Extract a readable name from feed URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain.split(".")[0]

    async def health_check(self) -> bool:
        """Check RSS feed accessibility."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for feed in self.DEFAULT_FEEDS[:1]:
                    response = await client.get(feed)
                    if response.status_code == 200:
                        return True
                return False
        except Exception:
            return False
