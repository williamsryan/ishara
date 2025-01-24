import argparse
import json
from src.fetchers.alpaca_historical import insert_historical_data
from src.fetchers.alpaca_realtime import fetch_real_time_data
from src.fetchers.yf_fetcher import fetch_yahoo_finance_data
from src.fetchers.google_trends_fetcher import fetch_google_trends
from src.fetchers.reddit_fetcher import fetch_reddit_sentiment
from src.fetchers.quiverquant_fetcher import process_congressional_trades
from src.fetchers.symbol_fetcher import populate_symbols_table
from src.processors.clustering_analysis import perform_clustering_analysis
from src.processors.regime_analysis import perform_regime_analysis
from src.processors.derived_metrics import populate_derived_metrics
# from src.backtesting.backtester import BacktestManager
from src.backtesting.backtester_zipline import BacktesterZipline
from src.backtesting.strategies.macd_strategy import MACDStrategy
from src.dashboard.app import run_dashboard

# Default tickers and subreddits
DEFAULT_TICKERS = [
    "T", "PG", "F", "ACHR", "LUNR", "RKLB", "SNOW",
    "RGTI", "QBTS", "QUBT", "MSTR", "PLTR", "PL", "KURA", "KULR"
]
DEFAULT_SUBREDDITS = ["stocks", "investing", "wallstreetbets"]
STRATEGY_REGISTRY = {
    "MACDStrategy": MACDStrategy,
}

def populate_database(target, start_date=None, end_date=None):
    """
    Populate the database with data from selected sources.
    Args:
        target (str): Target dataset to populate.
        start_date (str): Start date for historical data (YYYY-MM-DD).
        end_date (str): End date for historical data (YYYY-MM-DD).
    """
    if target == "all":
        populate_symbols_table()
        insert_historical_data(DEFAULT_TICKERS, start_date, end_date)
        fetch_yahoo_finance_data(DEFAULT_TICKERS)
        fetch_google_trends(DEFAULT_TICKERS)
        fetch_reddit_sentiment(DEFAULT_SUBREDDITS, DEFAULT_TICKERS)
        populate_derived_metrics()
    elif target == "symbols":
        populate_symbols_table()
    elif target == "alpaca_historical":
        insert_historical_data(DEFAULT_TICKERS, start_date, end_date)
    elif target == "alpaca_realtime":
        fetch_real_time_data()
    elif target == "yahoo_finance":
        fetch_yahoo_finance_data(DEFAULT_TICKERS)
    elif target == "google_trends":
        fetch_google_trends(DEFAULT_TICKERS)
    elif target == "reddit":
        fetch_reddit_sentiment(DEFAULT_SUBREDDITS, DEFAULT_TICKERS)
    elif target == "quiver":
        process_congressional_trades()
    elif target == "derived":
        populate_derived_metrics()
    else:
        print(f"⚠️ Unknown target '{target}' for database population.")

def run_analysis(analysis_type):
    """
    Run a specified analysis and display results.
    Args:
        analysis_type (str): Type of analysis to perform.
    """
    if analysis_type == "clustering":
        perform_clustering_analysis()
    elif analysis_type == "regime":
        perform_regime_analysis()
    else:
        print(f"⚠️ Unknown analysis type '{analysis_type}'.")

def run_backtest(symbols, start_date, end_date, strategy_name, additional_args):
    """
    Run a backtest with the specified parameters.
    """
    print(f"⚙️ Running backtest with strategy: {strategy_name}")

    try:
        # Load the user-defined strategy
        if strategy_name not in STRATEGY_REGISTRY:
            raise ValueError(f"Strategy '{strategy_name}' is not registered.")
        strategy = STRATEGY_REGISTRY[strategy_name]()

        # Initialize and run the backtest
        backtester = BacktesterZipline(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            strategy=strategy,
            capital=additional_args.get("capital", 100000),
        )
        results = backtester.run()
        print(f"✅ Backtesting completed successfully.")
        print(f"📈 Results:\n{results}")
    except Exception as e:
        print(f"❌ Error during backtesting: {e}")

def load_ticker_data(file_path):
    """
    Load ticker data from a JSON file.
    Args:
        file_path (str): Path to the JSON file.
    Returns:
        dict: Parsed ticker data.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def main():
    parser = argparse.ArgumentParser(description="Ishara Platform Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: Populate Database
    populate_parser = subparsers.add_parser("populate", help="Populate the database with data.")
    populate_parser.add_argument(
        "target",
        choices=[
            "all", "symbols", "alpaca_historical", "alpaca_realtime",
            "yahoo_finance", "google_trends", "reddit", "quiver", "derived"
        ],
        help="Data source to populate."
    )
    populate_parser.add_argument(
        "--start-date", type=str, default="2024-01-01", help="Start date for historical data (YYYY-MM-DD)."
    )
    populate_parser.add_argument(
        "--end-date", type=str, default="2024-12-31", help="End date for historical data (YYYY-MM-DD)."
    )

    # Subcommand: Run Analyses
    analysis_parser = subparsers.add_parser("analyze", help="Run an analysis.")
    analysis_parser.add_argument("type", choices=["clustering", "regime"], help="Type of analysis to perform.")

    # Subcommand: Backtest
    backtest_parser = subparsers.add_parser("backtest", help="Run a backtest.")
    backtest_parser.add_argument("-s", "--symbols", type=str, required=True, help="Comma-separated list of stock symbols (e.g., AAPL,MSFT,GOOGL)")
    backtest_parser.add_argument("-sd", "--start-date", type=str, required=True, help="Start date for the backtest in YYYY-MM-DD format")
    backtest_parser.add_argument("-ed", "--end-date", type=str, required=True, help="End date for the backtest in YYYY-MM-DD format")
    backtest_parser.add_argument("-st", "--strategy", type=str, required=True, help="Strategy to backtest (e.g., MovingAverageCrossover, MomentumStrategy)")
    backtest_parser.add_argument("-a", "--args", type=json.loads, default={}, help="Additional arguments for the strategy (JSON format)")

    # Subcommand: Launch UI
    subparsers.add_parser("ui", help="Launch the Ishara dashboard UI.")

    # Subcommand: Load Data
    load_parser = subparsers.add_parser("load", help="Specify input file to load ticker data (JSON)")
    load_parser.add_argument("file", type=str, help="Path to the input JSON file containing ticker data.")

    args = parser.parse_args()

    if args.command == "populate":
        populate_database(args.target, args.start_date, args.end_date)
    elif args.command == "analyze":
        run_analysis(args.type)
    elif args.command == "backtest":
        symbols = [symbol.strip() for symbol in args.symbols.split(",")]
        run_backtest(symbols, args.start_date, args.end_date, args.strategy, args.args)
    elif args.command == "ui":
        run_dashboard()
    elif args.command == "load":
        ticker_data = load_ticker_data(args.file)
        print(f"Loaded ticker data: {ticker_data}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
