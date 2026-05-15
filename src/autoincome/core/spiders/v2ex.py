"""V2EX spider - fetches real data from V2EX API.

V2EX has a public API: https://www.v2ex.com/api/
Nodes of interest: "share", "jobs", "create"
"""

from __future__ import annotations

from typing import Any, Dict, List

import httpx

from autoincome.core.spiders.base import BaseSpider


class V2EXSpider(BaseSpider):
    """Fetch opportunities from V2EX "分享创造" and "酷工作" nodes."""

    name = "v2ex"
    base_url = "https://www.v2ex.com/api"

    # V2EX nodes that contain side hustle / indie hacker content
    TARGET_NODES = ["share", "create"]

    async def fetch(self, limit: int = 20, **kwargs: Any) -> List[Dict[str, Any]]:
        """Fetch latest topics from target V2EX nodes.

        Args:
            limit: Maximum topics per node.

        Returns:
            List of opportunity dicts.
        """
        opportunities: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for node_name in self.TARGET_NODES:
                try:
                    node_topics = await self._fetch_node(client, node_name, limit)
                    opportunities.extend(node_topics)
                except Exception:
                    # White-hat: fail gracefully, don't crash the whole scan
                    continue

        return opportunities

    async def _fetch_node(
        self, client: httpx.AsyncClient, node_name: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch topics from a specific V2EX node."""
        url = f"{self.base_url}/topics/latest.json"

        response = await client.get(url)
        response.raise_for_status()
        topics = response.json()

        opportunities = []
        for topic in topics[:limit]:
            # Filter for topics that look like side hustles / projects
            title = topic.get("title", "")
            content = topic.get("content", "")

            # Skip if no meaningful content
            if not title or len(title) < 5:
                continue

            opp = {
                "title": title[:256],
                "description": (content or title)[:4096],
                "source": f"V2EX/{node_name}",
                "source_url": topic.get("url", ""),
                "verified": False,
                "warning": "信息来自社区分享，请自行验证",
                "tags": ["社区", "分享"],
                "required_skills": [],
                "investment": 0,
                "age_days": 0,  # Could calculate from created time
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
        """Check V2EX API accessibility."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/nodes/show.json?name=share")
                return response.status_code == 200
        except Exception:
            return False
