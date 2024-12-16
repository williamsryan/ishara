import alpaca_trade_api as tradeapi
from src.utils.database import insert_stock_data
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def fetch_alpaca_historical(symbols, start_date, end_date, timeframe="1Day"):
    """
    Fetch historical stock data from Alpaca.
    
    Args:
        symbols (list): List of stock symbols to fetch.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        timeframe (str): Timeframe for data ('1Min', '1Day', etc.).
    
    Returns:
        list: List of tuples [(symbol, datetime, open, high, low, close, volume)].
    """
    all_data = []
    for symbol in symbols:
        print(f"Fetching historical data for {symbol}...")
        bars = api.get_bars(symbol, timeframe, start=start_date, end=end_date).df
        bars.index = bars.index.tz_convert(None)
        all_data.extend([
            (symbol, row.name, float(row["open"]), float(row["high"]),
             float(row["low"]), float(row["close"]), int(row["volume"]))
            for _, row in bars.iterrows()
        ])
    return all_data

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "TSLA"]
    data = fetch_alpaca_historical(symbols, "2020-01-01", "2023-12-31")
    insert_stock_data(data)
    print("Historical stock data inserted into database.")
    