import websocket
import json
from datetime import datetime
from src.utils.database import connect_to_db
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY

def insert_real_time_data(data):
    """
    Insert real-time market data into the database.
    """
    query = """
        INSERT INTO real_time_market_data (symbol, datetime, price, volume)
        VALUES (%s, %s, %s, %s)
    """
    conn = connect_to_db()
    if not conn:
        print("❌ Failed to connect to the database.")
        return

    try:
        with conn.cursor() as cursor:
            for item in data:
                cursor.execute(
                    query, (item['symbol'], item['datetime'], item['price'], item['volume'])
                )
        conn.commit()
        print(f"✅ Successfully inserted {len(data)} records into real_time_market_data.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting real-time data: {e}")
    finally:
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
        try:
            parsed_message = json.loads(message)
            data_to_insert = []

            for entry in parsed_message:
                if entry.get("T") == "t":  # 'T' indicates trade data
                    # Parse and convert data
                    symbol = entry["S"]
                    timestamp = datetime.utcfromtimestamp(int(entry["t"]) / 1e9)  # Nanoseconds to seconds
                    price = float(entry["p"])  # Convert price to float
                    volume = int(entry["s"])  # Convert size to integer

                    data_to_insert.append({
                        "symbol": symbol,
                        "datetime": timestamp,
                        "price": price,
                        "volume": volume
                    })

            if data_to_insert:
                insert_real_time_data(data_to_insert)

        except Exception as e:
            print(f"Error processing message: {e}")
            print(f"Message causing error: {message}")

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
