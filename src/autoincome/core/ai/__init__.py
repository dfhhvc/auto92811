"""AI-powered analysis modules for AutoIncome.

Provides real LLM-based content analysis, semantic deduplication,
and intelligent recommendation — replacing the legacy rules-only engine.
"""

from __future__ import annotations

from autoincome.core.ai.content_analyzer import ContentAnalyzer
from autoincome.core.ai.llm_client import LLMClient, get_llm_client
from autoincome.core.ai.recommender import AIRecommender
from autoincome.core.ai.semantic_dedup import SemanticDeduplicator

__all__ = [
    "LLMClient",
    "get_llm_client",
    "ContentAnalyzer",
    "AIRecommender",
    "SemanticDeduplicator",
]