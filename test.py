import asyncio
from alpaca.data.live import StockDataStream

# Alpaca API credentials
ALPACA_API_KEY = "PKS83YQBEUPZL111E7NJ"
ALPACA_SECRET_KEY = "NDSora4h27DyMzn1vgRElYWr40gkDpkZTrzIXwvh"
ALPACA_WS_URL = "wss://stream.data.alpaca.markets/v2/iex"  # For IEX feed

# Initialize the StockDataStream client
stock_stream_client = StockDataStream(
    api_key=ALPACA_API_KEY,
    secret_key=ALPACA_SECRET_KEY,
)

# Handle received trade data
async def trade_handler(trade):
    print(f"Trade received: {trade}")
    # Process and insert data into the database

# Handle received bar (OHLC) data
async def bar_handler(bar):
    print(f"Bar received: {bar}")
    # Process and insert data into the database

async def main():
    # Subscribe to trades and bars for specific symbols
    symbols = ["AAPL", "MSFT", "GOOGL"]
    stock_stream_client.subscribe_trades(trade_handler, *symbols)
    stock_stream_client.subscribe_bars(bar_handler, *symbols)

    # Run the WebSocket connection
    print("Starting WebSocket...")
    # await stock_stream_client.run()
    await stock_stream_client._start_ws()
    print("WebSocket started.")
    await stock_stream_client._run_forever()
    print("WebSocket ran.")

if __name__ == "__main__":
    asyncio.run(main())