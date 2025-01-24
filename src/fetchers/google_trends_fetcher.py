from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
import pandas as pd
import logging
from time import sleep
from src.utils.database import insert_google_trends_data

# Initialize PyTrends API
pytrends = TrendReq(hl="en-US", tz=360)

def fetch_google_trends(tickers, timeframe="now 5-d", retries=3, retry_delay=5):
    """
    Fetch Google Trends data for specified tickers.

    Args:
        tickers (list): List of tickers to fetch trends for.
        timeframe (str): Timeframe for trends (default: "now 5-d").
        retries (int): Number of retries in case of failure.
        retry_delay (int): Seconds to wait between retries.

    Returns:
        pd.DataFrame: Google Trends data with columns ['ticker', 'date', 'trend_score'].
    """
    trends_data = []
    for ticker in tickers:
        for attempt in range(retries):
            try:
                logging.info(f"🔍 Fetching Google Trends data for {ticker} (Attempt {attempt + 1}/{retries})...")
                pytrends.build_payload([ticker], timeframe=timeframe)
                data = pytrends.interest_over_time()
                if not data.empty:
                    for date, score in data[ticker].items():
                        trends_data.append({"ticker": ticker, "date": date, "trend_score": score})
                    logging.info(f"✅ Successfully fetched data for {ticker}.")
                break  # Break out of retry loop if successful
            except ResponseError as e:
                logging.warning(f"⚠️ Google Trends request failed for {ticker}: {e}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    sleep(retry_delay)
                else:
                    logging.error(f"❌ All retries failed for {ticker}. Skipping.")
            except Exception as e:
                logging.error(f"❌ Unexpected error for {ticker}: {e}")
                break  # Stop retries for unexpected errors
    return pd.DataFrame(trends_data)

def insert_google_trends(tickers, timeframe="now 5-d"):
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
    