"""GitHub spider - fetches trending repos and sponsor opportunities."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from autoincome.core.spiders.base import BaseSpider

logger = logging.getLogger(__name__)


class GitHubSpider(BaseSpider):
    """Fetch GitHub Trending and sponsor-related repositories."""

    name = "github"
    base_url = "https://api.github.com"

    SEARCH_TOPICS = [
        "passive-income",
        "side-hustle",
        "indie-hacker",
        "maker",
        "open-source-sponsorship",
        "freelance",
    ]

    async def fetch(self, limit: int = 20, **kwargs: Any) -> list[dict[str, Any]]:
        """Fetch GitHub trending and search results."""
        opportunities: list[dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                trending = await self._fetch_trending(client, limit)
                opportunities.extend(trending)
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "github_trending_http_error",
                    status=exc.response.status_code,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "github_trending_request_error",
                    error=str(exc),
                )
            except Exception:
                logger.exception("github_trending_unexpected_error")

            for topic in self.SEARCH_TOPICS[:3]:
                try:
                    topic_repos = await self._fetch_topic_repos(
                        client, topic, limit // 3
                    )
                    opportunities.extend(topic_repos)
                except httpx.HTTPStatusError as exc:
                    logger.warning(
                        "github_topic_http_error",
                        topic=topic,
                        status=exc.response.status_code,
                    )
                except httpx.RequestError as exc:
                    logger.warning(
                        "github_topic_request_error",
                        topic=topic,
                        error=str(exc),
                    )
                except Exception:
                    logger.exception(
                        "github_topic_unexpected_error",
                        topic=topic,
                    )

        return opportunities

    async def _fetch_trending(
        self,
        client: httpx.AsyncClient,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Fetch GitHub trending repositories."""
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": "stars:>100 created:>2024-01-01",
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 30),
        }

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        opportunities = []
        items = data.get("items", [])

        for item in items[:limit]:
            description = item.get("description", "")
            if not description:
                continue

            opp = {
                "title": f"开源项目: {item.get('name', 'Unknown')}",
                "description": description[:4096],
                "source": "GitHub Trending",
                "source_url": item.get("html_url", ""),
                "verified": True,
                "warning": "需要技术能力，通过 GitHub Sponsors 或相关服务变现",
                "tags": ["GitHub", "开源", "技术"],
                "required_skills": ["编程"],
                "investment": 0,
                "age_days": 0,
                "platform_risk": False,
                "monthly_income": 0,
                "hours_per_day": 5.0,
                "success_cases": item.get("stargazers_count", 0),
                "has_tutorial": "README" in str(item.get("topics", [])),
                "has_video_tutorial": False,
                "feedback": [],
            }
            opportunities.append(opp)

        return opportunities

    async def _fetch_topic_repos(
        self,
        client: httpx.AsyncClient,
        topic: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Fetch repositories by topic."""
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": f"topic:{topic} stars:>50",
            "sort": "updated",
            "order": "desc",
            "per_page": min(limit, 10),
        }

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        opportunities = []
        items = data.get("items", [])

        for item in items[:limit]:
            opp = {
                "title": f"GitHub: {item.get('name', 'Unknown')}",
                "description": (item.get("description", "") or item.get("name", ""))[:4096],
                "source": f"GitHub/{topic}",
                "source_url": item.get("html_url", ""),
                "verified": True,
                "warning": "技术项目，需要持续维护",
                "tags": ["GitHub", "开源", topic],
                "required_skills": ["编程"],
                "investment": 0,
                "age_days": 0,
                "platform_risk": False,
                "monthly_income": 0,
                "hours_per_day": 5.0,
                "success_cases": item.get("stargazers_count", 0),
                "has_tutorial": True,
                "has_video_tutorial": False,
                "feedback": [],
            }
            opportunities.append(opp)

        return opportunities

    async def health_check(self) -> bool:
        """Check GitHub API accessibility."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.github.com")
                return response.status_code == 200
        except httpx.RequestError:
            return False
        except Exception:
            logger.exception("github_health_check_failed")
            return False
