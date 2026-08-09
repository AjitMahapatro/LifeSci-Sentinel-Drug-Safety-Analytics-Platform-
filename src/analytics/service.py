"""Reusable analytics service for LifeSci Sentinel.

This module centralizes the analytical computations used across the project
(drug metrics, priority scoring, risk classification, reporting trends) so that
the FastAPI layer, the React frontend, and the AI assistant all consume the
same, verified business logic.

It reuses the EXISTING methodology found in the repository's analytics scripts
and config files. It does NOT redefine or duplicate the existing priority engine
methodology; risk classification is a transparent, configurable OVERLAY on top
of the existing priority score.

NOTE: These are analytical decision-support metrics. They do not establish
causality, clinical risk, or a regulatory conclusion.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Paths are relative to the repository root. The FastAPI app runs from the
# repository root, so these resolve consistently.
ROOT = Path(__file__).resolve().parent.parent.parent

GOLD_DIR = ROOT / "data" / "gold"
ANALYTICS_DIR = ROOT / "data" / "analytics"
CONFIG_DIR = ROOT / "config"

FACT_DRUG_SAFETY = GOLD_DIR / "fact_drug_safety_events.csv"
DIM_DRUG = GOLD_DIR / "dim_drug.csv"
DIM_REACTION = GOLD_DIR / "dim_reaction.csv"
DIM_DATE = GOLD_DIR / "dim_date.csv"
FACT_EVENT_REACTION = GOLD_DIR / "fact_event_reaction.csv"

FEATURES_CSV = ANALYTICS_DIR / "features.csv"
PRIORITY_CSV = ANALYTICS_DIR / "priority_scores.csv"
DRUG_METRICS_CSV = ANALYTICS_DIR / "drug_metrics.csv"
DRUG_REACTION_PATTERNS_CSV = ANALYTICS_DIR / "drug_reaction_patterns.csv"

PRIORITY_WEIGHTS_JSON = CONFIG_DIR / "priority_weights.json"
RISK_RULES_JSON = CONFIG_DIR / "risk_rules.json"
QUALITY_RULES_JSON = CONFIG_DIR / "quality_rules.json"

# Serious flag in the fact table: 1 = serious, 2 = non-serious (FAERS/OpenFDA).
SERIOUS_FLAG = 1


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r") as f:
        return json.load(f)


def load_priority_weights() -> dict[str, float]:
    return load_json(PRIORITY_WEIGHTS_JSON)


def load_risk_rules() -> dict[str, Any]:
    return load_json(RISK_RULES_JSON)


def load_quality_rules() -> dict[str, Any]:
    return load_json(QUALITY_RULES_JSON)


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------


def serious_rate(serious_reports: int, total_reports: int) -> float:
    """Return serious rate as a ratio (0..1). Returns 0.0 for zero reports."""
    if total_reports <= 0:
        return 0.0
    return serious_reports / total_reports


def serious_rate_pct(serious_reports: int, total_reports: int) -> float:
    """Return serious rate as a percentage (0..100)."""
    return serious_rate(serious_reports, total_reports) * 100


def _serious_rate_series(serious_series: pd.Series, total_series: pd.Series) -> pd.Series:
    """Vectorized serious-rate ratio (0..1) for two integer series."""
    total = total_series.astype(float)
    serious = serious_series.astype(float)
    result = pd.Series(0.0, index=total.index)
    mask = total > 0
    result.loc[mask] = serious.loc[mask] / total.loc[mask]
    return result


def drug_metrics_from_fact(fact: pd.DataFrame, drug: pd.DataFrame) -> pd.DataFrame:
    """Compute per-drug metrics following the existing drug_metrics.py logic.

    Parameters
    ----------
    fact : pd.DataFrame
        The fact_drug_safety_events table (event_id, drug_key, date_key, serious).
    drug : pd.DataFrame
        The dim_drug dimension (drug_key, drug_name).

    Returns
    -------
    pd.DataFrame
        Columns: drug_key, drug_name, total_reports, serious_reports, serious_rate.
    """
    analysis = (
        fact.groupby("drug_key")
        .agg(
            total_reports=("event_id", "count"),
            serious_reports=("serious", lambda x: int((x == SERIOUS_FLAG).sum())),
        )
        .reset_index()
    )
    analysis["serious_rate"] = _serious_rate_series(
        analysis["serious_reports"], analysis["total_reports"]
    )
    analysis = analysis.merge(
        drug[["drug_key", "drug_name"]], on="drug_key", how="left"
    )
    return analysis


# ---------------------------------------------------------------------------
# Priority score & existing classification (mirrors signal_priority.py)
# ---------------------------------------------------------------------------


def priority_level(score: float) -> str:
    """Return the EXISTING label (High/Medium/Low) for backward compatibility.

    This reproduces the exact thresholds used in signal_priority.py:
        >= 70 -> "High", >= 40 -> "Medium", else "Low".
    """
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def compute_priority_features(features: pd.DataFrame) -> pd.DataFrame:
    """Given a features frame, compute priority_score and existing priority_level.

    Mirrors signal_priority.py exactly (weights, *100, round(2), ranking).
    """
    weights = load_priority_weights()
    df = features.copy()
    df["priority_score"] = (
        weights["serious_rate"] * df["serious_rate"]
        + weights["normalized_reports"] * df["normalized_reports"]
        + weights["reaction_diversity"] * df["reaction_diversity_index"]
    ) * 100
    df["priority_score"] = df["priority_score"].round(2)
    df["priority_level"] = df["priority_score"].apply(priority_level)
    df = df.sort_values("priority_score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


# ---------------------------------------------------------------------------
# NEW: Configurable risk classification (overlay, does not alter existing)
# ---------------------------------------------------------------------------


def classify_risk(
    priority_score: float,
    serious_rate_value: float,
    total_reports: int,
    rules: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Classify a drug/signal into LOW / MODERATE / HIGH / CRITICAL.

    This is a transparent, configurable overlay on the existing priority engine.
    It consumes priority_score (from the existing engine) plus serious rate and
    report volume. It does NOT modify the existing priority_scores.csv output.

    Parameters
    ----------
    priority_score : float
        The existing 0-100 priority score.
    serious_rate_value : float
        Serious rate as a ratio (0..1).
    total_reports : int
        Number of reports for the drug.
    rules : dict, optional
        Risk rules; if omitted, loaded from config/risk_rules.json.

    Returns
    -------
    dict
        {"risk_level": ..., "rationale": [list of reason strings]}
    """
    if rules is None:
        rules = load_risk_rules()

    min_reports = rules.get("min_reports_for_risk_analysis", 5)
    p_thresh = rules.get("priority_based_risk_thresholds", {})
    s_thresh = rules.get("serious_rate_thresholds", {})

    rationale: list[str] = [
        f"Priority score {priority_score:.2f} based on existing weighted engine"
    ]

    if priority_score >= p_thresh.get("critical_min", 90):
        level = "CRITICAL"
    elif priority_score >= p_thresh.get("high_min", 70):
        level = "HIGH"
    elif priority_score >= p_thresh.get("moderate_min", 40):
        level = "MODERATE"
    else:
        level = "LOW"

    if serious_rate_value >= s_thresh.get("critical_min", 0.9):
        if level in ("LOW", "MODERATE"):
            level = "HIGH"
            rationale.append("Elevated serious-report proportion (>=90%)")
    elif serious_rate_value >= s_thresh.get("high_min", 0.7):
        if level == "LOW":
            level = "MODERATE"
            rationale.append("Elevated serious-report proportion (>=70%)")

    if total_reports < min_reports:
        rationale.append(
            f"Report volume below risk-analysis threshold ({min_reports} reports)"
        )

    rationale.append(
        "This is an analytical risk classification requiring further investigation; "
        "it does not establish causality."
    )
    return {"risk_level": level, "rationale": rationale}


