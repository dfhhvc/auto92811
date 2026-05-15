"""AI-powered personalized recommendation engine.

Replaces rules-only matching with LLM-driven understanding of:
- User skills, time budget, risk tolerance
- Opportunity content and requirements
- Historical user behavior and feedback
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from autoincome.core.ai.llm_client import LLMClient, get_llm_client

logger = structlog.get_logger(__name__)

_RECOMMEND_PROMPT = """You are a personalized side-hustle recommendation engine.

Given a USER PROFILE and a list of OPPORTUNITIES, rank the opportunities by relevance.
For each opportunity, provide:
- match_score: 0.0–10.0 (higher = better fit)
- match_reasons: 2–3 short Chinese sentences explaining WHY this fits
- risk_note: any caution specific to this user's profile

Output ONLY valid JSON in this exact shape:
{
  "rankings": [
    {
      "index": 0,
      "match_score": 8.5,
      "match_reasons": ["理由1", "理由2"],
      "risk_note": "风险提示或null"
    }
  ]
}
"""


class AIRecommender:
    """LLM-based personalized recommender."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or get_llm_client()

    async def recommend(
        self,
        user_profile: dict[str, Any],
        opportunities: list[dict[str, Any]],
        top_n: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate AI-powered recommendations.

        Falls back to rules-based matching if LLM fails.
        """
        if not opportunities:
            return []

        # Batch opportunities to stay within context window
        batch_size = 10
        all_rankings: list[dict[str, Any]] = []

        for i in range(0, len(opportunities), batch_size):
            batch = opportunities[i:i + batch_size]
            try:
                rankings = await self._recommend_batch(user_profile, batch, i)
                all_rankings.extend(rankings)
            except Exception as exc:
                logger.warning("ai_recommend_batch_failed", batch=i, error=str(exc))
                # Fallback for this batch
                all_rankings.extend(self._fallback_rank(user_profile, batch, i))

        # Sort by match_score descending
        all_rankings.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return all_rankings[:top_n]

    async def _recommend_batch(
        self,
        user_profile: dict[str, Any],
        batch: list[dict[str, Any]],
        offset: int,
    ) -> list[dict[str, Any]]:
        """Recommend for a single batch."""
        profile_text = json.dumps(user_profile, ensure_ascii=False, indent=2)
        opp_text = json.dumps(batch, ensure_ascii=False, indent=2)

        text = f"USER PROFILE:\n{profile_text}\n\nOPPORTUNITIES:\n{opp_text}"

        response = await self.llm.analyze_text(
            text, _RECOMMEND_PROMPT, json_mode=True
        )
        result = json.loads(response.text)
        rankings = result.get("rankings", [])

        # Merge ranking data back into opportunity dicts
        output = []
        for r in rankings:
            idx = r.get("index", 0)
            if 0 <= idx < len(batch):
                opp = batch[idx].copy()
                opp["match_score"] = round(float(r.get("match_score", 5.0)), 1)
                opp["match_reasons"] = r.get("match_reasons", [])
                opp["risk_note"] = r.get("risk_note")
                output.append(opp)

        return output

    def _fallback_rank(
        self,
        user_profile: dict[str, Any],
        batch: list[dict[str, Any]],
        offset: int,
    ) -> list[dict[str, Any]]:
        """Rules-based fallback when LLM is unavailable."""
        from autoincome.core.analyzer.recommender import Recommender, UserProfile

        try:
            profile = UserProfile(
                skills=user_profile.get("skills", []),
                time_budget=user_profile.get("time_budget", "2h"),
                risk_level=user_profile.get("risk_level", "moderate"),
                languages=user_profile.get("languages", ["zh"]),
            )
            rec = Recommender(profile)
            return rec.recommend(batch, top_n=len(batch))
        except Exception:
            # Last resort: score-based sort
            scored = []
            for opp in batch:
                opp_copy = opp.copy()
                opp_copy["match_score"] = opp.get("score_total", 5.0)
                opp_copy["match_reasons"] = ["基于综合评分推荐"]
                scored.append(opp_copy)
            scored.sort(key=lambda x: x["match_score"], reverse=True)
            return scored

    async def generate_reasoning(
        self,
        user_profile: dict[str, Any],
        opportunity: dict[str, Any],
    ) -> str:
        """Generate natural-language reasoning for a single recommendation."""
        prompt = """Explain in 2–3 friendly Chinese sentences why this opportunity matches the user.
Be specific about skills and time. Mention any caveats."""
        text = (
            f"User: {json.dumps(user_profile, ensure_ascii=False)}\n\n"
            f"Opportunity: {json.dumps(opportunity, ensure_ascii=False)}"
        )
        try:
            response = await self.llm.analyze_text(text, prompt)
            return response.text.strip()
        except Exception as exc:
            logger.warning("reasoning_generation_failed", error=str(exc))
            return "该机会与您的资料较为匹配，建议进一步了解。"