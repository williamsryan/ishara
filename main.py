import argparse
from src.fetchers.alpaca_historical import insert_historical_data
from src.fetchers.yf_fetcher import fetch_yfinance_data
from src.fetchers.google_trends_fetcher import fetch_google_trends_data
from src.fetchers.reddit_fetcher import fetch_reddit_sentiment
from src.processors.alternative_data_streamer import stream_alternative_data
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
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    print(f"📊 Fetching historical data for symbols: {symbols}")
    insert_historical_data(symbols, start_date, end_date)
    print("✅ Historical data fetch complete.")

def fetch_alternative_data():
    """
    Fetch alternative data sources: Google Trends, Reddit sentiment, Yahoo Finance.
    """
    symbols = ["AAPL", "MSFT"]
    keywords = ["AAPL", "MSFT"]
    subreddits = ["stocks", "wallstreetbets"]

    print("🔍 Fetching alternative data...")

    # Fetch Google Trends
    print("📈 Fetching Google Trends data...")
    fetch_google_trends_data(keywords)

    # Fetch Reddit sentiment
    print("📰 Fetching Reddit sentiment data...")
    for subreddit in subreddits:
        for keyword in keywords:
            fetch_reddit_sentiment(subreddit, keyword)

    print("✅ Alternative data fetch complete.")

def stream_data():
    """
    Stream alternative data periodically for real-time predictions.
    """
    symbols = ["AAPL", "MSFT"]
    keywords = ["AAPL", "MSFT"]
    print("🚀 Starting real-time alternative data stream...")
    stream_alternative_data(symbols, keywords, subreddit="stocks", interval=300)

def main():
    parser = argparse.ArgumentParser(description="Ishara Data Pipeline")
    parser.add_argument("--setup-db", action="store_true", help="Test database connection.")
    parser.add_argument("--fetch-historical", action="store_true", help="Fetch historical market data.")
    parser.add_argument("--fetch-alternative", action="store_true", help="Fetch alternative data sources.")
    parser.add_argument("--stream-data", action="store_true", help="Stream alternative data in real-time.")

    args = parser.parse_args()

    if args.setup_db:
        setup_database()
    elif args.fetch_historical:
        fetch_historical_data()
    elif args.fetch_alternative:
        fetch_alternative_data()
    elif args.stream_data:
        stream_data()
    else:
        print("❓ No valid arguments provided. Use --help for options.")

if __name__ == "__main__":
    main()