"""AI-powered content analysis for side-hustle opportunities.

Uses LLM to:
- Extract structured fields from raw text
- Assess feasibility, credibility, and ROI
- Generate concise summaries and risk warnings
- Identify required skills and time investment
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from autoincome.core.ai.llm_client import LLMClient, get_llm_client

logger = structlog.get_logger(__name__)

_ANALYSIS_PROMPT = """You are an expert side-hustle analyst. Analyze the following opportunity description and output a structured JSON assessment.

Evaluate across these dimensions (score 0.0–10.0):
- feasibility: How easy is it for an average person to start? Lower barrier = higher score.
- timeliness: Is this still viable today? Recent trend = higher score.
- credibility: Does it sound realistic or like a scam? Realistic = higher score.
- roi: Return on time/money investment. High return = higher score.
- replicability: Have others succeeded? Many cases = higher score.

Also extract:
- required_skills: list of skills needed
- time_investment: estimated daily hours
- monthly_income: estimated monthly income in CNY
- investment: upfront cost in CNY
- risk_level: "low", "medium", or "high"
- tags: relevant category tags (max 5)
- summary: one-sentence summary in Chinese
- warning: any red flags or cautions

Output ONLY valid JSON in this exact shape:
{
  "scores": {"feasibility": 0.0, "timeliness": 0.0, "credibility": 0.0, "roi": 0.0, "replicability": 0.0},
  "required_skills": ["string"],
  "time_investment": "2h/天",
  "monthly_income": 3000,
  "investment": 0,
  "risk_level": "low",
  "tags": ["tag1"],
  "summary": "string",
  "warning": "string or null"
}
"""

_SUMMARY_PROMPT = """Summarize this side-hustle opportunity in 2–3 concise Chinese sentences.
Highlight: what it is, who it's for, and the key risk."""

_RISK_PROMPT = """Analyze the risk level of this side-hustle opportunity.
Output JSON: {"risk_level": "low|medium|high", "warning": "specific warning text", "red_flags": ["flag1"]}
If it sounds like a scam, pyramid scheme, or requires upfront payment with no guarantee, mark risk_level as "high"."""


class ContentAnalyzer:
    """LLM-based opportunity content analyzer."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or get_llm_client()

    async def analyze(self, title: str, description: str) -> dict[str, Any]:
        """Full AI analysis of an opportunity.

        Returns structured dict with scores, skills, risks, etc.
        Falls back to heuristic estimation if LLM fails.
        """
        text = f"Title: {title}\n\nDescription: {description}"

        try:
            response = await self.llm.analyze_text(
                text, _ANALYSIS_PROMPT, json_mode=True
            )
            result = json.loads(response.text)
            logger.info("ai_analysis_complete", title=title[:50])
            return self._normalize(result)
        except json.JSONDecodeError as exc:
            logger.warning("ai_analysis_json_parse_failed", error=str(exc))
            return self._fallback_analysis(title, description)
        except Exception as exc:
            logger.warning("ai_analysis_failed", error=str(exc))
            return self._fallback_analysis(title, description)

    async def summarize(self, title: str, description: str) -> str:
        """Generate a concise Chinese summary."""
        text = f"Title: {title}\n\nDescription: {description}"
        try:
            response = await self.llm.analyze_text(text, _SUMMARY_PROMPT)
            return response.text.strip()
        except Exception as exc:
            logger.warning("ai_summary_failed", error=str(exc))
            return description[:200] if description else title

    async def assess_risk(self, title: str, description: str) -> dict[str, Any]:
        """Assess risk level and red flags."""
        text = f"Title: {title}\n\nDescription: {description}"
        try:
            response = await self.llm.analyze_text(text, _RISK_PROMPT, json_mode=True)
            return json.loads(response.text)
        except Exception as exc:
            logger.warning("ai_risk_assessment_failed", error=str(exc))
            return {"risk_level": "medium", "warning": "请自行验证", "red_flags": []}

    def _normalize(self, result: dict[str, Any]) -> dict[str, Any]:
        """Normalize LLM output to standard schema."""
        scores = result.get("scores", {})
        return {
            "score_feasibility": round(float(scores.get("feasibility", 5.0)), 1),
            "score_timeliness": round(float(scores.get("timeliness", 5.0)), 1),
            "score_credibility": round(float(scores.get("credibility", 5.0)), 1),
            "score_roi": round(float(scores.get("roi", 5.0)), 1),
            "score_replicability": round(float(scores.get("replicability", 5.0)), 1),
            "required_skills": result.get("required_skills", []),
            "time_investment": result.get("time_investment", "2h/天"),
            "monthly_income": int(result.get("monthly_income", 0)),
            "investment": int(result.get("investment", 0)),
            "risk_level": result.get("risk_level", "medium"),
            "tags": result.get("tags", []),
            "summary": result.get("summary", ""),
            "warning": result.get("warning") or "请自行验证",
        }

    def _fallback_analysis(self, title: str, description: str) -> dict[str, Any]:
        """Heuristic fallback when LLM is unavailable."""
        from autoincome.core.analyzer.scorer import Scorer

        scorer = Scorer()
        item = {"title": title, "description": description}
        score = scorer.score(item)

        return {
            "score_feasibility": score.feasibility,
            "score_timeliness": score.timeliness,
            "score_credibility": score.credibility,
            "score_roi": score.roi,
            "score_replicability": score.replicability,
            "required_skills": [],
            "time_investment": "2h/天",
            "monthly_income": 0,
            "investment": 0,
            "risk_level": "medium",
            "tags": [],
            "summary": title,
            "warning": "AI分析服务暂时不可用，请自行判断",
        }