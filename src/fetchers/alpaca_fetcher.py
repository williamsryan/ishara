import alpaca_trade_api as tradeapi
from src.utils.database import insert_stock_data
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def fetch_and_store_historical_data(symbols, start, end, timeframe="1Day"):
    """
    Fetch and store historical stock data for multiple symbols.

    Args:
        symbols (list): List of stock symbols.
        start (str): Start date (YYYY-MM-DD).
        end (str): End date (YYYY-MM-DD).
        timeframe (str): Timeframe (e.g., '1Day', '1Min', '1Hour').
    """
    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
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
        insert_stock_data(data)
        print(f"Data for {symbol} inserted successfully.")

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]  # Example symbols
    fetch_and_store_historical_data(symbols, "2020-01-01", "2022-12-31")
    