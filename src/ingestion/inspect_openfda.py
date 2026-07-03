import pandas as pd
from src.utils.logger import logger

logger.info("Inspecting raw adverse_events.csv data.")
df = pd.read_csv("data/raw/adverse_events.csv")

logger.info(f"Shape: {df.shape}")

logger.info(f"Columns: {df.columns.tolist()}")

logger.info("Data Types:\n" + df.dtypes.to_string())

null_percentages = (df.isnull().mean() * 100).sort_values(ascending=False).head(20)
logger.info("Null Percentage (Top 20):\n" + null_percentages.to_string())

# The print statements below are kept for interactive analysis summary
print("\n--- Data Inspection Summary ---")
print(f"\nShape: {df.shape}")
print("\nNull Percentage (Top 20):")
print(null_percentages)