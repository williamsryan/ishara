import alpaca_trade_api as tradeapi
import pandas as pd
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def fetch_historical_data(symbol, start, end, timeframe="day"):
    """Fetch historical stock price data."""
    bars = api.get_bars(symbol, timeframe, start=start, end=end).df
    bars.index = bars.index.tz_convert(None)  # Convert timezone
    return bars

if __name__ == "__main__":
    data = fetch_historical_data("AAPL", "2020-01-01", "2022-12-31")
    data.to_csv("data/raw/aapl_historical.csv", index=False)
    print("AAPL historical data saved to data/raw/aapl_historical.csv")
    