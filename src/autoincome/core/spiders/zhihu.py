"""知乎爬虫 - fetches hot topics and search results from Zhihu.

Uses Zhihu public API (no auth required for hot lists).
"""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from autoincome.core.spiders.base import BaseSpider

logger = logging.getLogger(__name__)


class ZhihuSpider(BaseSpider):
    """Fetch side-hustle-related content from Zhihu."""

    name = "zhihu"
    base_url = "https://www.zhihu.com/api"

    SEARCH_QUERIES = [
        "副业赚钱",
        "被动收入",
        "自由职业",
        "独立开发者赚钱",
        "AI赚钱",
    ]

    async def fetch(self, limit: int = 20, **kwargs: Any) -> list[dict[str, Any]]:
        """Fetch hot search results related to side hustles."""
        opportunities: list[dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                hot_items = await self._fetch_hot_list(client, limit)
                opportunities.extend(hot_items)
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "zhihu_hot_list_http_error",
                    status=exc.response.status_code,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "zhihu_hot_list_request_error",
                    error=str(exc),
                )
            except Exception:
                logger.exception("zhihu_hot_list_unexpected_error")

            for query in self.SEARCH_QUERIES:
                try:
                    search_items = await self._fetch_search(
                        client, query, limit // 3
                    )
                    opportunities.extend(search_items)
                except httpx.HTTPStatusError as exc:
                    logger.warning(
                        "zhihu_search_http_error",
                        query=query,
                        status=exc.response.status_code,
                    )
                except httpx.RequestError as exc:
                    logger.warning(
                        "zhihu_search_request_error",
                        query=query,
                        error=str(exc),
                    )
                except Exception:
                    logger.exception(
                        "zhihu_search_unexpected_error",
                        query=query,
                    )

        return opportunities

    async def _fetch_hot_list(
        self,
        client: httpx.AsyncClient,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Fetch Zhihu hot list."""
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        opportunities = []
        items = data.get("data", [])[:limit]

        for item in items:
            target = item.get("target", {})
            title = target.get("title", "")
            excerpt = target.get("excerpt", "")

            if not self._is_side_hustle_related(title):
                continue

            opp = {
                "title": title[:256],
                "description": (excerpt or title)[:4096],
                "source": "知乎热榜",
                "source_url": f"https://www.zhihu.com/question/{target.get('id', '')}",
                "verified": False,
                "warning": "信息来自知乎热榜，请自行验证真实性",
                "tags": ["知乎", "热榜"],
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

    async def _fetch_search(
        self,
        client: httpx.AsyncClient,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search Zhihu for specific queries."""
        url = "https://www.zhihu.com/api/v4/search_v3"
        params = {
            "t": "general",
            "q": query,
            "correction": "1",
            "offset": "0",
            "limit": str(limit),
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        opportunities = []
        items = data.get("data", [])

        for item in items:
            obj = item.get("object", {})
            if obj.get("type") != "answer":
                continue

            content = obj.get("content", "")
            text = re.sub(r"<[^>]+>", "", content)

            if len(text) < 50:
                continue

            question = obj.get("question", {})
            title = question.get("name", "")[:256]

            opp = {
                "title": title or f"知乎搜索: {query}",
                "description": text[:4096],
                "source": f"知乎搜索/{query}",
                "source_url": f"https://www.zhihu.com/question/{question.get('id', '')}",
                "verified": False,
                "warning": "信息来自知乎搜索，请自行验证",
                "tags": ["知乎", "搜索", query],
                "required_skills": [],
                "investment": 0,
                "age_days": 0,
                "platform_risk": False,
                "monthly_income": 0,
                "hours_per_day": 2.0,
                "success_cases": 0,
                "has_tutorial": len(text) > 500,
                "has_video_tutorial": False,
                "feedback": [],
            }
            opportunities.append(opp)

        return opportunities

    def _is_side_hustle_related(self, title: str) -> bool:
        """Check if title is related to side hustles."""
        keywords = [
            "赚钱", "副业", "收入", "自由职业", "兼职", "创业",
            "被动收入", "睡后收入", "斜杠", "月入", "年入",
            "独立开发", "自媒体", "电商", "AI", "chatgpt",
        ]
        title_lower = title.lower()
        return any(kw in title_lower for kw in keywords)

    async def health_check(self) -> bool:
        """Check Zhihu API accessibility."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://www.zhihu.com",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False
        except Exception:
            logger.exception("zhihu_health_check_failed")
            return False
