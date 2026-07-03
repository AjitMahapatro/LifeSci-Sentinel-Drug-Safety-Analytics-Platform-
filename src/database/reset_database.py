import psycopg2
from src.database.connection import get_connection
from src.utils.logger import logger


def reset_warehouse_tables(conn):
    """
    Truncates all data warehouse tables in the correct dependency order.
    """
    logger.info("Resetting all warehouse tables.")
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            TRUNCATE TABLE
                warehouse.fact_drug_safety_events,
                warehouse.fact_event_reaction,
                warehouse.dim_date,
                warehouse.dim_drug,
                warehouse.dim_reaction
            RESTART IDENTITY CASCADE;
            """)
        logger.info("All warehouse tables have been truncated and reset.")
    except (Exception, psycopg2.DatabaseError) as e:
        logger.error(f"Error resetting warehouse tables: {e}")
        raise


if __name__ == '__main__':
    connection = get_connection()
    reset_warehouse_tables(connection)
    connection.commit()
    connection.close()