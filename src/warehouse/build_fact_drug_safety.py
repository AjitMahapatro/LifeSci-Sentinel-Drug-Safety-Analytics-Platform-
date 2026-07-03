import pandas as pd
from pathlib import Path
from src.utils.logger import logger

silver = pd.read_csv(
    "data/processed/silver_drug_safety.csv"
)

dim_drug = pd.read_csv(
    "data/gold/dim_drug.csv"
)

logger.info("Building fact_drug_safety_events table.")
# standardize names exactly like dim_drug
silver["drug_name"] = (
    silver["drug_name"]
    .str.upper()
    .str.strip()
    .str.replace(".", "", regex=False)
)
logger.info("Standardized drug names.")

fact = silver.merge(
    dim_drug,
    on="drug_name",
    how="left"
)

fact["event_date"] = pd.to_datetime(
    fact["event_date"],
    format="%Y%m%d",
    errors="coerce"
)
logger.info("Processed event dates.")

fact["date_key"] = (
    fact["event_date"]
    .dt.strftime("%Y%m%d")
)

fact_table = fact[
    [
        "event_id",
        "drug_key",
        "date_key",
        "serious"
    ]
]

Path("data/gold").mkdir(
    parents=True,
    exist_ok=True
)

fact_table.to_csv(
    "data/gold/fact_drug_safety_events.csv",
    index=False
)
logger.info(f"Saved fact table with {len(fact_table)} rows to gold layer.")
missing_keys = fact_table["drug_key"].isna().sum()
logger.warning(f"Missing Drug Keys: {missing_keys}")
logger.info("Finished building fact_drug_safety_events.")