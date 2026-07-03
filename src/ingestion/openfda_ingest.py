import requests
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import json
from src.utils.logger import logger

load_dotenv()

API_KEY = os.getenv("FDA_API_KEY")

with open("config/api.json") as f:
    api_config = json.load(f)

BASE_URL = api_config["base_url"]

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_adverse_events(limit=api_config["limit"]):
    logger.info(f"Fetching {limit} records from OpenFDA API.")

    params = {
        "limit": limit,
        "api_key": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        logger.info(f"API request successful with status code {response.status_code}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise


def save_raw_data(data):
    df = pd.json_normalize(data["results"])

    output_file = OUTPUT_DIR / "adverse_events.csv"

    df.to_csv(output_file, index=False)

    logger.info(f"Saved {len(df)} records to {output_file}")


if __name__ == "__main__":
    logger.info("Starting OpenFDA data ingestion process.")
    data = fetch_adverse_events()
    save_raw_data(data)
    logger.info("OpenFDA data ingestion process finished.")