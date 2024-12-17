import argparse
from src.fetchers.alpaca_historical import fetch_historical_data
from src.fetchers.alpaca_realtime import start_stream
from src.fetchers.quiverquant_fetcher import process_congressional_trades
from src.fetchers.yf_fetcher import fetch_yahoo_key_stats
from src.utils.database import connect_to_db
from src.backtesting.backtester import run_portfolio_backtest
from src.backtesting.visualization import plot_portfolio_performance

def setup_database():
    """
    Test database connection to ensure everything is set up correctly.
    """
    session = connect_to_db()
    if session:
        print("✅ Database connection successful.")
        session.close()
    else:
        print("❌ Database connection failed.")

def fetch_alpaca_historical():
    """
    Fetch historical stock data from Alpaca and store it in the database.
    """
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    print(f"📊 Fetching historical data for symbols: {symbols}")
    fetch_historical_data(symbols, start_date, end_date)
    print("✅ Historical data fetch complete.")

def stream_alpaca_realtime():
    """
    Stream real-time stock market data from Alpaca and store it in the database.
    """
    print("🚀 Starting real-time Alpaca data stream...")
    start_stream()

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
    Main entry point for the data pipeline.
    """
    parser = argparse.ArgumentParser(description="Ishara Data Pipeline")
    parser.add_argument(
        "--setup-db", action="store_true", help="Test database connection setup."
    )
    parser.add_argument(
        "--fetch-historical", action="store_true", help="Fetch historical Alpaca data."
    )
    parser.add_argument(
        "--stream-realtime", action="store_true", help="Stream real-time Alpaca data."
    )

    args = parser.parse_args()

    if args.setup_db:
        setup_database()
    elif args.fetch_historical:
        fetch_alpaca_historical()
    elif args.stream_realtime:
        stream_alpaca_realtime()
    else:
        print("❓ No valid arguments provided. Use --help for available options.")

if __name__ == "__main__":
    main()