import pandas as pd
from src.database.connection import get_connection
from src.utils.logger import logger


def load_fact_drug_safety(conn):
    """Loads drug safety fact data from CSV to the warehouse."""
    logger.info("Starting load for: warehouse.fact_drug_safety_events")
    table_name = "warehouse.fact_drug_safety_events"
    df = pd.read_csv("data/gold/fact_drug_safety_events.csv")

    with conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
        logger.info(f"Cleared {table_name}")

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO warehouse.fact_drug_safety_events
                (event_id, drug_key, date_key, serious)
                VALUES (%s,%s,%s,%s)
                """,
                (
                    row["event_id"],
                    int(row["drug_key"]),
                    int(row["date_key"]),
                    int(row["serious"])
                )
            )
    logger.info(f"Successfully loaded {len(df)} records into {table_name}.")


if __name__ == '__main__':
    connection = get_connection()
    try:
        load_fact_drug_safety(connection)
        connection.commit()
    finally:
        connection.close()