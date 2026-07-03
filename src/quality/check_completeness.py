import pandas as pd

df = pd.read_csv("data/gold/fact_drug_safety_events.csv")

required_columns = [
    "event_id",
    "drug_key",
    "date_key",
    "serious"
]

print("------ Completeness Report ------")

for column in required_columns:

    total = len(df)

    populated = df[column].notna().sum()

    completeness = (populated / total) * 100

    status = "PASS" if completeness == 100 else "WARNING"

    print(
        f"{column:12} : {completeness:.2f}%   {status}"
    )