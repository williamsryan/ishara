import alpaca_trade_api as tradeapi
from src.utils.database import insert_stock_data
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def fetch_and_store_historical_data(symbols, start, end, timeframe="day"):
    """
    Fetch and store historical stock data for multiple symbols.

    Args:
        symbols (list): List of stock symbols.
        start (str): Start date (YYYY-MM-DD).
        end (str): End date (YYYY-MM-DD).
        timeframe (str): Timeframe (e.g., 'day', 'minute').
    """
    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        bars = api.get_bars(symbol, timeframe, start=start, end=end).df
        bars.index = bars.index.tz_convert(None)  # Remove timezone info
        data = [
            (symbol, row.name, row["open"], row["high"], row["low"], row["close"], row["volume"])
            for _, row in bars.iterrows()
        ]
        insert_stock_data(data)
        print(f"Data for {symbol} inserted successfully.")

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]  # Example symbols
    fetch_and_store_historical_data(symbols, "2020-01-01", "2022-12-31")
    