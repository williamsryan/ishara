from pytrends.request import TrendReq
from datetime import datetime
from time import sleep  # Import sleep for rate limiting
from src.utils.database import insert_alternative_data

def fetch_google_trends_data(keywords):
    """
    Fetch Google Trends data and store it using insert_alternative_data.
    """
    pytrends = TrendReq(hl='en-US', tz=360)  # Initialize Google Trends
    data_to_insert = []

    for keyword in keywords:
        try:
            print(f"📊 Fetching Google Trends data for keyword: {keyword}...")
            pytrends.build_payload([keyword], timeframe="now 7-d")

            trends = pytrends.interest_over_time()
            if not trends.empty:
                search_volume = trends[keyword].iloc[-1]
                data_to_insert.append(("google_trends", keyword, datetime.now(), "search_volume", search_volume, None))
                print(f"✅ Data fetched for {keyword}: {search_volume}")
            
            # Rate limiting: Sleep for 30 seconds between requests
            sleep(30)

        except Exception as e:
            print(f"❌ Error fetching Google Trends data for {keyword}: {e}")

    if data_to_insert:
        insert_alternative_data(data_to_insert)
        print("✅ Google Trends data inserted successfully.")
    else:
        print("⚠️ No valid data fetched to insert.")
