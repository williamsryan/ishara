from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import settings
import json
import websockets
import os

router = APIRouter()

# ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
# ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
# ALPACA_STREAM_URL = "wss://stream.data.alpaca.markets/v2/sip"  # For real-time trades, quotes, bars

clients = set()

async def connect_to_alpaca(websocket: WebSocket, symbols: list):
    async with websockets.connect(settings.ALPACA_STREAM_URL) as alpaca_ws:
        auth_message = {
            "action": "auth",
            "key": settings.ALPACA_API_KEY,
            "secret": settings.ALPACA_API_SECRET
        }
        await alpaca_ws.send(json.dumps(auth_message))

        subscribe_message = {
            "action": "subscribe",
            "trades": symbols,  # List of stock symbols to track trades
            "quotes": symbols,
            "bars": symbols
        }
        await alpaca_ws.send(json.dumps(subscribe_message))

        while True:
            response = await alpaca_ws.recv()
            await websocket.send_text(response)

@router.websocket("/ws/market-data")
async def market_data(websocket: WebSocket, symbols: str):
    await websocket.accept()
    clients.add(websocket)
    symbol_list = symbols.split(",") if symbols else ["AAPL", "TSLA"]
    
    try:
        await connect_to_alpaca(websocket, symbol_list)
    except WebSocketDisconnect:
        clients.remove(websocket)
