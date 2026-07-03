import pandas as pd
from src.database.connection import get_connection
from src.utils.logger import logger


def load_fact_event_reaction(conn):
    """Loads event-reaction fact data from CSV to the warehouse."""
    logger.info("Starting load for: warehouse.fact_event_reaction")
    table_name = "warehouse.fact_event_reaction"
    fact = pd.read_csv("data/gold/fact_event_reaction.csv")

    with conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name};")
        logger.info(f"Cleared {table_name}")

        for _, row in fact.iterrows():
            cursor.execute("""
                INSERT INTO warehouse.fact_event_reaction
                (event_id, reaction_key)
                VALUES (%s,%s)
                """,
                (
                    row["event_id"],
                    int(row["reaction_key"])
                )
            )
    logger.info(f"Successfully loaded {len(fact)} records into {table_name}.")


if __name__ == '__main__':
    connection = get_connection()
    try:
        load_fact_event_reaction(connection)
        connection.commit()
    finally:
        connection.close()