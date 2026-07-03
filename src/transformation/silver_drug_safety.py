import pandas as pd
import ast
from pathlib import Path

from src.utils.logger import logger
RAW_FILE = "data/raw/adverse_events.csv"

SILVER_DIR = Path("data/processed")
SILVER_DIR.mkdir(parents=True, exist_ok=True)


def extract_drug_name(drug_text):

    try:

        drug_list = ast.literal_eval(drug_text)

        if isinstance(drug_list, list) and len(drug_list) > 0:

            return drug_list[0].get("medicinalproduct")
    except (ValueError, SyntaxError) as e:
        logger.warning(f"Could not parse drug text: {drug_text}. Error: {e}")
        return None

    return None


logger.info("Starting silver transformation for drug safety data.")
df = pd.read_csv(RAW_FILE)
logger.info(f"Read {len(df)} rows from {RAW_FILE}.")

df["drug_name"] = df["patient.drug"].apply(extract_drug_name)

silver_df = df[
    [
        "safetyreportid",
        "receiptdate",
        "serious",
        "drug_name"
    ]
].copy()

silver_df.rename(
    columns={
        "safetyreportid": "event_id",
        "receiptdate": "event_date"
    },
    inplace=True
)

silver_df.to_csv(
    SILVER_DIR / "silver_drug_safety.csv",
    index=False
)
logger.info(f"Saved {len(silver_df)} rows to silver layer.")
logger.info("Silver transformation finished.")