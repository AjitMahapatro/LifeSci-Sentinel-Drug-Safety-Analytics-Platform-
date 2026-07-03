import pandas as pd
from pathlib import Path

INPUT_FILE = "data/processed/silver_drug_safety.csv"

GOLD_DIR = Path("data/gold")
GOLD_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

df["event_date"] = pd.to_datetime(
    df["event_date"],
    format="%Y%m%d",
    errors="coerce"
)

dates = pd.DataFrame({
    "date": sorted(df["event_date"].dropna().unique())
})

dates["date_key"] = (
    dates["date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

dates["year"] = dates["date"].dt.year
dates["month"] = dates["date"].dt.month
dates["month_name"] = dates["date"].dt.month_name()
dates["quarter"] = dates["date"].dt.quarter

dim_date = dates[
    [
        "date_key",
        "date",
        "year",
        "month",
        "month_name",
        "quarter"
    ]
]

dim_date.to_csv(
    GOLD_DIR / "dim_date.csv",
    index=False
)

print(dim_date.head())
print(f"\nTotal Dates: {len(dim_date)}")