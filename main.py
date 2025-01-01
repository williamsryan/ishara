import argparse
from src.fetchers.alpaca_historical import insert_historical_data
from src.fetchers.alpaca_realtime import fetch_real_time_data
from src.fetchers.yf_fetcher import fetch_yahoo_finance_data
from src.fetchers.google_trends_fetcher import fetch_google_trends
from src.fetchers.reddit_fetcher import fetch_reddit_sentiment
from src.fetchers.quiverquant_fetcher import process_congressional_trades
from src.processors.clustering_analysis import perform_clustering_analysis
from src.processors.regime_analysis import perform_regime_analysis
from src.processors.derived_metrics import populate_derived_metrics
from src.dashboard.app import run_dashboard
import json

DEFAULT_TICKERS = ["T", "PG", "F", "ACHR", "LUNR", "RKLB", "SNOW", "RGTI", "QBTS", "QUBT", "MSTR", "PLTR", "PL", "KURA"]

def populate_database(target):
    """
    Populate the database with data from selected sources.
    """
    if target == "all":
        insert_historical_data(DEFAULT_TICKERS)
        fetch_yahoo_finance_data(DEFAULT_TICKERS)
        fetch_google_trends(DEFAULT_TICKERS)
        fetch_reddit_sentiment("stocks", DEFAULT_TICKERS)
        populate_derived_metrics()
        # fetch_real_time_data()
    elif target == "alpaca_historical":
        insert_historical_data(DEFAULT_TICKERS)
    elif target == "alpaca_realtime":
        fetch_real_time_data()
    elif target == "yahoo_finance":
        fetch_yahoo_finance_data(DEFAULT_TICKERS)
    elif target == "google_trends":
        fetch_google_trends(DEFAULT_TICKERS)
    elif target == "reddit":
        fetch_reddit_sentiment("stocks", DEFAULT_TICKERS)
    elif target == "quiver":
        process_congressional_trades()
    elif target == "derived":
        populate_derived_metrics()
    else:
        print(f"⚠️ Unknown target '{target}' for database population.")

def run_analysis(analysis_type):
    """
    Run a specified analysis and display results.
    """
    if analysis_type == "clustering":
        perform_clustering_analysis()
    elif analysis_type == "regime":
        perform_regime_analysis()
    else:
        print(f"⚠️ Unknown analysis type '{analysis_type}'.")

def main():
    parser = argparse.ArgumentParser(description="Ishara Platform Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: Populate Database
    populate_parser = subparsers.add_parser("populate", help="Populate the database with data.")
    populate_parser.add_argument("target", choices=["all", "alpaca_historical", "alpaca_realtime", "yahoo_finance", "google_trends", "reddit", "quiver", "derived"], help="Data source to populate.")

    # Subcommand: Run Analyses
    analysis_parser = subparsers.add_parser("analyze", help="Run an analysis.")
    analysis_parser.add_argument("type", choices=["clustering", "regime"], help="Type of analysis to perform.")

    # Subcommand: Launch UI
    subparsers.add_parser("ui", help="Launch the Ishara dashboard UI.")

    # Subcommand: Load Data
    load_parser = subparsers.add_parser("load", help="Specify input file to load ticker data (JSON)")
    load_parser.add_argument("file", type=str, help="Path to the input JSON file containing ticker data.")

    args = parser.parse_args()

    if args.command == "populate":
        populate_database(args.target)
    elif args.command == "analyze":
        run_analysis(args.type)
    elif args.command == "ui":
        run_dashboard()
    elif args.command == "load":
        print(f"Loading data from input file: {args.file}")
        def load_ticker_data(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data

        ticker_data = load_ticker_data(args.file)
        print(f"Loaded ticker data: {ticker_data}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
    