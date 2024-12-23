import pandas as pd
import alpaca_trade_api as tradeapi
from src.utils.database import insert_historical_market_data
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def insert_historical_data(symbols, start, end, timeframe="1Day"):
    """
    Fetch and store historical stock data for multiple symbols at the finest granularity.

    Args:
        symbols (list): List of stock symbols.
        start (str): Start date (YYYY-MM-DD).
        end (str): End date (YYYY-MM-DD).
        timeframe (str): Timeframe (e.g., '1Min', '1Day').
    """
    for symbol in symbols:
        print(f"Fetching {timeframe} data for {symbol}...")
        try:
            bars = api.get_bars(symbol, timeframe, start=start, end=end).df
            bars.index = bars.index.tz_convert(None)  # Remove timezone info
            data = [
                (
                    symbol,
                    row.name,  # datetime
                    float(row["open"]),  # Convert np.float64 to float
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    int(row["volume"])  # Convert np.int64 to int
                )
                for _, row in bars.iterrows()
            ]
            insert_historical_market_data(data)
            print(f"Data for {symbol} inserted successfully.")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

def fetch_historical_data(symbols, start_date, end_date, timeframe="1Day"):
    """
    Fetch historical stock data from Alpaca and return it as a DataFrame.

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
        print(f"Fetching historical data for {symbol}...")
        bars = api.get_bars(symbol, timeframe, start=start_date, end=end_date).df
        bars.index = bars.index.tz_convert(None)  # Remove timezone info

        # Prepare data for DataFrame
        fetched_data = [
            [symbol, row.name, row["open"], row["high"], row["low"], row["close"], row["volume"]]
            for _, row in bars.iterrows()
        ]
        all_data.extend(fetched_data)

    # Convert to DataFrame
    columns = ["symbol", "datetime", "open", "high", "low", "close", "volume"]
    return pd.DataFrame(all_data, columns=columns)

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]  # Example symbols
    insert_historical_data(symbols, "2023-12-01", "2024-12-16")
