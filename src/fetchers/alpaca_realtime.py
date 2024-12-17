import websocket
import json
from datetime import datetime
from src.utils.database import connect_to_db
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY

def insert_real_time_data(data):
    """
    Inserts real-time market data into the database.
    """
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO real_time_market_data (symbol, datetime, price, volume)
            VALUES (%s, %s, %s, %s);
        """, (data['symbol'], data['timestamp'], data['price'], data['volume']))
        conn.commit()
    except Exception as e:
        print(f"Error inserting real-time data: {e}")
    finally:
        cursor.close()
        conn.close()

def on_open(ws):
    """
    Sends authentication payload on WebSocket connection open.
    """
    print("🔐 Authenticating WebSocket...")
    auth_payload = {
        "action": "auth",
        "key": ALPACA_API_KEY,
        "secret": ALPACA_SECRET_KEY
    }
    ws.send(json.dumps(auth_payload))
    print("✅ WebSocket authentication sent.")

    # Subscribe to market data
    print("📡 Subscribing to symbols...")
    subscribe_payload = {
        "action": "subscribe",
        "bars": ["AAPL", "MSFT", "GOOGL"]  # Replace with desired symbols
    }
    ws.send(json.dumps(subscribe_payload))
    print(f"✅ Subscribed to symbols: {subscribe_payload['bars']}")

def on_message(ws, message):
    """
    Handles incoming WebSocket messages and inserts data into the database.
    """
    try:
        data = json.loads(message)
        if isinstance(data, list):
            for item in data:
                parse_and_insert(item)
        elif isinstance(data, dict):
            parse_and_insert(data)
        else:
            print(f"Unexpected message format: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")

def parse_and_insert(item):
    """
    Parses a single WebSocket message and inserts it into the database.
    """
    if "T" in item and item["T"] == "b":  # "b" stands for bar (market data)
        try:
            record = {
                'symbol': item['S'],  # Symbol
                'timestamp': datetime.fromtimestamp(item['t'] / 1e9),  # Timestamp
                'price': item['c'],  # Close price
                'volume': item['v']   # Volume
            }
            insert_real_time_data(record)
            print(f"Inserted real-time data: {record}")
        except KeyError as e:
            print(f"Missing field in bar data: {e}")
    elif "T" in item and item["T"] in ["success", "error"]:
        print(f"WebSocket message: {item}")

def start_stream():
    """
    Starts the Alpaca WebSocket stream with authentication and subscriptions.
    """
    socket_url = "wss://stream.data.alpaca.markets/v2/iex"  # Adjust to 'sip' for premium feed

    ws = websocket.WebSocketApp(
        socket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=lambda ws, err: print(f"WebSocket error: {err}"),
        on_close=lambda ws, close_status, close_msg: print("WebSocket connection closed.")
    )

    ws.run_forever()

if __name__ == "__main__":
    start_stream()
