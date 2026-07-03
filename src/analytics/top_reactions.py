import pandas as pd
from src.utils.logger import logger
logger.info("Analyzing top reactions.")
df = pd.read_csv(
    "data/processed/event_reactions.csv"
)

top_reactions = (
    df["reaction_name"]
    .value_counts()
    .head(10)
)

print(top_reactions)
logger.info("Finished analyzing top reactions.")

top_reactions = (
    df["reaction_name"]
    .value_counts()
    .head(10)
    .reset_index()
)

top_reactions.columns = [
    "reaction_name",
    "count"
]

top_reactions.to_csv(
    "data/analytics/top_reactions.csv",
    index=False
)

print(top_reactions)