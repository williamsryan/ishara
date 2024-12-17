import yfinance as yf
from datetime import datetime
from src.utils.database import insert_alternative_data

def fetch_yfinance_data(symbols):
    """
    Fetch Yahoo Finance data and store it using insert_alternative_data.
    """
    data_to_insert = []
    for symbol in symbols:
        print(f"Fetching Yahoo Finance data for {symbol}...")
        stock = yf.Ticker(symbol)
        history = stock.history(period="1d")

        if not history.empty:
            latest_close = history['Close'].iloc[-1]
            data_to_insert.append(("yfinance", symbol, datetime.now(), "close_price", latest_close))

    if data_to_insert:
        insert_alternative_data(data_to_insert)
        