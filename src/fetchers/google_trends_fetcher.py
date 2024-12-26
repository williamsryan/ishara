from pytrends.request import TrendReq
from datetime import datetime
from src.utils.database import insert_alternative_data

def fetch_google_trends(symbols):
    """
    Fetch Google Trends data for symbols and insert into the database.
    """
    pytrends = TrendReq()
    data_to_insert = []

    for symbol in symbols:
        print(f"🔍 Fetching Google Trends data for {symbol}...")
        pytrends.build_payload([symbol], timeframe="now 7-d")
        trends = pytrends.interest_over_time()

        if trends.empty:
            print(f"⚠️ No trends data found for {symbol}.")
            continue

        for date, row in trends.iterrows():
            if 'isPartial' in row and row['isPartial']:
                continue
            data_to_insert.append((
                "google_trends",  # Source
                symbol,
                date,
                "interest_over_time",
                row[symbol],
                None  # Details
            ))

    # Insert data into the database
    if data_to_insert:
        insert_alternative_data(data_to_insert)
    else:
        print("⚠️ No data fetched to insert.")

if __name__ == "__main__":
    fetch_google_trends(["AAPL", "MSFT", "GOOGL", "AMZN"])
    