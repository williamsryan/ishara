import websocket
import json
from src.utils.config import ALPACA_API_KEY

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("WebSocket connection closed")

def on_open(ws):
    ws.send(json.dumps({"action": "subscribe", "trades": ["AAPL"]}))

if __name__ == "__main__":
    url = "wss://stream.data.alpaca.markets/v2/iex"
    headers = {"Authorization": f"Bearer {ALPACA_API_KEY}"}
    ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
    