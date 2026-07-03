import pandas as pd

df = pd.read_csv("data/gold/fact_drug_safety_events.csv")

required_columns = [
    "event_id",
    "drug_key",
    "date_key",
    "serious"
]

for column in required_columns:

    missing = df[column].isnull().sum()

    print(f"{column}: {missing}")