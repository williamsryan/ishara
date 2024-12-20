from pytrends.request import TrendReq
from src.utils.database import insert_alternative_data

def fetch_google_trends(symbols):
    """
    Fetch Google Trends data for the given symbols and insert it into the database.

    Args:
        symbols (list): List of symbols to fetch trends data for.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    all_data = []

    for symbol in symbols:
        try:
            print(f"📊 Fetching Google Trends data for keyword: {symbol}...")
            pytrends.build_payload(kw_list=[symbol], timeframe='today 5-y')
            trends_data = pytrends.interest_over_time()

            if trends_data.empty:
                print(f"⚠️ No trends data available for symbol: {symbol}.")
                continue

            processed_data = process_google_trends_data(trends_data, symbol)
            all_data.extend(processed_data)

            print(f"✅ Successfully fetched trends data for keyword: {symbol}.")
        except Exception as e:
            print(f"❌ Error fetching Google Trends data for {symbol}: {e}")

    if all_data:
        print(f"🛠️ Inserting {len(all_data)} records into the database...")
        insert_alternative_data(all_data)
    else:
        print("⚠️ No valid Google Trends data to insert.")

def process_google_trends_data(data, symbol):
    """
    Processes Google Trends data for insertion into the database.

    Args:
        data (DataFrame): DataFrame containing Google Trends data.
        symbol (str): Symbol for which data is fetched.

    Returns:
        list: Processed data ready for database insertion.
    """
    processed_data = []
    for index, row in data.iterrows():
        processed_data.append((
            'google_trends',
            symbol,
            pd.Timestamp(index).to_pydatetime(),  # Convert to native datetime
            'search_volume',
            int(row[symbol]),                     # Cast numpy.int64 to int
            f"Partial: {row['isPartial']}"        # Add partial details
        ))
    return processed_data
