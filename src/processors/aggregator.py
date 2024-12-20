import pandas as pd
from src.utils.database import connect_to_db

def aggregate_data():
    conn = connect_to_db()
    market_query = "SELECT * FROM historical_market_data"
    alt_query = "SELECT * FROM alternative_data"

    market_data = pd.read_sql(market_query, conn)
    alt_data = pd.read_sql(alt_query, conn)

    merged = pd.merge(market_data, alt_data, on=["symbol", "datetime"], how="left")
    merged.to_csv("data/processed/aggregated_data.csv", index=False)
    print("Aggregated data saved.")
    