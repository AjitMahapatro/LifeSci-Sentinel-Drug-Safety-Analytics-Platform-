import pandas as pd

df = pd.read_csv(
    "data/gold/fact_drug_safety_events.csv"
)

duplicates = df["event_id"].duplicated().sum()

print(f"Duplicate Events : {duplicates}")