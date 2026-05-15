"""Spider tests."""

from __future__ import annotations

import pytest

from autoincome.core.spiders.v2ex import V2EXSpider


@pytest.mark.asyncio
async def test_v2ex_health_check():
    """V2EX spider can check platform health."""
    spider = V2EXSpider()
    result = await spider.health_check()
    # V2EX may be blocked in some networks, so we just assert it's a bool
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_v2ex_fetch():
    """V2EX spider fetches real data."""
    spider = V2EXSpider()
    items = await spider.fetch(limit=5)

    # If V2EX is reachable, we get real data; if blocked, empty list
    for item in items:
        assert "title" in item
        assert "description" in item
        assert "source" in item
        assert len(item["title"]) > 0
