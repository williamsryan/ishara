import yfinance as yf
from datetime import datetime
from src.utils.database import insert_yahoo_finance_data

def fetch_yahoo_finance_data(symbols):
    """
    Fetch historical data from Yahoo Finance and insert into the database.
    """
    data_to_insert = []

    for symbol in symbols:
        print(f"📊 Fetching Yahoo Finance data for {symbol}...")
        stock = yf.Ticker(symbol)
        history = stock.history(period="1y", interval="1h")

        # Prepare data for insertion
        for date, row in history.iterrows():
            data_to_insert.append((
                symbol,
                date,
                int(row['Open']),
                int(row['High']),
                int(row['Low']),
                int(row['Close']),
                int(row['Volume']),
                None,  # Dividends
                None   # Earnings
            ))

    # Insert data into the database
    if data_to_insert:
        insert_yahoo_finance_data(data_to_insert)
    else:
        print("⚠️ No data fetched to insert.")

if __name__ == "__main__":
    fetch_yahoo_finance_data(["AAPL", "MSFT", "GOOGL", "AMZN"])
    