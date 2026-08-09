"""Unit tests for the grounded AI assistant.

These tests cover the INTENT ROUTER (a pure, deterministic state machine) and
the RULE-BASED EXPLAINER output formatting. They do not require a database or
network access. The LLM is intentionally not exercised here.
"""

from __future__ import annotations

import pytest

from api.services.ai_service import AIIntent, IntentRouter, RuleBasedExplainer


@pytest.fixture
def router() -> IntentRouter:
    return IntentRouter()


@pytest.fixture
def explainer() -> RuleBasedExplainer:
    return RuleBasedExplainer()


# ---------------------------------------------------------------------------
# Intent router
# ---------------------------------------------------------------------------


def test_drug_list_intent(router: IntentRouter):
    assert router.route("Which drugs have the highest serious-report rate?") == (
        AIIntent.DRUG_LIST
    )


def test_drug_profile_intent(router: IntentRouter):
    assert router.route("Show me the safety profile of LIPITOR") == (
        AIIntent.DRUG_PROFILE
    )


def test_reaction_list_intent(router: IntentRouter):
    assert router.route("What are the top reactions?") == AIIntent.REACTION_LIST


def test_signal_intent(router: IntentRouter):
    assert router.route("Which drugs currently have high-priority signals?") == (
        AIIntent.SIGNALS
    )


def test_signal_why_intent(router: IntentRouter):
    assert router.route("Why is HUMIRA high priority?") == AIIntent.SIGNAL_WHY


def test_compare_intent(router: IntentRouter):
    assert router.route("Compare LIPITOR and HUMIRA") == AIIntent.COMPARE


def test_trends_intent(router: IntentRouter):
    assert router.route("What changed in reporting over time?") == AIIntent.TRENDS


def test_overview_intent(router: IntentRouter):
    assert router.route("How many total reports are there?") == AIIntent.OVERVIEW


def test_unknown_intent(router: IntentRouter):
    assert router.route("What is the weather today?") == AIIntent.UNKNOWN


# ---------------------------------------------------------------------------
# Rule-based explainer (grounded, no invented stats)
# ---------------------------------------------------------------------------


def test_drug_list_explainer_uses_provided_data(explainer: RuleBasedExplainer):
    drugs = [
        {
            "drug_name": "A",
            "total_reports": 10,
            "serious_reports": 5,
            "serious_rate": 0.5,
            "risk": {"risk_level": "HIGH"},
        }
    ]
    text = explainer.drug_list(drugs, limit=1)
    assert "A" in text
    assert "10" in text
    assert "5" in text
    assert "HIGH" in text


def test_drug_list_explainer_empty(explainer: RuleBasedExplainer):
    text = explainer.drug_list([])
    assert "No drug data" in text


def test_signal_why_includes_disclaimer(explainer: RuleBasedExplainer):
    inv = {
        "drug": "X",
        "reaction": "Y",
        "reports": 10,
        "serious_reports": 8,
        "serious_rate": 0.8,
        "priority_score": 75.0,
        "risk_level": "HIGH",
        "rationale": ["reason 1"],
    }
    text = explainer.signal_why(inv)
    assert "X" in text
    assert "HIGH" in text
    assert "does not establish causality" in text


def test_compare_explainer(explainer: RuleBasedExplainer):
    a = {
        "drug_name": "A",
        "total_reports": 5,
        "serious_reports": 2,
        "serious_rate": 0.4,
        "priority_score": 40.0,
        "risk": {"risk_level": "MODERATE"},
    }
    b = {
        "drug_name": "B",
        "total_reports": 8,
        "serious_reports": 3,
        "serious_rate": 0.375,
        "priority_score": 44.0,
        "risk": {"risk_level": "MODERATE"},
    }
    text = explainer.compare(a, b)
    assert "A vs B" in text
    assert "[A]" in text
    assert "[B]" in text


def test_empty_compare_explainer(explainer: RuleBasedExplainer):
    text = explainer.compare(None, None)
    assert "not found" in text
