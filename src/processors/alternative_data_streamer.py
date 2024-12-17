import time
from src.fetchers.yf_fetcher import fetch_yfinance_data
from src.fetchers.google_trends_fetcher import fetch_google_trends_data
from src.fetchers.reddit_fetcher import fetch_reddit_sentiment

def stream_alternative_data(symbols, keywords, subreddit="stocks", interval=60):
    """
    Stream alternative data sources periodically.
    """
    while True:
        print("🌐 Streaming Yahoo Finance data...")
        fetch_yfinance_data(symbols)

        print("🔍 Streaming Google Trends data...")
        fetch_google_trends_data(keywords)

        print("📰 Streaming Reddit sentiment data...")
        for keyword in keywords:
            fetch_reddit_sentiment(subreddit, keyword)

        print("✅ Alternative data streaming cycle complete. Sleeping...")
        time.sleep(interval)

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT"]
    keywords = ["AAPL", "MSFT"]
    stream_alternative_data(symbols, keywords)
    