"""Prometheus metrics exposure for monitoring.

Exposes:
- HTTP request latency histogram
- Request count by method/status/endpoint
- Active connections gauge
- Spider execution metrics
- Cache hit/miss rates
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

from autoincome import __version__

# ── Application Info ────────────────────────────────────────────

app_info = Info("autoincome", "Application information")
app_info.info({"version": __version__})

# ── HTTP Metrics ────────────────────────────────────────────────

http_requests_total = Counter(
    "autoincome_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "autoincome_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

active_connections = Gauge(
    "autoincome_active_connections",
    "Number of active connections",
)

# ── Spider Metrics ──────────────────────────────────────────────

spider_runs_total = Counter(
    "autoincome_spider_runs_total",
    "Total spider executions",
    ["spider_name", "status"],
)

spider_duration_seconds = Histogram(
    "autoincome_spider_duration_seconds",
    "Spider execution duration",
    ["spider_name"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
)

spider_results_count = Counter(
    "autoincome_spider_results_total",
    "Total results fetched by spiders",
    ["spider_name"],
)

# ── Cache Metrics ───────────────────────────────────────────────

cache_hits_total = Counter(
    "autoincome_cache_hits_total",
    "Total cache hits",
    ["cache_type"],
)

cache_misses_total = Counter(
    "autoincome_cache_misses_total",
    "Total cache misses",
    ["cache_type"],
)

# ── Business Metrics ────────────────────────────────────────────

opportunities_scored_total = Counter(
    "autoincome_opportunities_scored_total",
    "Total opportunities scored",
)

opportunities_deduplicated_total = Counter(
    "autoincome_opportunities_deduplicated_total",
    "Total duplicate opportunities merged",
)

notifications_sent_total = Counter(
    "autoincome_notifications_sent_total",
    "Total notifications sent",
    ["channel", "status"],
)

# ── Helpers ─────────────────────────────────────────────────────

@contextmanager
def measure_http_request(method: str, endpoint: str) -> Generator[None, None, None]:
    """Context manager to measure HTTP request duration."""
    active_connections.inc()
    with http_request_duration_seconds.labels(
        method=method, endpoint=endpoint
    ).time():
        try:
            yield
        finally:
            active_connections.dec()


def record_spider_run(spider_name: str, status: str, duration: float, results: int) -> None:
    """Record spider execution metrics."""
    spider_runs_total.labels(spider_name=spider_name, status=status).inc()
    spider_duration_seconds.labels(spider_name=spider_name).observe(duration)
    spider_results_count.labels(spider_name=spider_name).inc(results)


def record_cache_hit(cache_type: str = "default") -> None:
    """Record cache hit."""
    cache_hits_total.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str = "default") -> None:
    """Record cache miss."""
    cache_misses_total.labels(cache_type=cache_type).inc()


def get_metrics() -> bytes:
    """Generate Prometheus metrics output."""
    return generate_latest()
