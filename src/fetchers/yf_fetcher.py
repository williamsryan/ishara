import yfinance as yf
from src.utils.database import insert_stock_data

def fetch_yahoo_historical(symbol, start_date, end_date):
    """Fetch historical data using Yahoo Finance."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date)
    data = [
        (symbol, index, row["Open"], row["High"], row["Low"], row["Close"], row["Volume"])
        for index, row in df.iterrows()
    ]
    return data

if __name__ == "__main__":
    data = fetch_yahoo_historical("AAPL", "2020-01-01", "2023-12-31")
    insert_stock_data(data)
    print("Yahoo Finance data inserted into database.")
    