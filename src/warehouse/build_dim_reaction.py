import pandas as pd

# Read processed reaction data
df = pd.read_csv(
    "data/processed/event_reactions.csv"
)

# Keep unique reactions
dim = (
    df[["reaction_name"]]
    .drop_duplicates()
    .sort_values("reaction_name")
    .reset_index(drop=True)
)

# Generate surrogate keys
dim["reaction_key"] = range(1, len(dim) + 1)

# Reorder columns
dim = dim[
    ["reaction_key", "reaction_name"]
]

# Save Gold layer
dim.to_csv(
    "data/gold/dim_reaction.csv",
    index=False
)

print(dim.head())

print()

print(f"Total Reactions: {len(dim)}")