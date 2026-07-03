import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from src.utils.logger import logger

logger.info("Starting feature engineering.")

# -----------------------------
# Load Drug Metrics
# -----------------------------

df = pd.read_csv(
    "data/analytics/drug_metrics.csv"
)

# -----------------------------
# Normalize Report Count
# -----------------------------

scaler = MinMaxScaler()

df["normalized_reports"] = scaler.fit_transform(
    df[["total_reports"]]
)

# -----------------------------
# Convert Serious Rate
# -----------------------------

df["serious_rate"] = (
    df["serious_rate"] / 100
)

# -----------------------------
# Reaction Diversity Index
# -----------------------------

df["reaction_diversity_index"] = (
    df["reaction_diversity"] /
    df["total_reports"]
)

df["reaction_diversity_index"] = (
    df["reaction_diversity_index"]
    .fillna(0)
)

# -----------------------------
# Select Final Features
# -----------------------------

features = df[
    [
        "drug_key",
        "drug_name",
        "total_reports",
        "serious_reports",
        "serious_rate",
        "reaction_diversity",
        "normalized_reports",
        "reaction_diversity_index"
    ]
]

# -----------------------------
# Save Output
# -----------------------------

Path("data/analytics").mkdir(
    parents=True,
    exist_ok=True
)

features.to_csv(
    "data/analytics/features.csv",
    index=False
)

print(features.head())

print("\nSaved features.csv")

logger.info("Feature engineering completed successfully.")