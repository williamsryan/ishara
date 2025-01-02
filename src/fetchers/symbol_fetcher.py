import requests
import pandas as pd
from src.utils.database import insert_symbols
from src.utils.config import FINNHUB_API_KEY

API_URL = "https://finnhub.io/api/v1/stock/symbol"

def fetch_symbols(exchange="US"):
    """Fetch symbols from Finnhub for a given exchange."""
    try:
        params = {"exchange": exchange, "token": FINNHUB_API_KEY}
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        symbols = response.json()
        return [
            (symbol["symbol"], symbol.get("description", ""), symbol.get("type", ""), exchange)
            for symbol in symbols if "symbol" in symbol
        ]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching symbols: {e}")
        return []

def populate_symbols_table():
    """
    Fetch symbols and populate the symbols table in the database.
    """
    data = fetch_symbols()  # Assume fetch_symbols() fetches the data
    if not data:
        print("⚠️ No symbol data fetched.")
        return

    # Insert the fetched data into the symbols table
    rows_inserted = insert_symbols(data)
    print(f"✅ Inserted {rows_inserted} symbols into the symbols table.")

if __name__ == "__main__":
    populate_symbols_table()
