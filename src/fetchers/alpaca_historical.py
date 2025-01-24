import pandas as pd
import alpaca_trade_api as tradeapi
from src.utils.database import insert_historical_market_data
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
import logging

# Initialize Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def fetch_historical_data(symbols, start_date, end_date, timeframe="1Day"):
    """
    Fetch historical stock data from Alpaca.

    Args:
        symbols (list): List of stock symbols.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        timeframe (str): Timeframe for data ('1Day', '1Min', etc.).

    Returns:
        pd.DataFrame: Historical stock data with columns ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume'].
    """
    all_data = []
    for symbol in symbols:
        logging.info(f"📊 Fetching {timeframe} data for {symbol}...")
        try:
            bars = api.get_bars(symbol, timeframe, start=start_date, end=end_date).df
            bars.index = bars.index.tz_convert(None)  # Remove timezone info

            # Prepare data for DataFrame
            fetched_data = [
                [symbol, row.name, row["open"], row["high"], row["low"], row["close"], row["volume"]]
                for _, row in bars.iterrows()
            ]
            all_data.extend(fetched_data)
        except Exception as e:
            logging.error(f"❌ Error fetching data for {symbol}: {e}")
            continue

    # Convert to DataFrame
    columns = ["symbol", "datetime", "open", "high", "low", "close", "volume"]
    return pd.DataFrame(all_data, columns=columns)

def insert_historical_data(symbols, start_date, end_date, timeframe="1Day"):
    """
    Fetch and store historical stock data for multiple symbols.

    Args:
        symbols (list): List of stock symbols.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        timeframe (str): Timeframe for data ('1Day', '1Min', etc.).
    """
    historical_data = fetch_historical_data(symbols, start_date, end_date, timeframe)
    if not historical_data.empty:
        data_to_insert = [
            (
                row["symbol"], row["datetime"], float(row["open"]), float(row["high"]),
                float(row["low"]), float(row["close"]), int(row["volume"])
            )
            for _, row in historical_data.iterrows()
        ]
        insert_historical_market_data(data_to_insert)
        logging.info(f"✅ Data for {len(symbols)} symbols inserted successfully.")
    else:
        logging.warning("⚠️ No data fetched for the given parameters.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    symbols = ["AAPL", "MSFT", "GOOGL"]
    insert_historical_data(symbols, start_date="2023-12-01", end_date="2023-12-16")
    