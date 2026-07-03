import pandas as pd
from src.database.connection import get_connection
from src.utils.logger import logger


def load_dim_date(conn):
    """Loads date dimension data from CSV to the warehouse."""
    logger.info("Starting load for: warehouse.dim_date")
    table_name = "warehouse.dim_date"
    df = pd.read_csv("data/gold/dim_date.csv")

    with conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
        logger.info(f"Cleared {table_name}")

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO warehouse.dim_date
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    int(row["date_key"]),
                    row["date"],
                    int(row["year"]),
                    int(row["month"]),
                    row["month_name"],
                    int(row["quarter"])
                )
            )
    logger.info(f"Successfully loaded {len(df)} records into {table_name}.")


if __name__ == '__main__':
    connection = get_connection()
    try:
        load_dim_date(connection)
        connection.commit()
    finally:
        connection.close()