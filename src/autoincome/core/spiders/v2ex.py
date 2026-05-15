"""V2EX spider - fetches real data from V2EX API.

V2EX public API: https://www.v2ex.com/api/
Nodes of interest: "create" (分享创造), "jobs" (酷工作)
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from autoincome.core.spiders.base import BaseSpider

logger = logging.getLogger(__name__)


class V2EXSpider(BaseSpider):
    """Fetch opportunities from V2EX target nodes."""

    name = "v2ex"
    base_url = "https://www.v2ex.com/api"

    # Nodes containing side-hustle / indie-hacker content
    TARGET_NODES = ["create", "share"]

    async def fetch(self, limit: int = 20, **kwargs: Any) -> list[dict[str, Any]]:
        """Fetch latest topics from target V2EX nodes.

        Args:
            limit: Maximum topics per node.

        Returns:
            List of opportunity dicts.
        """
        opportunities: list[dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for node_name in self.TARGET_NODES:
                try:
                    node_topics = await self._fetch_node(client, node_name, limit)
                    opportunities.extend(node_topics)
                except httpx.HTTPStatusError as exc:
                    logger.warning(
                        "v2ex_node_http_error",
                        node=node_name,
                        status=exc.response.status_code,
                    )
                except httpx.RequestError as exc:
                    logger.warning(
                        "v2ex_node_request_error",
                        node=node_name,
                        error=str(exc),
                    )
                except Exception:
                    logger.exception("v2ex_node_unexpected_error", node=node_name)

        return opportunities

    async def _fetch_node(
        self,
        client: httpx.AsyncClient,
        node_name: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Fetch topics from a specific V2EX node."""
        url = f"{self.base_url}/topics/show.json"
        params = {"node_name": node_name}

        response = await client.get(url, params=params)
        response.raise_for_status()
        topics = response.json()

        opportunities = []
        for topic in topics[:limit]:
            title = topic.get("title", "")
            content = topic.get("content", "")

            if not title or len(title) < 5:
                continue

            node_info = topic.get("node", {})
            actual_node = node_info.get("name", node_name)

            opp = {
                "title": title[:256],
                "description": (content or title)[:4096],
                "source": f"V2EX/{actual_node}",
                "source_url": topic.get("url", ""),
                "verified": False,
                "warning": "信息来自社区分享，请自行验证",
                "tags": ["社区", "分享"],
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

        logger.info(
            "v2ex_node_fetched",
            node=node_name,
            count=len(opportunities),
        )
        return opportunities

    async def health_check(self) -> bool:
        """Check V2EX API accessibility."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/nodes/show.json",
                    params={"name": "create"},
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False
        except Exception:
            logger.exception("v2ex_health_check_failed")
            return False
