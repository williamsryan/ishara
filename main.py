import argparse
from src.fetchers.alpaca_historical import insert_historical_data
from src.fetchers.alpaca_realtime import start_stream as stream_alpaca_realtime
from src.fetchers.yf_fetcher import fetch_yahoo_finance_data
from src.fetchers.google_trends_fetcher import fetch_google_trends
from src.fetchers.reddit_fetcher import fetch_reddit_sentiment
from src.processors.alternative_data_streamer import stream_alternative_data
from src.processors.clustering_analysis import perform_clustering_analysis
from src.processors.regime_analysis import perform_regime_analysis
from src.dashboard.app import run_dashboard_with_stream
from src.utils.database import connect_to_db

def setup_database():
    """
    Test the database connection to ensure everything is working.
    """
    conn = connect_to_db()
    if conn:
        print("✅ Database connection successful.")
        conn.close()
    else:
        print("❌ Database connection failed.")

def fetch_historical_data():
    """
    Fetch historical stock data from Alpaca and store it in the database.
    """
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    start_date = "2024-12-01"
    end_date = "2024-12-20"
    print(f"📊 Fetching historical data for symbols: {symbols}")
    insert_historical_data(symbols, start_date, end_date)
    print("✅ Historical data fetch complete.")

def fetch_alternative_data():
    """
    Fetch alternative data sources: Google Trends, Reddit sentiment, Yahoo Finance.
    """
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    keywords = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    subreddits = ["stocks", "wallstreetbets"]

    print("🔍 Fetching alternative data...")

    # Fetch Yahoo Finance
    print("📊 Fetching Yahoo Finance data...")
    fetch_yahoo_finance_data(symbols)

    # Fetch Google Trends
    print("📈 Fetching Google Trends data...")
    fetch_google_trends(keywords)

    # Fetch Reddit sentiment
    print("📰 Fetching Reddit sentiment data...")
    for subreddit in subreddits:
        for keyword in keywords:
            fetch_reddit_sentiment(subreddit, keyword)

    print("✅ Alternative data fetch complete.")

def stream_real_time_data():
    """
    Stream real-time Alpaca market data.
    """
    print("🚀 Starting Alpaca real-time data streaming...")
    stream_alpaca_realtime()

    # symbols = ["AAPL", "MSFT"]
    # keywords = ["AAPL", "MSFT"]
    # print("🚀 Starting real-time alternative data stream...")
    # stream_alternative_data(symbols, keywords, subreddit="stocks", interval=300)

def perform_clustering():
    """
    Perform clustering analysis on historical and alternative data.
    """
    print("🔍 Performing clustering analysis...")
    perform_clustering_analysis(["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"])
    print("✅ Clustering analysis complete.")

def perform_regime_analysis():
    """
    Perform regime detection analysis on historical data.
    """
    print("🔍 Performing regime detection analysis...")
    perform_regime_analysis()
    print("✅ Regime detection analysis complete.")

def launch_dashboard():
    """
    Launch the interactive UI dashboard for viewing data.
    """
    print("🚀 Launching the Ishara Trading Dashboard...")
    run_dashboard_with_stream()

def main():
    parser = argparse.ArgumentParser(description="Ishara Data Pipeline and Dashboard")
    parser.add_argument("--setup-db", action="store_true", help="Test database connection.")
    parser.add_argument("--fetch-historical", action="store_true", help="Fetch historical market data.")
    parser.add_argument("--fetch-alternative", action="store_true", help="Fetch alternative data sources.")
    parser.add_argument("--stream-data", action="store_true", help="Stream real-time market data.")
    parser.add_argument("--perform-clustering", action="store_true", help="Perform clustering analysis.")
    parser.add_argument("--perform-regime", action="store_true", help="Perform regime detection analysis.")
    parser.add_argument("--launch-ui", action="store_true", help="Launch the interactive UI dashboard.")

    args = parser.parse_args()

    if args.setup_db:
        setup_database()
    elif args.fetch_historical:
        fetch_historical_data()
    elif args.fetch_alternative:
        fetch_alternative_data()
    elif args.stream_data:
        stream_real_time_data()
    elif args.perform_clustering:
        perform_clustering()
    elif args.perform_regime:
        perform_regime_analysis()
    elif args.launch_ui:
        launch_dashboard()
    else:
        print("❓ No valid arguments provided. Use --help for options.")

if __name__ == "__main__":
    main()
