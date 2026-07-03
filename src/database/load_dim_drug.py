import pandas as pd
from src.database.connection import get_connection
from src.utils.logger import logger


def load_dim_drug(conn):
    """Loads drug dimension data from CSV to the warehouse."""
    logger.info("Starting load for: warehouse.dim_drug")
    table_name = "warehouse.dim_drug"
    df = pd.read_csv("data/gold/dim_drug.csv")

    with conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
        logger.info(f"Cleared {table_name}")

        for _, row in df.iterrows():
            cursor.execute(
                f"""
                INSERT INTO warehouse.dim_drug
                (drug_key, drug_name)
                VALUES (%s,%s)
                """,
                (
                    int(row["drug_key"]),
                    row["drug_name"]
                )
            )

    logger.info(f"Successfully loaded {len(df)} records into {table_name}.")


if __name__ == '__main__':
    connection = get_connection()
    try:
        load_dim_drug(connection)
        connection.commit()
    finally:
        connection.close()