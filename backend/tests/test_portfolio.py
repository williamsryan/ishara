import requests

BASE_URL = "http://localhost:1337/api"

def fetch_stock_data():
    url = f"{BASE_URL}/stocks"
    payload = {
        "symbols": ["AAPL", "MSFT", "GOOGL"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "timeframe": "1Day"
    }
    response = requests.post(url, json=payload)
    print("Stocks Response:", response.json())

def fetch_options_data():
    url = f"{BASE_URL}/options"
    payload = {
        "symbols": ["AAPL", "MSFT"],
        "expiration_dates": ["2025-02-16", "2025-03-16"]
    }
    response = requests.post(url, json=payload)
    print("Options Response:", response.json())

def start_streaming():
    url = f"{BASE_URL}/stream"
    payload = {
        "symbols": ["AAPL", "MSFT", "GOOGL"]
    }
    response = requests.post(url, json=payload)
    print("Stream Response:", response.json())

if __name__ == "__main__":
    fetch_stock_data()
    fetch_options_data()
    start_streaming()
    