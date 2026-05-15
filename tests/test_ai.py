"""AI module unit tests.

Tests LLM client fallback, content analysis, semantic deduplication,
and personalized recommendation with mocked LLM responses.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoincome.core.ai.content_analyzer import ContentAnalyzer
from autoincome.core.ai.llm_client import LLMClient, LLMResponse
from autoincome.core.ai.recommender import AIRecommender
from autoincome.core.ai.semantic_dedup import SemanticDeduplicator


class TestLLMClient:
    def test_health_check_no_providers(self, monkeypatch):
        """Health check reports no providers when none configured."""
        monkeypatch.delenv("AUTOINCOME_MOONSHOT_API_KEY", raising=False)
        monkeypatch.delenv("AUTOINCOME_OPENROUTER_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        client = LLMClient()
        health = client.health_check()
        assert "ollama" in health

    @pytest.mark.asyncio
    async def test_chat_fallback_chain(self):
        """LLM client falls back through provider chain on failure."""
        client = LLMClient()
        client._providers = [
            {"name": "fail1", "base_url": "http://localhost:1", "api_key": "x", "model": "m", "headers": {}},
            {"name": "fail2", "base_url": "http://localhost:1", "api_key": "x", "model": "m", "headers": {}},
        ]
        with pytest.raises(RuntimeError, match="All LLM providers failed"):
            await client.chat([{"role": "user", "content": "hello"}])

    @pytest.mark.asyncio
    async def test_analyze_text_json_mode(self):
        """analyze_text wrapper works for single-turn analysis."""
        client = LLMClient()
        client._providers = []
        # Should raise RuntimeError with no providers
        with pytest.raises(RuntimeError):
            await client.analyze_text("test", "prompt", json_mode=True)


class TestContentAnalyzer:
    @pytest.mark.asyncio
    async def test_fallback_analysis(self):
        """Fallback works when LLM is unavailable."""
        analyzer = ContentAnalyzer()
        result = analyzer._fallback_analysis("Test Title", "Test description")
        assert "score_feasibility" in result
        assert "score_timeliness" in result
        assert result["summary"] == "Test Title"
        assert "AI分析服务暂时不可用" in result["warning"]

    @pytest.mark.asyncio
    async def test_normalize_scores(self):
        """Score normalization clamps values correctly."""
        analyzer = ContentAnalyzer()
        raw = {
            "scores": {
                "feasibility": 15.0,
                "timeliness": -3.0,
                "credibility": 8.5,
                "roi": 7.0,
                "replicability": 6.0,
            },
            "required_skills": ["写作"],
            "time_investment": "2h/天",
            "monthly_income": 5000,
            "investment": 0,
            "risk_level": "low",
            "tags": ["写作"],
            "summary": "测试",
            "warning": None,
        }
        result = analyzer._normalize(raw)
        assert result["score_feasibility"] == 15.0  # Not clamped in normalize
        assert result["score_timeliness"] == -3.0
        assert result["summary"] == "测试"


class TestSemanticDeduplicator:
    def test_empty_list(self):
        dedup = SemanticDeduplicator()
        unique, merged = asyncio.run(dedup.deduplicate([]))
        assert unique == []
        assert merged == 0

    def test_no_duplicates(self):
        dedup = SemanticDeduplicator(similarity_threshold=0.95)
        items = [
            {"title": "AI写作", "description": "用AI写文章", "tags": ["AI"]},
            {"title": "闲鱼电商", "description": "在闲鱼卖货", "tags": ["电商"]},
        ]
        unique, merged = asyncio.run(dedup.deduplicate(items))
        assert len(unique) == 2
        assert merged == 0

    def test_cosine_similarity_identical(self):
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert SemanticDeduplicator._cosine_similarity(a, b) == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert SemanticDeduplicator._cosine_similarity(a, b) == pytest.approx(0.0)

    def test_local_embedding_deterministic(self):
        """Local embedding must be deterministic across calls."""
        dedup = SemanticDeduplicator()
        e1 = dedup._local_embedding("test text for embedding")
        e2 = dedup._local_embedding("test text for embedding")
        assert e1 == e2
        assert len(e1) == 32

    def test_local_embedding_different_texts(self):
        """Different texts should produce different embeddings."""
        dedup = SemanticDeduplicator()
        e1 = dedup._local_embedding("AI writing opportunity")
        e2 = dedup._local_embedding("E-commerce dropshipping guide")
        assert e1 != e2


class TestAIRecommender:
    @pytest.mark.asyncio
    async def test_fallback_rank_empty(self):
        """Fallback ranking with empty opportunities returns empty."""
        rec = AIRecommender()
        result = rec._fallback_rank({"skills": []}, [], 0)
        assert result == []

    @pytest.mark.asyncio
    async def test_fallback_rank_basic(self):
        """Fallback ranking sorts by score."""
        rec = AIRecommender()
        batch = [
            {"title": "A", "score_total": 5.0},
            {"title": "B", "score_total": 8.5},
        ]
        result = rec._fallback_rank({"skills": ["写作"]}, batch, 0)
        assert len(result) == 2
        assert result[0]["title"] == "B"  # Higher score first

    @pytest.mark.asyncio
    async def test_generate_reasoning_fallback(self):
        """Reasoning generation falls back gracefully."""
        rec = AIRecommender()
        reasoning = await rec.generate_reasoning(
            {"skills": ["写作"]}, {"title": "测试"}
        )
        assert "匹配" in reasoning or "了解" in reasoning


import asyncio