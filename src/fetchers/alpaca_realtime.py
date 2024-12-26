import websocket
import json
from datetime import datetime
from dateutil import parser 
from src.utils.database import insert_real_time_data
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY

DEFAULT_TICKERS = ["T", "PG", "F", "ACHR", "LUNR", "RKLB", "SNOW", "RGTI", "QBTS", "QUBT", "MSTR", "PLTR", "PL", "KURA"]

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
        "trades": DEFAULT_TICKERS,  # Trade updates
        "bars": DEFAULT_TICKERS     # Minute bar updates
    }
    ws.send(json.dumps(subscribe_payload))
    print(f"✅ Subscribed to trades and bars for: {', '.join(DEFAULT_TICKERS)}")

def on_message(ws, message):
    """
    Processes incoming messages from Alpaca's WebSocket.
    """
    try:
        parsed_message = json.loads(message)
        data_to_insert = []

        # Process incoming WebSocket messages
        for entry in parsed_message:
            if entry.get("T") == "b":  # 'b' indicates bar data (OHLC)
                timestamp = parser.isoparse(entry["t"])  # Automatically handles fractional seconds or not
                symbol = entry["S"]
                open_price = float(entry["o"])
                high_price = float(entry["h"])
                low_price = float(entry["l"])
                close_price = float(entry["c"])
                volume = int(entry["v"])

                data_to_insert.append((symbol, timestamp, open_price, high_price, low_price, close_price, volume))

            elif entry.get("T") == "t":  # 't' indicates trade data
                timestamp = parser.isoparse(entry["t"])
                symbol = entry["S"]
                price = float(entry["p"])  # Trade price
                volume = int(entry["s"])  # Trade volume

                # Use `price` for all OHLC fields for trade data
                data_to_insert.append((symbol, timestamp, price, price, price, price, volume))

        if data_to_insert:
            insert_real_time_data(data_to_insert)

    except Exception as e:
        print(f"❌ Error processing message: {e}")
        print(f"Message causing error: {message}")

def fetch_real_time_data():
    """
    Starts the Alpaca WebSocket stream with authentication and subscriptions.
    """
    socket_url = "wss://stream.data.alpaca.markets/v2/iex"

    ws = websocket.WebSocketApp(
        socket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=lambda ws, err: print(f"❌ WebSocket error: {err}"),
        on_close=lambda ws, close_status, close_msg: print("❌ WebSocket connection closed.")
    )

    print("🔄 Starting WebSocket stream...")
    ws.run_forever()

if __name__ == "__main__":
    fetch_real_time_data()
