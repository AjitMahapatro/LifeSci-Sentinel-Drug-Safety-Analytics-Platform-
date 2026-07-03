from src.utils.logger import logger
from src.database.connection import get_connection
from src.database.reset_database import reset_warehouse_tables
from src.database.load_dim_date import load_dim_date
from src.database.load_dim_drug import load_dim_drug
from src.database.load_dim_reaction import load_dim_reaction
from src.database.load_fact_drug_safety import load_fact_drug_safety
from src.database.load_fact_event_reaction import load_fact_event_reaction


def main():
    """
    Orchestrates the entire data warehouse loading process within a single transaction.
    1. Resets all warehouse tables.
    2. Loads all dimension tables.
    3. Loads all fact tables.
    """
    conn = None
    try:
        conn = get_connection()
        logger.info("Successfully connected to the database. Starting ETL load process.")

        # 1. Reset database
        reset_warehouse_tables(conn)

        # 2. Load dimensions
        load_dim_date(conn)
        load_dim_drug(conn)
        load_dim_reaction(conn)

        # 3. Load facts
        load_fact_drug_safety(conn)
        load_fact_event_reaction(conn)

        # 4. Commit transaction
        conn.commit()
        logger.info("ETL load process completed successfully. Transaction committed.")

    except Exception as e:
        logger.error(f"An error occurred during the ETL load process: {e}")
        if conn:
            conn.rollback()
            logger.error("Transaction has been rolled back.")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")


if __name__ == "__main__":
    logger.info("--- Starting Data Warehouse Load ---")
    main()
    logger.info("--- Data Warehouse Load Finished ---")