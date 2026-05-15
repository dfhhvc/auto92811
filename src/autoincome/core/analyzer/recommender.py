"""Personalized recommendation engine with real matching algorithm."""

from __future__ import annotations

from typing import Dict, List, Tuple

from autoincome.core.analyzer.scorer import ScoreResult, Scorer


class UserProfile:
    """User profile for personalized matching."""

    TIME_BUDGET_MAP = {
        "1h": 1.0,
        "2h": 2.0,
        "4h": 4.0,
        "8h": 8.0,
    }

    RISK_MULTIPLIERS = {
        "conservative": 0.8,
        "moderate": 1.0,
        "aggressive": 1.2,
    }

    def __init__(
        self,
        skills: List[str],
        time_budget: str,
        risk_level: str,
        languages: List[str] | None = None,
    ) -> None:
        self.skills = [s.lower() for s in skills]
        self.time_budget = time_budget
        self.risk_level = risk_level
        self.languages = languages or ["zh"]
        self.daily_hours = self.TIME_BUDGET_MAP.get(time_budget, 2.0)
        self.risk_multiplier = self.RISK_MULTIPLIERS.get(risk_level, 1.0)

    def __repr__(self) -> str:
        return f"UserProfile(skills={self.skills}, time={self.time_budget}, risk={self.risk_level})"


class Recommender:
    """Personalized opportunity recommender."""

    SKILL_MATCH_WEIGHT = 0.25
    TIME_MATCH_WEIGHT = 0.20
    RISK_MATCH_WEIGHT = 0.15
    SCORE_WEIGHT = 0.40

    RISK_TAGS = {
        "low": ["被动收入", "长期", "稳健"],
        "medium": ["兼职", "技能变现", "内容创作"],
        "high": ["创业", "投资", "快速见效", "风险"],
    }

    def __init__(self, user_profile: UserProfile) -> None:
        self.user = user_profile
        self.scorer = Scorer()

    def calculate_match_score(self, opportunity: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate match score between user and opportunity."""
        reasons = []

        skill_score = self._match_skills(opportunity)
        if skill_score > 0.8:
            reasons.append("与你的技能高度匹配")
        elif skill_score > 0.5:
            reasons.append("部分技能可迁移")

        time_score = self._match_time(opportunity)
        if time_score > 0.9:
            reasons.append("时间投入符合你的预算")
        elif time_score < 0.5:
            reasons.append("⚠️ 时间投入超出预算")

        risk_score = self._match_risk(opportunity)
        if risk_score > 0.8:
            reasons.append("风险水平符合你的偏好")

        base_score = self._get_base_score(opportunity)

        match_score = (
            skill_score * self.SKILL_MATCH_WEIGHT +
            time_score * self.TIME_MATCH_WEIGHT +
            risk_score * self.RISK_MATCH_WEIGHT +
            base_score * self.SCORE_WEIGHT
        )

        return round(match_score * 10, 1), reasons

    def _match_skills(self, opportunity: Dict[str, Any]) -> float:
        """Calculate skill match percentage."""
        opp_skills = [s.lower() for s in opportunity.get("tags", [])]
        if not opp_skills:
            return 0.5

        matched = sum(
            1 for skill in self.user.skills
            if any(skill in opp for opp in opp_skills)
        )
        return min(1.0, matched / max(len(self.user.skills), 1))

    def _match_time(self, opportunity: Dict[str, Any]) -> float:
        """Calculate time budget match."""
        time_str = opportunity.get("time_investment", "")
        hours = self._parse_time_string(time_str)
        if hours is None:
            return 0.5

        ratio = self.user.daily_hours / hours if hours > 0 else 1.0
        if ratio >= 1.0:
            return 1.0
        elif ratio >= 0.5:
            return 0.7
        else:
            return 0.3

    def _parse_time_string(self, time_str: str) -> float | None:
        """Parse time investment string."""
        import re

        daily_match = re.search(r'(\d+(?:\.\d+)?)\s*h/天', time_str)
        if daily_match:
            return float(daily_match.group(1))

        weekly_match = re.search(r'(\d+(?:\.\d+)?)\s*h/周', time_str)
        if weekly_match:
            return float(weekly_match.group(1)) / 7

        num_match = re.search(r'(\d+(?:\.\d+)?)', time_str)
        if num_match:
            return float(num_match.group(1))

        return None

    def _match_risk(self, opportunity: Dict[str, Any]) -> float:
        """Calculate risk preference match."""
        tags = [t.lower() for t in opportunity.get("tags", [])]

        risk_level = "medium"
        for level, risk_tags in self.RISK_TAGS.items():
            if any(tag in tags for tag in risk_tags):
                risk_level = level
                break

        user_risk = self.user.risk_level

        if user_risk == "conservative":
            return 1.0 if risk_level == "low" else (0.6 if risk_level == "medium" else 0.2)
        elif user_risk == "moderate":
            return 0.8 if risk_level == "medium" else (0.6 if risk_level == "low" else 0.5)
        else:
            return 1.0 if risk_level == "high" else (0.7 if risk_level == "medium" else 0.4)

    def _get_base_score(self, opportunity: Dict[str, Any]) -> float:
        """Get normalized base score."""
        score = opportunity.get("score", 5.0)
        return min(1.0, score / 10.0)

    def recommend(
        self,
        opportunities: List[Dict[str, Any]],
        top_n: int = 3,
    ) -> List[Dict[str, Any]]:
        """Recommend top N opportunities for the user."""
        scored = []
        for opp in opportunities:
            match_score, reasons = self.calculate_match_score(opp)
            opp_copy = opp.copy()
            opp_copy["match_score"] = match_score
            opp_copy["match_reasons"] = reasons
            scored.append(opp_copy)

        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored[:top_n]
