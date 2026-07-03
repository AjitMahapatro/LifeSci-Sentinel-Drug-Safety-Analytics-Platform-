import pandas as pd
import json
from pathlib import Path
from src.utils.logger import logger

logger.info("Starting Signal Priority Engine.")

# -----------------------------
# Load Features
# -----------------------------

df = pd.read_csv(
    "data/analytics/features.csv"
)

# -----------------------------
# Load Weights
# -----------------------------

with open("config/priority_weights.json") as f:
    weights = json.load(f)

# -----------------------------
# Calculate Priority Score
# -----------------------------

df["priority_score"] = (

    weights["serious_rate"] * df["serious_rate"]

    +

    weights["normalized_reports"] * df["normalized_reports"]

    +

    weights["reaction_diversity"] * df["reaction_diversity_index"]

)

# Convert to percentage

df["priority_score"] = (
    df["priority_score"] * 100
).round(2)

# -----------------------------
# Priority Levels
# -----------------------------

def classify(score):

    if score >= 70:
        return "High"

    elif score >= 40:
        return "Medium"

    else:
        return "Low"

df["priority_level"] = (
    df["priority_score"]
    .apply(classify)
)

# -----------------------------
# Ranking
# -----------------------------

df = df.sort_values(
    "priority_score",
    ascending=False
)

df.insert(
    0,
    "rank",
    range(1, len(df) + 1)
)

# -----------------------------
# Save
# -----------------------------

Path("data/analytics").mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    "data/analytics/priority_scores.csv",
    index=False
)

print(
    df[
        [
            "rank",
            "drug_name",
            "priority_score",
            "priority_level"
        ]
    ].head(20)
)

print("\nSaved priority_scores.csv")

logger.info("Signal Priority Engine completed successfully.")