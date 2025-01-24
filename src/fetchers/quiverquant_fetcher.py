import requests
import pandas as pd
from src.utils.database import insert_quiverquant_data
from src.utils.config import QUIVERQUANT_API_KEY

def fetch_quiverquant_data(endpoint):
    """
    Fetch data from a specific QuiverQuant endpoint.
    
    Args:
        endpoint (str): API endpoint (e.g., "congresstrading").
    
    Returns:
        pd.DataFrame: Data fetched from QuiverQuant.
    """
    url = f"https://api.quiverquant.com/beta/{endpoint}"
    headers = {"Authorization": f"Token {QUIVERQUANT_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        raise ValueError(f"Failed to fetch data: {response.status_code} - {response.text}")

def process_congressional_trades():
    """Fetch and process congressional trading data."""
    df = fetch_quiverquant_data("congresstrading")
    df['date'] = pd.to_datetime(df['TransactionDate'])
    df['key_metric'] = "TransactionType"
    df['value'] = df['Transaction']
    df['data_source'] = "QuiverQuant"
    processed_data = df[['data_source', 'Ticker', 'date', 'key_metric', 'value']]
    processed_data.columns = ['data_source', 'symbol', 'date', 'key_metric', 'value']
    return processed_data

if __name__ == "__main__":
    data = process_congressional_trades()
    insert_quiverquant_data(data.to_records(index=False))
    print("Congressional trades data inserted into database.")
    