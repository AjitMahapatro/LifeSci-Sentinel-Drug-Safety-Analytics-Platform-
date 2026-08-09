"""Grounded AI analytics assistant for LifeSci Sentinel.

This assistant answers questions using ACTUAL data from the LifeSci Sentinel
analytics/database layer. It is NOT a generic chatbot.

Architecture:
    User question
        -> Intent understanding (keyword-based router)
        -> Structured analytics/database retrieval (DatabaseService)
        -> Trusted result set
        -> LLM explanation (optional) OR rule-based explanation (default)
        -> Answer

The LLM is never the source of truth for numbers. All metrics come from the
database/analytics layer. If no LLM API key is configured, a fully functional
rule-based explanation generator is used (offline, no network required).

The assistant NEVER invents statistics.
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional

from api.services.database_service import get_database_service

DISCLAIMER = (
    "LifeSci Sentinel provides analytical decision support based on available "
    "adverse-event data. It does not provide medical diagnosis, treatment "
    "recommendations, or establish causality."
)


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------


class AIIntent:
    DRUG_LIST = "drug_list"
    DRUG_PROFILE = "drug_profile"
    REACTION_LIST = "reaction_list"
    OVERVIEW = "overview"
    SIGNALS = "signals"
    SIGNAL_WHY = "signal_why"
    COMPARE = "compare"
    TRENDS = "trends"
    UNKNOWN = "unknown"


class IntentRouter:
    """Detect the intended analytical question from free-text."""

    def __init__(self) -> None:
        self.drug_patterns = [
            r"drug[s]?\s+with\s+highest\s+serious",
            r"top\s+drugs",
            r"most\s+reported\s+drugs",
            r"list\s+drugs",
            r"which\s+drugs",
        ]
        self.profile_patterns = [
            r"safety\s+profile\s+of\s+",
            r"profile\s+of\s+(\w+)",
            r"show\s+me\s+(.+?)\s+report",
            r"about\s+drug\s+(\w+)",
        ]
        self.reaction_patterns = [
            r"top\s+reactions",
            r"reactions\s+associated\s+with\s+",
            r"most\s+common\s+reactions",
            r"reactions\s+for\s+",
        ]
        self.signal_patterns = [
            r"high.-?priority\s+signals",
            r"signals\s+need\s+investigation",
            r"which\s+signals",
            r"current\s+signals",
            r"high\s+priority",
            r"signal",
        ]
        self.why_patterns = [
            r"why\s+was\s+(\w+)\s+flagged",
            r"why\s+is\s+(\w+)\s+high",
            r"why\s+.*\bhigh\b",
        ]
        self.trend_patterns = [
            r"trend",
            r"over\s+time",
            r"changed\s+in\s+reporting",
            r"reporting\s+over",
        ]

    def route(self, question: str) -> str:
        q = question.lower()
        if re.search(r"compare\s+(\w+)\s+and\s+(\w+)", q):
            return AIIntent.COMPARE
        if self._match_any(q, self.why_patterns):
            return AIIntent.SIGNAL_WHY
        if self._match_any(q, self.signal_patterns):
            return AIIntent.SIGNALS
        if self._match_any(q, self.profile_patterns):
            return AIIntent.DRUG_PROFILE
        if self._match_any(q, self.reaction_patterns):
            return AIIntent.REACTION_LIST
        if self._match_any(q, self.trend_patterns):
            return AIIntent.TRENDS
        if self._match_any(q, self.drug_patterns):
            return AIIntent.DRUG_LIST
        if self._match_any(q, [r"overview", r"total\s+reports", r"how\s+many"]):
            return AIIntent.OVERVIEW
        return AIIntent.UNKNOWN

    @staticmethod
    def _match_any(text: str, patterns: list[str]) -> bool:
        return any(re.search(p, text) for p in patterns)


# ---------------------------------------------------------------------------
# Rule-based explanation generator (offline default)
# ---------------------------------------------------------------------------


class RuleBasedExplainer:
    """Generates grounded, evidence-based explanations without an LLM."""

    def drug_list(self, drugs: list[dict[str, Any]], limit: int = 5) -> str:
        if not drugs:
            return "No drug data is currently available."
        lines = [
            f"Based on the LifeSci Sentinel dataset, the top {len(drugs[:limit])} "
            "drugs by reported volume are:"
        ]
        for d in drugs[:limit]:
            lines.append(
                f"• {d['drug_name']}: {d['total_reports']} reports, "
                f"{d['serious_reports']} serious "
                f"({d['serious_rate']*100:.1f}% serious rate), "
                f"risk {d['risk']['risk_level']}"
            )
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def drug_profile(
        self, d: Optional[dict[str, Any]], reactions: list[dict[str, Any]]
    ) -> str:
        if not d:
            return "No data found for that drug."
        top_reactions = ", ".join(
            f"{r['reaction_name']} ({r['count']})" for r in reactions[:5]
        ) or "none"
        lines = [
            f"{d['drug_name']} safety profile:",
            f"• Report count: {d['total_reports']}",
            f"• Serious reports: {d['serious_reports']}",
            f"• Serious rate: {d['serious_rate']*100:.1f}%",
            f"• Priority score: {d['priority_score']:.2f} "
            f"({d['priority_level']})",
            f"• Risk level: {d['risk']['risk_level']}",
            f"• Top reactions: {top_reactions}",
        ]
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def reaction_list(self, reactions: list[dict[str, Any]]) -> str:
        if not reactions:
            return "No reaction data is currently available."
        lines = ["Top reactions in the dataset:"]
        for r in reactions[:5]:
            lines.append(
                f"• {r['reaction_name']}: {r['total_reports']} reports "
                f"across {r['affected_drugs']} drugs"
            )
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def signals(self, signals: list[dict[str, Any]], limit: int = 5) -> str:
        if not signals:
            return "No safety signals currently meet the configured thresholds."
        lines = [
            "Current analytical safety signals (drug-reaction pairs) "
            "requiring further investigation:"
        ]
        for s in signals[:limit]:
            lines.append(
                f"• {s['drug']} / {s['reaction']}: {s['reports']} reports, "
                f"serious rate {s['serious_rate']*100:.1f}%, "
                f"priority {s['priority_score']:.2f}, risk {s['risk_level']}"
            )
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def signal_why(self, inv: Optional[dict[str, Any]]) -> str:
        if not inv:
            return "No signal found for that drug/reaction combination."
        lines = [
            f"{inv['drug']} is currently classified as {inv['risk_level']} "
            "priority based on:",
            f"• Report count: {inv['reports']}",
            f"• Serious reports: {inv['serious_reports']}",
            f"• Serious rate: {inv['serious_rate']*100:.1f}%",
            f"• Priority score: {inv['priority_score']:.2f}",
        ]
        if inv.get("rationale"):
            lines.append("Rationale:")
            for r in inv["rationale"][:5]:
                lines.append(f"  - {r}")
        lines.append(
            "This is an analytical signal for further investigation and does "
            "not establish causality."
        )
        return "\n".join(lines)

    def compare(
        self,
        drug_a: Optional[dict[str, Any]],
        drug_b: Optional[dict[str, Any]],
    ) -> str:
        if not drug_a or not drug_b:
            return "One or both drugs were not found in the dataset."
        lines = [
            f"Safety profile comparison: {drug_a['drug_name']} vs {drug_b['drug_name']}"
        ]
        for tag, d in (("A", drug_a), ("B", drug_b)):
            lines.append(
                f"[{tag}] {d['drug_name']}: {d['total_reports']} reports, "
                f"{d['serious_reports']} serious "
                f"({d['serious_rate']*100:.1f}%), priority "
                f"{d['priority_score']:.2f}, risk {d['risk']['risk_level']}"
            )
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def trends(self, question: str, overview: dict[str, Any]) -> str:
        pts = overview.get("trends", [])
        if not pts:
            return "No reporting trend data is currently available."
        total = sum(p["total_reports"] for p in pts)
        lines = [
            f"Reporting over time: {len(pts)} monthly periods, "
            f"{total} total reports.",
            "Recent months (most recent first):",
        ]
        for p in pts[-5:]:
            lines.append(
                f"• {p['month_name']} {p['year']}: {p['total_reports']} reports "
                f"({p['serious_reports']} serious)"
            )
        lines.append(DISCLAIMER)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Optional LLM integration (enhances explanation, never source of truth)
# ---------------------------------------------------------------------------


class LLMEnhancer:
    """Optional OpenAI-compatible LLM wrapper. Pure enhancement."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.enabled = bool(self.api_key)

    def enhance(self, answer: str, evidence: list[dict[str, Any]]) -> str:
        """Optionally rewrite the grounded answer with the LLM.

        The evidence (trusted numbers) is passed in so the LLM cannot invent
        statistics. On any failure, the original grounded answer is returned.
        """
        if not self.enabled:
            return answer
        try:
            import httpx

            prompt = (
                "You are an analytical decision-support assistant. Restate the "
                "following answer concisely and professionally. Do NOT add any "
                "numbers or facts beyond what is provided. Data basis:\n"
                f"{evidence}\n\nAnswer:\n{answer}"
            )
            resp = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "temperature": 0.2,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return str(data["choices"][0]["message"]["content"]).strip()
        except Exception:
            return answer


