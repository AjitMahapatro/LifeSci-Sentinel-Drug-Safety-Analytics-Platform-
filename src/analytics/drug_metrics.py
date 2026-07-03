import pandas as pd
import json
from pathlib import Path
from src.utils.logger import logger

# ----------------------------
# Load Configuration
# ----------------------------

with open("config/quality_rules.json") as f:
    quality_rules = json.load(f)

# ----------------------------
# Load Data
# ----------------------------

fact = pd.read_csv(
    "data/gold/fact_drug_safety_events.csv"
)

drug = pd.read_csv(
    "data/gold/dim_drug.csv"
)

event_reactions = pd.read_csv(
    "data/processed/event_reactions.csv"
)

logger.info("Starting drug metrics calculation.")

# ----------------------------
# Business Metrics
# ----------------------------

analysis = (
    fact
    .groupby("drug_key")
    .agg(
        total_reports=("event_id", "count"),
        serious_reports=(
            "serious",
            lambda x: (x == 1).sum()
        )
    )
    .reset_index()
)

analysis["serious_rate"] = (
    analysis["serious_reports"]
    / analysis["total_reports"]
) * 100

# ----------------------------
# Reaction Diversity
# ----------------------------

drug_events = fact.merge(
    drug,
    on="drug_key",
    how="left"
)

full_data = drug_events.merge(
    event_reactions,
    on="event_id",
    how="left"
)

reaction_diversity = (
    full_data
    .groupby("drug_key")["reaction_name"]
    .nunique()
    .reset_index(name="reaction_diversity")
)

analysis = analysis.merge(
    reaction_diversity,
    on="drug_key",
    how="left"
)

analysis["reaction_diversity"] = (
    analysis["reaction_diversity"]
    .fillna(0)
    .astype(int)
)

# ----------------------------
# Add Drug Name
# ----------------------------

analysis = analysis.merge(
    drug,
    on="drug_key",
    how="left"
)

# ----------------------------
# Apply Business Rule
# ----------------------------

min_reports_threshold = quality_rules[
    "min_reports_for_risk_analysis"
]

analysis = analysis[
    analysis["total_reports"] >= min_reports_threshold
]

logger.info(
    f"Filtered drugs with fewer than {min_reports_threshold} reports."
)

# ----------------------------
# Sort
# ----------------------------

analysis = analysis.sort_values(
    "serious_rate",
    ascending=False
)

# ----------------------------
# Save
# ----------------------------

Path("data/analytics").mkdir(
    parents=True,
    exist_ok=True
)

analysis.to_csv(
    "data/analytics/drug_metrics.csv",
    index=False
)

print(
    analysis[
        [
            "drug_name",
            "total_reports",
            "serious_reports",
            "serious_rate",
            "reaction_diversity"
        ]
    ].head(15)
)

print("\nSaved drug_metrics.csv")

logger.info("Drug metrics calculation completed.")