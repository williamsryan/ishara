import requests
import pandas as pd
from src.utils.config import QUIVERQUANT_API_KEY

def fetch_congressional_trades():
    """Fetch congressional trading data from QuiverQuant."""
    url = "https://api.quiverquant.com/beta/congresstrading"
    headers = {"Authorization": f"Token {QUIVERQUANT_API_KEY}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

if __name__ == "__main__":
    df = fetch_congressional_trades()
    df.to_csv("data/raw/congressional_trades.csv", index=False)
    print("Congressional trades data saved to data/raw/congressional_trades.csv")
    