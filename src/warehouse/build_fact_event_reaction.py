import pandas as pd
from src.utils.logger import logger
logger.info("Building fact_event_reaction table.")
# Read processed reactions
events = pd.read_csv(
    "data/processed/event_reactions.csv"
)

# Read reaction dimension
dim = pd.read_csv(
    "data/gold/dim_reaction.csv"
)

# Replace reaction names with surrogate keys
fact = events.merge(
    dim,
    on="reaction_name",
    how="left"
)
logger.info("Merged event reactions with dimension to get reaction keys.")

# Keep only warehouse columns
fact = fact[
    ["event_id", "reaction_key"]
]

# Remove duplicate event-reaction pairs
fact = fact.drop_duplicates()

logger.info(f"Fact table contains {len(fact)} unique event-reaction pairs.")
# Save Gold layer
fact.to_csv(
    "data/gold/fact_event_reaction.csv",
    index=False
)
logger.info("Saved fact_event_reaction to gold layer.")
missing_keys = fact['reaction_key'].isna().sum()
logger.warning(f"Missing Reaction Keys: {missing_keys}")