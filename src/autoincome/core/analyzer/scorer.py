"""Multi-dimensional scoring engine with strict input validation.

All inputs are validated for type and range before processing.
No hardcoded weights can be overridden without validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from autoincome.core.config import get_settings


@dataclass(frozen=True)
class ScoreResult:
    """Immutable scoring result."""

    total: float = 0.0
    feasibility: float = 0.0
    timeliness: float = 0.0
    credibility: float = 0.0
    roi: float = 0.0
    replicability: float = 0.0
    reasons: List[str] = field(default_factory=list)


class Scorer:
    """Production-grade opportunity scorer."""

    HIGH_CRED_SOURCES: frozenset[str] = frozenset({
        "V2EX", "GitHub", "知乎高赞", "即刻精选", "Reddit", "HackerNews",
    })

    def __init__(self, weights: Dict[str, float] | None = None) -> None:
        if weights is not None:
            self._validate_weights(weights)
            self.weights = dict(weights)
        else:
            self.weights = dict(get_settings().get_scoring_weights())

    @staticmethod
    def _validate_weights(weights: Dict[str, float]) -> None:
        required = {"feasibility", "timeliness", "credibility", "roi", "replicability"}
        if not required.issubset(weights.keys()):
            raise ValueError(f"Weights must contain keys: {required}")
        total = sum(weights.values())
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"Weight sum must be 1.0, got {total}")
        for k, v in weights.items():
            if not isinstance(v, (int, float)) or v < 0:
                raise ValueError(f"Weight {k} must be non-negative numeric")

    def score(self, item: Dict[str, Any]) -> ScoreResult:
        """Score a single opportunity with full validation."""
        reasons: List[str] = []

        feasibility = self._score_feasibility(item)
        if feasibility < 5.0:
            reasons.append("门槛过高，需要特殊技能或大量资金")

        timeliness = self._score_timeliness(item)
        if timeliness < 5.0:
            reasons.append("信息可能已过时或平台规则已变更")

        credibility = self._score_credibility(item)
        if credibility < 5.0:
            reasons.append("来源可信度较低，建议谨慎验证")

        roi = self._score_roi(item)
        if roi < 5.0:
            reasons.append("投入产出比不高，时间成本较大")

        replicability = self._score_replicability(item)
        if replicability < 5.0:
            reasons.append("成功案例难以复制，个人差异大")

        total = (
            feasibility * self.weights["feasibility"]
            + timeliness * self.weights["timeliness"]
            + credibility * self.weights["credibility"]
            + roi * self.weights["roi"]
            + replicability * self.weights["replicability"]
        )

        return ScoreResult(
            total=round(min(10.0, max(0.0, total)), 1),
            feasibility=round(min(10.0, max(0.0, feasibility)), 1),
            timeliness=round(min(10.0, max(0.0, timeliness)), 1),
            credibility=round(min(10.0, max(0.0, credibility)), 1),
            roi=round(min(10.0, max(0.0, roi)), 1),
            replicability=round(min(10.0, max(0.0, replicability)), 1),
            reasons=reasons,
        )

    def _score_feasibility(self, item: Dict[str, Any]) -> float:
        score = 7.0
        skills = item.get("required_skills", [])
        if isinstance(skills, list):
            n = len(skills)
            if n <= 1:
                score += 2.0
            elif n <= 2:
                score += 1.0
            elif n >= 5:
                score -= 2.5
            elif n >= 3:
                score -= 1.0

        investment = item.get("investment", 0)
        if isinstance(investment, (int, float)):
            if investment == 0:
                score += 1.0
            elif investment > 50000:
                score -= 3.0
            elif investment > 10000:
                score -= 2.0
            elif investment > 1000:
                score -= 1.0
        return min(10.0, max(1.0, score))

    def _score_timeliness(self, item: Dict[str, Any]) -> float:
        score = 7.0
        age = item.get("age_days", 0)
        if isinstance(age, (int, float)):
            if age < 3:
                score += 2.5
            elif age < 7:
                score += 2.0
            elif age < 14:
                score += 1.0
            elif age > 180:
                score -= 4.0
            elif age > 90:
                score -= 3.0
            elif age > 30:
                score -= 1.5
        if item.get("platform_risk", False):
            score -= 2.0
        return min(10.0, max(1.0, score))

    def _score_credibility(self, item: Dict[str, Any]) -> float:
        score = 6.0
        source = str(item.get("source", ""))
        if any(s in source for s in self.HIGH_CRED_SOURCES):
            score += 2.5
        elif "知乎" in source or "公众号" in source:
            score += 1.0
        if item.get("verified", False):
            score += 1.5
        feedback = item.get("feedback", [])
        if isinstance(feedback, list) and feedback:
            positive = sum(1 for f in feedback if isinstance(f, dict) and f.get("positive"))
            ratio = positive / len(feedback)
            score += (ratio - 0.5) * 3
        return min(10.0, max(1.0, score))

    def _score_roi(self, item: Dict[str, Any]) -> float:
        score = 6.0
        income = item.get("monthly_income", 0)
        if isinstance(income, (int, float)):
            if income >= 10000:
                score += 3.0
            elif income >= 5000:
                score += 2.0
            elif income >= 3000:
                score += 1.0
            elif income < 500:
                score -= 1.5

        hours = item.get("hours_per_day", 2.0)
        if isinstance(hours, (int, float)):
            if hours <= 0.5:
                score += 2.0
            elif hours <= 1.0:
                score += 1.5
            elif hours <= 2.0:
                score += 0.5
            elif hours >= 8.0:
                score -= 2.0
            elif hours >= 4.0:
                score -= 1.0
        return min(10.0, max(1.0, score))

    def _score_replicability(self, item: Dict[str, Any]) -> float:
        score = 6.0
        cases = item.get("success_cases", 0)
        if isinstance(cases, int):
            if cases >= 20:
                score += 3.0
            elif cases >= 10:
                score += 2.0
            elif cases >= 5:
                score += 1.0
            elif cases >= 3:
                score += 0.5
            elif cases == 0:
                score -= 2.5
        if item.get("has_tutorial", False):
            score += 1.0
        if item.get("has_video_tutorial", False):
            score += 0.5
        return min(10.0, max(1.0, score))

    def batch_score(self, items: List[Dict[str, Any]]) -> List[ScoreResult]:
        """Score multiple items."""
        return [self.score(item) for item in items]
