import pandas as pd
import ast
from pathlib import Path

df = pd.read_csv("data/raw/adverse_events.csv")

reaction_rows = []

for _, row in df.iterrows():

    event_id = row["safetyreportid"]

    try:
        reactions = ast.literal_eval(
            str(row["patient.reaction"])
        )

        for reaction in reactions:

            reaction_rows.append(
                {
                    "event_id": event_id,
                    "reaction_name":
                    reaction.get("reactionmeddrapt")
                }
            )

    except Exception:
        pass

reaction_df = pd.DataFrame(reaction_rows)

Path("data/processed").mkdir(
    exist_ok=True,
    parents=True
)

reaction_df.to_csv(
    "data/processed/event_reactions.csv",
    index=False
)

print(reaction_df.head())
print("\nRows:", len(reaction_df))
print(
    "\nUnique Reactions:",
    reaction_df["reaction_name"].nunique()
)