# ---------------------------------------------------------------------------
# Trend computation
# ---------------------------------------------------------------------------


def reporting_trends(
    fact: pd.DataFrame, dim_date: pd.DataFrame
) -> list[dict[str, Any]]:
    """Return monthly report volume over time.

    Parameters
    ----------
    fact : pd.DataFrame
        fact_drug_safety_events containing date_key.
    dim_date : pd.DataFrame
        dim_date dimension (date_key -> year, month, month_name).

    Returns
    -------
    list[dict]
        Sorted by date_key ascending: {date_key, year, month, month_name,
        total_reports, serious_reports, serious_rate}.
    """
    if fact.empty:
        return []

    merged = fact.merge(dim_date, on="date_key", how="left")
    grouped = (
        merged.groupby(["date_key", "year", "month", "month_name"])
        .agg(
            total_reports=("event_id", "count"),
            serious_reports=("serious", lambda x: int((x == SERIOUS_FLAG).sum())),
        )
        .reset_index()
    )
    grouped["serious_rate"] = _serious_rate_series(
        grouped["serious_reports"], grouped["total_reports"]
    )
    grouped = grouped.sort_values("date_key").reset_index(drop=True)
    raw_records = grouped.astype(object).to_dict(orient="records")
    records: list[dict[str, Any]] = [
        {str(k): v for k, v in rec.items()} for rec in raw_records
    ]
    return records


# ---------------------------------------------------------------------------
# Overview aggregation
# ---------------------------------------------------------------------------


def overview_summary(
    fact: pd.DataFrame, drug: pd.DataFrame, reaction: pd.DataFrame
) -> dict[str, Any]:
    """Compute the high-level executive overview metrics."""
    total_reports = int(len(fact))
    total_drugs = int(drug["drug_key"].nunique())
    total_reactions = int(reaction["reaction_key"].nunique())
    serious_reports = int((fact["serious"] == SERIOUS_FLAG).sum())
    return {
        "total_reports": total_reports,
        "total_drugs": total_drugs,
        "total_reactions": total_reactions,
        "serious_reports": serious_reports,
        "serious_rate": round(serious_rate(serious_reports, total_reports), 4),
    }


# ---------------------------------------------------------------------------
# Data loaders (thin reusable wrappers over the existing gold layer)
# ---------------------------------------------------------------------------


def load_fact() -> pd.DataFrame:
    df = pd.read_csv(FACT_DRUG_SAFETY)
    df["drug_key"] = df["drug_key"].astype(int)
    df["date_key"] = df["date_key"].astype(int)
    df["serious"] = df["serious"].astype(int)
    return df


def load_dim_drug() -> pd.DataFrame:
    return pd.read_csv(DIM_DRUG)


def load_dim_reaction() -> pd.DataFrame:
    return pd.read_csv(DIM_REACTION)


def load_dim_date() -> pd.DataFrame:
    return pd.read_csv(DIM_DATE)


def load_fact_event_reaction() -> pd.DataFrame:
    return pd.read_csv(FACT_EVENT_REACTION)


def load_features() -> pd.DataFrame:
    return pd.read_csv(FEATURES_CSV)


def load_priority_scores() -> pd.DataFrame:
    return pd.read_csv(PRIORITY_CSV)


def load_drug_metrics() -> pd.DataFrame:
    return pd.read_csv(DRUG_METRICS_CSV)


def load_drug_reaction_patterns() -> pd.DataFrame:
    return pd.read_csv(DRUG_REACTION_PATTERNS_CSV)
