import argparse
from src.fetchers.alpaca_fetcher import insert_historical_data
from src.fetchers.quiverquant_fetcher import process_congressional_trades
from src.fetchers.yf_fetcher import fetch_yahoo_key_stats
from src.utils.database import connect_to_db
from src.backtesting.backtester import run_portfolio_backtest
from src.backtesting.visualization import plot_portfolio_performance

def setup_database():
    """
    Test database connection to ensure everything is set up correctly.
    """
    try:
        engine = connect_to_db()
        with engine.connect() as conn:  # Use the connection object
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

def run_backtest():
    """
    Run a backtest on a portfolio of stocks with a specified strategy and visualize results.
    """
    portfolio = {
        "AAPL": 0.4,  # 40% allocation
        "MSFT": 0.3,  # 30% allocation
        "GOOGL": 0.2,  # 20% allocation
        "TSLA": 0.1,  # 10% allocation
    }
    start_date = "2020-01-01"
    end_date = "2022-12-31"
    strategy_name = "MovingAverageCrossover"  # Change this to test other strategies

    print("Running backtest...")
    results = run_portfolio_backtest(portfolio, start_date, end_date, strategy_name)
    print("Backtest completed. Generating visualization...")

    plot_portfolio_performance(results, portfolio)
    print("Visualization complete.")

def main():
    """
    Main entry point for the Ishara project.
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
    parser.add_argument(
        "--run-backtest", action="store_true", help="Run portfolio backtesting and visualization"
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
    if args.run_backtest:
        run_backtest()

if __name__ == "__main__":
    main()