# ---------------------------------------------------------------------------
# Assistant orchestration
# ---------------------------------------------------------------------------


class AIService:
    """Coordinates intent routing, retrieval, and explanation."""

    def __init__(self) -> None:
        self.db = get_database_service()
        self.router = IntentRouter()
        self.explainer = RuleBasedExplainer()
        self.llm = LLMEnhancer()

    def answer(
        self,
        question: str,
        drug: Optional[str] = None,
        reaction: Optional[str] = None,
    ) -> dict[str, Any]:
        intent = self.router.route(question)
        evidence: list[dict[str, Any]] = []
        answer = ""
        source = {
            "type": "database_analytics",
            "description": "PostgreSQL warehouse + analytics layer",
        }

        if intent == AIIntent.DRUG_LIST:
            result = self.db.drug_list(limit=10)
            evidence = result.get("drugs", [])[:5]
            answer = self.explainer.drug_list(evidence)
        elif intent == AIIntent.DRUG_PROFILE:
            target = drug or self._drug_from_question(question)
            detail = self.db.drug_detail(target) if target else None
            reactions = self.db.drug_reactions(target) if target else []
            evidence = [detail] if detail else []
            answer = self.explainer.drug_profile(detail, reactions)
        elif intent == AIIntent.REACTION_LIST:
            result = self.db.reaction_list(limit=10)
            evidence = result.get("reactions", [])[:5]
            answer = self.explainer.reaction_list(evidence)
        elif intent == AIIntent.SIGNALS:
            result = self.db.signals(limit=10)
            evidence = result.get("signals", [])[:5]
            answer = self.explainer.signals(evidence)
        elif intent == AIIntent.SIGNAL_WHY:
            target = self._drug_from_question(question)
            detail = self.db.drug_detail(target) if target else None
            inv = None
            if detail and target:
                reac = self.db.drug_reactions(target)
                top_reaction = reac[0]["reaction_name"] if reac else reaction
                if top_reaction:
                    inv = self.db.signal_detail(target, top_reaction)
            evidence = [inv] if inv else []
            answer = self.explainer.signal_why(inv)
        elif intent == AIIntent.COMPARE:
            a, b = self._compare_drugs(question)
            da = self.db.drug_detail(a) if a else None
            db_ = self.db.drug_detail(b) if b else None
            evidence = [x for x in [da, db_] if x]
            answer = self.explainer.compare(da, db_)
        elif intent == AIIntent.TRENDS:
            overview = self.db.overview()
            evidence = overview.get("trends", [])[-5:]
            answer = self.explainer.trends(question, overview)
        elif intent == AIIntent.OVERVIEW:
            overview = self.db.overview()
            s = overview.get("summary", {})
            evidence = [s]
            answer = (
                f"Executive overview: {s.get('total_reports', 0)} total reports, "
                f"{s.get('total_drugs', 0)} drugs, "
                f"{s.get('total_reactions', 0)} reactions, "
                f"{s.get('serious_reports', 0)} serious "
                f"({s.get('serious_rate', 0)*100:.1f}% serious rate).\n{DISCLAIMER}"
            )
        else:
            overview = self.db.overview()
            s = overview.get("summary", {})
            evidence = [s]
            answer = (
                "I can answer questions about drug safety signals, drug profiles, "
                "reactions, reporting trends, and priorities. For example: "
                "'Which drugs have the highest serious-report rate?'. "
                f"\n\nCurrent snapshot: {s.get('total_reports', 0)} reports, "
                f"{s.get('total_drugs', 0)} drugs, "
                f"{s.get('serious_rate', 0)*100:.1f}% serious rate.\n{DISCLAIMER}"
            )

        enhanced = self.llm.enhance(answer, evidence)
        return {
            "answer": enhanced if self.llm.enabled else answer,
            "evidence": evidence,
            "sources": [source],
            "question": question,
        }

    @staticmethod
    def _drug_from_question(question: str) -> Optional[str]:
        # Handle "why is X ..." / "why was X ..." -> capture X greedily up to a
        # keyword or end-of-clause.
        m = re.search(
            r"\bwhy\s+(?:is|was)\s+"
            r"([A-Za-z][A-Za-z0-9\-]*(?:\s+[A-Za-z][A-Za-z0-9\-]*)*?)"
            r"(?=\s+(?:high|flagged|priority|classified|as)\b|\?|$)",
            question,
            re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()
        # Handle "safety profile of X" / "profile of X" / "about drug X"
        m = re.search(
            r"\b(?:profile\s+of|about|for)\s+(?:the\s+)?(?:drug\s+)?"
            r"([A-Za-z][A-Za-z0-9\-]*(?:\s+[A-Za-z][A-Za-z0-9\-]*)*?)"
            r"(?=\?|$|\s+(?:high|priority|report|safety))",
            question,
            re.IGNORECASE,
        )
        return m.group(1).strip() if m else None

    @staticmethod
    def _compare_drugs(question: str) -> tuple[Optional[str], Optional[str]]:
        m = re.search(r"compare\s+(\w+)\s+and\s+(\w+)", question, re.IGNORECASE)
        if m:
            return m.group(1), m.group(2)
        return None, None


_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
