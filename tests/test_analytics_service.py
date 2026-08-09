"""Unit tests for the reusable analytics service.

These tests cover pure functions that do not require a database connection:
serious-rate calculation, priority scoring, risk classification, and the
overview summary aggregation.
"""

from __future__ import annotations

import pytest
import pandas as pd

from src.analytics import service


# ---------------------------------------------------------------------------
# Serious rate
# ---------------------------------------------------------------------------


def test_serious_rate_basic():
    assert service.serious_rate(4, 10) == pytest.approx(0.4)


def test_serious_rate_zero_reports_returns_zero():
    assert service.serious_rate(0, 0) == 0.0


def test_serious_rate_no_serious():
    assert service.serious_rate(0, 10) == 0.0


def test_serious_rate_pct():
    assert service.serious_rate_pct(4, 10) == pytest.approx(40.0)


# ---------------------------------------------------------------------------
# Priority score (existing methodology)
# ---------------------------------------------------------------------------


def test_priority_level_boundaries():
    assert service.priority_level(70.0) == "High"
    assert service.priority_level(69.99) == "Medium"
    assert service.priority_level(40.0) == "Medium"
    assert service.priority_level(39.99) == "Low"


def test_compute_priority_features_matches_weights():
    # Build a small features frame with known values.
    df = pd.DataFrame(
        {
            "drug_key": [1],
            "drug_name": ["TEST"],
            "total_reports": [10],
            "serious_reports": [5],
            "serious_rate": [0.5],
            "reaction_diversity": [3],
            "normalized_reports": [0.5],
            "reaction_diversity_index": [0.3],
        }
    )
    result = service.compute_priority_features(df)
    weights = service.load_priority_weights()
    expected = (
        weights["serious_rate"] * 0.5
        + weights["normalized_reports"] * 0.5
        + weights["reaction_diversity"] * 0.3
    ) * 100
    assert result.iloc[0]["priority_score"] == pytest.approx(round(expected, 2))
    assert "rank" in result.columns
    assert result.iloc[0]["rank"] == 1


# ---------------------------------------------------------------------------
# Risk classification (configurable overlay)
# ---------------------------------------------------------------------------


def test_classify_risk_high_priority():
    rules = service.load_risk_rules()
    result = service.classify_risk(
        priority_score=85.0,
        serious_rate_value=0.8,
        total_reports=20,
        rules=rules,
    )
    assert result["risk_level"] == "HIGH"
    assert isinstance(result["rationale"], list)
    assert len(result["rationale"]) > 0


def test_classify_risk_critical():
    rules = service.load_risk_rules()
    result = service.classify_risk(
        priority_score=95.0, serious_rate_value=0.95, total_reports=30, rules=rules
    )
    assert result["risk_level"] == "CRITICAL"


def test_classify_risk_low():
    rules = service.load_risk_rules()
    result = service.classify_risk(
        priority_score=10.0, serious_rate_value=0.2, total_reports=10, rules=rules
    )
    assert result["risk_level"] == "LOW"


def test_classify_risk_serious_rate_escalation():
    # Low priority score but very high serious rate should escalate.
    rules = service.load_risk_rules()
    result = service.classify_risk(
        priority_score=15.0, serious_rate_value=0.95, total_reports=20, rules=rules
    )
    assert result["risk_level"] == "HIGH"


def test_classify_risk_below_min_reports_adds_rationale():
    rules = service.load_risk_rules()
    result = service.classify_risk(
        priority_score=50.0, serious_rate_value=0.5, total_reports=2, rules=rules
    )
    assert any("below risk-analysis threshold" in r for r in result["rationale"])


# ---------------------------------------------------------------------------
# Overview summary
# ---------------------------------------------------------------------------


def test_overview_summary_counts():
    fact = pd.DataFrame(
        {
            "event_id": ["e1", "e2", "e3"],
            "drug_key": [1, 1, 2],
            "date_key": [20200101, 20200101, 20200102],
            "serious": [1, 2, 1],
        }
    )
    drug = pd.DataFrame({"drug_key": [1, 2], "drug_name": ["A", "B"]})
    reaction = pd.DataFrame({"reaction_key": [10, 11], "reaction_name": ["R1", "R2"]})
    summary = service.overview_summary(fact, drug, reaction)
    assert summary["total_reports"] == 3
    assert summary["total_drugs"] == 2
    assert summary["total_reactions"] == 2
    assert summary["serious_reports"] == 2
    # overview_summary rounds serious_rate to 4 decimal places.
    assert summary["serious_rate"] == pytest.approx(round(2 / 3, 4))


# ---------------------------------------------------------------------------
# Reporting trends
# ---------------------------------------------------------------------------


def test_reporting_trends_empty():
    fact = pd.DataFrame(columns=["event_id", "drug_key", "date_key", "serious"])
    dim_date = pd.DataFrame(columns=["date_key", "year", "month", "month_name"])
    assert service.reporting_trends(fact, dim_date) == []


def test_reporting_trends_groups_by_date():
    fact = pd.DataFrame(
        {
            "event_id": ["e1", "e2", "e3"],
            "drug_key": [1, 1, 1],
            "date_key": [20200101, 20200101, 20200102],
            "serious": [1, 2, 1],
        }
    )
    dim_date = pd.DataFrame(
        {
            "date_key": [20200101, 20200102],
            "year": [2020, 2020],
            "month": [1, 1],
            "month_name": ["January", "January"],
        }
    )
    trends = service.reporting_trends(fact, dim_date)
    assert len(trends) == 2
    assert trends[0]["total_reports"] == 2
    assert trends[1]["total_reports"] == 1
