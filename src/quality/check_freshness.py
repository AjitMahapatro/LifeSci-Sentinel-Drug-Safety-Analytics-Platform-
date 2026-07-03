import json
import pandas as pd
from datetime import datetime

CONFIG_PATH = "config/quality_rules.json"
DATA_PATH = "data/gold/fact_drug_safety_events.csv"


def load_quality_rules(config_path):
    """Loads quality check rules from a JSON config file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def get_latest_report_date(data_path):
    """Reads the fact table and returns the most recent report date."""
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date_key"].astype(str), format="%Y%m%d")
    return df["date"].max()


def check_historical_freshness(latest_date, expected_date_str):
    """Validates freshness for a historical dataset."""
    expected_date = pd.Timestamp(expected_date_str)
    difference = (latest_date - expected_date).days
    
    if latest_date == expected_date:
        status = "PASS"
        message = "Historical snapshot validated."
    else:
        status = "WARNING"
        message = f"Expected {expected_date.date()}, but found {latest_date.date()}."
        
    return status, message, difference, expected_date


def check_live_freshness(latest_date, max_delay_days):
    """Validates freshness for a live dataset against today's date."""
    today = pd.Timestamp.today().normalize()
    difference = (today - latest_date).days
    
    if difference <= max_delay_days:
        status = "PASS"
        message = f"Data is fresh. Found delay of {difference} days."
    else:
        status = "WARNING"
        message = f"Data is stale. Delay of {difference} days exceeds max of {max_delay_days}."
        
    return status, message, difference, today


def print_report(mode, latest_date, comparison_date, difference, status, message):
    """Prints a formatted freshness report."""
    print("------ Freshness Report ------")
    print("")
    print(f"Dataset Mode          : {mode.title()}")
    print(f"Latest Report Date    : {latest_date.date()}")
    
    if mode == "historical":
        print(f"Expected Latest Date  : {comparison_date.date()}")
    else: # live
        print(f"Today's Date          : {comparison_date.date()}")
        
    print(f"Difference            : {difference} days")
    print("")
    print(f"Status                : {status}")
    print(message)
    print("------------------------------")


def main():
    """Main function to orchestrate the freshness check."""
    rules = load_quality_rules(CONFIG_PATH)
    latest_date = get_latest_report_date(DATA_PATH)
    
    mode = rules.get("dataset_mode", "live")
    
    if mode == "historical":
        expected_date_str = rules.get("expected_latest_date")
        if not expected_date_str:
            raise ValueError("`expected_latest_date` is required for historical mode.")
        
        status, message, diff, expected_date = check_historical_freshness(
            latest_date, expected_date_str
        )
        print_report(mode, latest_date, expected_date, diff, status, message)

    elif mode == "live":
        max_delay = rules.get("max_allowed_delay_days", 30)
        status, message, diff, today = check_live_freshness(
            latest_date, max_delay
        )
        print_report(mode, latest_date, today, diff, status, message)
        
    else:
        raise ValueError(f"Invalid `dataset_mode`: {mode}. Must be 'historical' or 'live'.")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        print(f"An error occurred: {e}")