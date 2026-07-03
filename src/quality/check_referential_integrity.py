import pandas as pd
fact = pd.read_csv(
    "data/gold/fact_drug_safety_events.csv"
)

drug = pd.read_csv(
    "data/gold/dim_drug.csv"
)

missing = (
    fact["drug_key"]
    .isin(drug["drug_key"])
).sum()

print(
    f"Missing Drug Keys : {missing}"
)