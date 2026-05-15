"""API endpoint tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from autoincome.api.main import app
from autoincome.core.config import reload_settings
from autoincome.core.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    """Override settings for tests."""
    monkeypatch.setenv("AUTOINCOME_SECRET_KEY", "test-secret-key-32-chars-long!!!")
    reload_settings()


@pytest.fixture(autouse=True)
async def setup_db():
    """Initialize test database."""
    await init_db()


def test_health_check():
    """Health endpoint returns correct structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert data["database"] in ("connected", "disconnected", "error")


def test_list_opportunities():
    """Opportunities list endpoint works."""
    response = client.get("/api/v1/opportunities?min_score=5.0&max_results=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_scan_endpoint():
    """Scan endpoint triggers without error."""
    response = client.post("/api/v1/opportunities/scan?min_score=5.0&max_results=5")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "raw_count" in data
    assert "elapsed_seconds" in data


def test_config_endpoint():
    """Public config endpoint returns safe data."""
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "env" in data
    assert "features" in data
    assert "scoring" in data
    assert "secret_key" not in str(data).lower()


def test_root_returns_html():
    """Root path serves HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_security_headers():
    """Security headers are present."""
    response = client.get("/api/v1/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers
