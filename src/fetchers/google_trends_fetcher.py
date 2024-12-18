from pytrends.request import TrendReq
from datetime import datetime
from time import sleep
import random
from src.utils.database import insert_alternative_data

def fetch_google_trends_data(keywords):
    """
    Fetch Google Trends data for a list of keywords and insert into the database.
    """
    data_to_insert = []

    # pytrends = TrendReq(
    #     hl='en-US', tz=360, 
    #     proxies=['https://34.203.233.13:80', 'https://51.79.50.22:8080'],
    #     retries=3,
    #     backoff_factor=0.3
    # )

    for keyword in keywords:
        retries = 3  # Number of retries for each keyword
        for attempt in range(retries):
            try:
                print(f"📊 Fetching Google Trends data for keyword: {keyword} (Attempt {attempt + 1})...")
                pytrends = TrendReq(hl='en-US', tz=360)  # Reinitialize for each keyword
                pytrends.build_payload([keyword], timeframe="today 1-m", geo='', gprop='')

                # Fetch trends data
                trends = pytrends.interest_over_time()

                if trends.empty:
                    print(f"⚠️ No trends data returned for keyword: {keyword}")
                else:
                    print(f"✅ Trends data fetched successfully for keyword: {keyword}")
                    print(trends.tail())  # Debug output

                    # Extract latest search volume
                    search_volume = trends[keyword].iloc[-1]
                    print(f"📈 Latest search volume for {keyword}: {search_volume}")

                    # Prepare data for insertion
                    data_to_insert.append((
                        "google_trends",
                        keyword,
                        datetime.now(),
                        "search_volume",
                        search_volume,
                        None
                    ))
                break  # Exit retry loop on success
            except Exception as e:
                print(f"❌ Error fetching Google Trends data for {keyword}: {e}")
                sleep(10)  # Short delay before retry
        else:
            print(f"❌ Failed to fetch data for keyword: {keyword} after {retries} attempts.")

        # Respect rate limits
        delay = random.randint(15, 45)
        print(f"⏳ Sleeping for {delay} seconds to respect rate limits...")
        sleep(delay)

    # Insert fetched data into the database
    if data_to_insert:
        try:
            print(f"🛠️ Inserting {len(data_to_insert)} records into the database...")
            insert_alternative_data(data_to_insert)
            print(f"✅ Successfully inserted {len(data_to_insert)} records.")
        except Exception as db_error:
            print(f"❌ Error inserting data into the database: {db_error}")
    else:
        print("⚠️ No valid data fetched to insert.")
        