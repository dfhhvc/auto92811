"""Redis cache layer with async support.

Provides:
- Key-value caching with TTL
- Cache-aside pattern helpers
- Distributed rate limiting
- Spider result caching
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any

import redis.asyncio as aioredis
from autoincome.core.config import get_settings

_redis_pool: aioredis.Redis | None = None


class CacheManager:
    """Async Redis cache manager."""

    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        settings = get_settings()
        self._redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._redis

    # ── Basic Operations ──────────────────────────────────────────

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> None:
        """Set value in cache with TTL (seconds)."""
        serialized = json.dumps(value, default=str)
        await self.redis.setex(key, ttl, serialized)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.redis.exists(key) > 0

    async def ping(self) -> bool:
        """Check Redis connectivity."""
        try:
            return await self.redis.ping() == "PONG"
        except Exception:
            return False

    async def flush_namespace(self, namespace: str) -> None:
        """Clear keys matching a namespace pattern (safe scoped deletion)."""
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=f"{namespace}:*", count=100)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break

    # ── Cache-Aside Pattern ───────────────────────────────────────

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int = 3600,
    ) -> Any:
        """Cache-aside: get from cache or compute and store."""
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await factory()
        await self.set(key, value, ttl)
        return value

    # ── Spider Result Caching ─────────────────────────────────────

    def _spider_key(self, spider_name: str, params: dict | None = None) -> str:
        """Generate cache key for spider results."""
        key_data = f"spider:{spider_name}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    async def get_spider_result(
        self,
        spider_name: str,
        params: dict | None = None,
    ) -> list[dict] | None:
        """Get cached spider results."""
        key = self._spider_key(spider_name, params)
        return await self.get(key)

    async def set_spider_result(
        self,
        spider_name: str,
        data: list[dict],
        params: dict | None = None,
        ttl: int = 1800,  # 30 min default for spider results
    ) -> None:
        """Cache spider results."""
        key = self._spider_key(spider_name, params)
        await self.set(key, data, ttl)

    # ── Distributed Rate Limiting ─────────────────────────────────

    async def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """Check if key is rate limited (distributed)."""
        pipe = self.redis.pipeline()
        now = await self.redis.time()
        current_time = now[0]
        window_start = current_time - window_seconds

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Count current entries
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        # Set expiry on the key
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        request_count = results[1]

        return request_count > max_requests

    # ── Statistics ────────────────────────────────────────────────

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        info = await self.redis.info("memory")
        return {
            "used_memory_human": info.get("used_memory_human", "unknown"),
            "used_memory_peak_human": info.get("used_memory_peak_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
        }


# Global singleton
cache = CacheManager()