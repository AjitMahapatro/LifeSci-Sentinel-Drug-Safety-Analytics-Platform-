import pandas as pd
from pathlib import Path

INPUT_FILE = "data/processed/silver_drug_safety.csv"

GOLD_DIR = Path("data/gold")
GOLD_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

dim_drug = (
    df["drug_name"]
    .dropna()
    .str.upper()
    .str.strip()
    .str.replace(".", "", regex=False)
    .drop_duplicates()
    .to_frame("drug_name")
)

dim_drug["drug_key"] = range(1, len(dim_drug) + 1)

dim_drug = dim_drug[
    ["drug_key", "drug_name"]
]

dim_drug.to_csv(
    GOLD_DIR / "dim_drug.csv",
    index=False
)

print(dim_drug.head())
print(f"\nTotal Drugs: {len(dim_drug)}")