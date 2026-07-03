import pandas as pd
from src.utils.logger import logger
logger.info("Starting drug-reaction pair analysis.")
fact = pd.read_csv(
    "data/gold/fact_drug_safety_events.csv"
)

drug = pd.read_csv(
    "data/gold/dim_drug.csv"
)

reactions = pd.read_csv(
    "data/processed/event_reactions.csv"
)

# Join fact with drug names
drug_events = fact.merge(
    drug,
    on="drug_key",
    how="left"
)
logger.info("Joined fact table with drug dimension.")
# Join with reactions
full_data = drug_events.merge(
    reactions,
    on="event_id",
    how="inner"
)
logger.info("Joined with reaction data.")
print(full_data.head())

print("\nTop Drug-Reaction Pairs\n")

result = (
    full_data
    .groupby(
        ["drug_name", "reaction_name"]
    )
    .size()
    .reset_index(name="count")
    .sort_values(
        "count",
        ascending=False
    )
)

result.to_csv(
    "data/analytics/drug_reaction_patterns.csv",
    index=False
)

print(result.head(20))

print(
    f"\nTotal Drug-Reaction Pairs: {len(result)}"
)
logger.info("Drug-reaction pair analysis finished.")