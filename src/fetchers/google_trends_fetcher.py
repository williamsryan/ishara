from pytrends.request import TrendReq
import pandas as pd
import logging
from src.utils.database import insert_google_trends_data

# Initialize PyTrends API
pytrends = TrendReq(hl='en-US', tz=360)

def fetch_google_trends(tickers, timeframe="today 5-y"):
    """
    Fetch Google Trends data for specified tickers.

    Args:
        tickers (list): List of tickers to fetch trends for.
        timeframe (str): Timeframe for trends (default: "today 5-y").

    Returns:
        pd.DataFrame: Google Trends data with columns ['ticker', 'date', 'trend_score'].
    """
    trends_data = []
    for ticker in tickers:
        logging.info(f"Fetching Google Trends data for {ticker}...")
        pytrends.build_payload([ticker], timeframe=timeframe)
        data = pytrends.interest_over_time()
        if not data.empty:
            for date, score in data[ticker].items():
                trends_data.append({"ticker": ticker, "date": date, "trend_score": score})
    return pd.DataFrame(trends_data)

def insert_google_trends(tickers, timeframe="today 5-y"):
    """
    Fetch and store Google Trends data.

    Args:
        tickers (list): List of tickers.
        timeframe (str): Timeframe for trends.
    """
    trends_data = fetch_google_trends(tickers, timeframe)
    if not trends_data.empty:
        insert_google_trends_data(trends_data.to_dict("records"))
        logging.info("✅ Google Trends data inserted successfully.")
    else:
        logging.warning("⚠️ No trends data fetched.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tickers = ["AAPL", "MSFT", "TSLA"]
    insert_google_trends(tickers)
    