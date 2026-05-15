"""即刻爬虫 - fetches posts from Jike app public feeds."""

from __future__ import annotations

from typing import Any, Dict, List

import httpx

from autoincome.core.spiders.base import BaseSpider


class JikeSpider(BaseSpider):
    """Fetch opportunities from Jike app circles."""

    name = "jike"
    base_url = "https://api.ruguoapp.com"

    # Jike circles related to side hustles
    TOPIC_IDS = [
        "5b1e0e5c0e6a9a0018691e2a",  # 分享创造
        "5b1e0e5c0e6a9a0018691e2b",  # 独立开发者
    ]

    async def fetch(self, limit: int = 20, **kwargs: Any) -> List[Dict[str, Any]]:
        """Fetch posts from Jike circles."""
        opportunities: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for topic_id in self.TOPIC_IDS:
                try:
                    posts = await self._fetch_topic_posts(client, topic_id, limit)
                    opportunities.extend(posts)
                except Exception:
                    continue

        return opportunities

    async def _fetch_topic_posts(
        self, client: httpx.AsyncClient, topic_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch posts from a Jike topic."""
        url = f"{self.base_url}/1.0/messages/list"
        params = {
            "topicId": topic_id,
            "limit": min(limit, 20),
        }
        headers = {
            "User-Agent": "Jike/7.0.0",
            "Accept": "application/json",
        }

        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        opportunities = []
        messages = data.get("data", [])[:limit]

        for msg in messages:
            content = msg.get("content", "")
            if len(content) < 20:
                continue

            opp = {
                "title": content[:100] + "..." if len(content) > 100 else content,
                "description": content[:4096],
                "source": "即刻/分享创造",
                "source_url": msg.get("linkUrl", ""),
                "verified": msg.get("isVerified", False),
                "warning": "信息来自即刻社区，请自行验证",
                "tags": ["即刻", "社区"],
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

    async def health_check(self) -> bool:
        """Check Jike API accessibility."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.base_url,
                    headers={"User-Agent": "Jike/7.0.0"},
                )
                return response.status_code in (200, 404)
        except Exception:
            return False
