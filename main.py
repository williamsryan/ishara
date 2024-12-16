import argparse
from src.fetchers.alpaca_fetcher import insert_historical_data
from src.fetchers.quiverquant_fetcher import process_congressional_trades
from src.fetchers.yf_fetcher import fetch_yahoo_key_stats
from src.utils.database import connect_to_db

def setup_database():
    """
    Test database connection to ensure everything is set up correctly.
    """
    try:
        conn = connect_to_db()
        conn.close()
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

def fetch_alpaca_data():
    """
    Fetch historical stock data from Alpaca and store it in the database.
    """
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]  # Example symbols
    insert_historical_data(symbols, "2020-01-01", "2022-12-31")

def fetch_yahoo_finance_data():
    """
    Fetch alternative key statistics data from Yahoo Finance and store it in the database.
    """
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    data = fetch_yahoo_key_stats(symbols)
    print(f"Inserted {len(data)} rows into alternative_data table.")

def fetch_quiverquant_data():
    """
    Fetch congressional trades data from QuiverQuant and store it in the database.
    """
    data = process_congressional_trades()
    print("Fetched and stored QuiverQuant data.")

def main():
    """
    Main entrypoint for the Ishara project.
    """
    parser = argparse.ArgumentParser(description="Ishara Data Pipeline Entrypoint")
    parser.add_argument(
        "--setup-db", action="store_true", help="Set up and verify database connectivity"
    )
    parser.add_argument(
        "--fetch-alpaca", action="store_true", help="Fetch and store historical stock data from Alpaca"
    )
    parser.add_argument(
        "--fetch-quiverquant", action="store_true", help="Fetch and store alternative data from QuiverQuant"
    )
    parser.add_argument(
        "--fetch-yahoo", action="store_true", help="Fetch and store alternative data from Yahoo Finance"
    )
    args = parser.parse_args()

    if args.setup_db:
        setup_database()
    if args.fetch_alpaca:
        fetch_alpaca_data()
    if args.fetch_quiverquant:
        fetch_quiverquant_data()
    if args.fetch_yahoo:
        fetch_yahoo_finance_data()

if __name__ == "__main__":
    main()
    