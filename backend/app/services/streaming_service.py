import asyncio
from threading import Thread
import logging
from alpaca.data.live import StockDataStream
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import StockPrice
from app.config import settings

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StreamingService")

# Database setup
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

# Alpaca API keys
API_KEY = settings.ALPACA_API_KEY
SECRET_KEY = settings.ALPACA_SECRET_KEY

# StockDataStream client
stock_stream_client = StockDataStream(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    url_override=None
)

# Handler for incoming data
async def stock_data_stream_handler(data):
    try:
        logger.info(f"Data received: {data}")
        # Save data to database
        record = StockPrice(
            symbol=data.symbol,
            price=data.bid_price or data.ask_price,
            open=data.bid_price,
            high=data.ask_price,
            low=data.bid_price,
            close=data.ask_price,
            volume=data.bid_size,
            timestamp=datetime.now()
        )
        db.add(record)
        db.commit()
        
        print(f"""
        ---- Trade Data ----
        Symbol: {data.symbol}
        Timestamp: {data.timestamp}
        Bid: {data.bid_price} (Size: {data.bid_size}, Exchange: {data.bid_exchange})
        Ask: {data.ask_price} (Size: {data.ask_size}, Exchange: {data.ask_exchange})
        Conditions: {data.conditions}
        Tape: {data.tape}
        --------------------
        """)

    except Exception as e:
        logger.error(f"Error saving data: {e}")

def run_stock_stream_client():
    stock_stream_client.run()

# Streaming function
async def start_streaming(symbols):
    """
    Start WebSocket streaming for the given symbols in a dedicated thread.
    """
    try:
        logger.info(f"Starting WebSocket streaming for symbols: {symbols}")
        stock_stream_client.subscribe_quotes(stock_data_stream_handler, *symbols)
        stock_stream_client.subscribe_trades(stock_data_stream_handler, *symbols)

        # Run in a dedicated thread
        thread = Thread(target=run_stock_stream_client)
        thread.start()
        thread.join()
    except Exception as e:
        logger.error(f"Error in streaming: {e}")
    finally:
        db.close()

# Main entry point
if __name__ == "__main__":
    import sys
    symbols = sys.argv[1:]  # Pass symbols as command-line arguments
    if not symbols:
        logger.error("No symbols provided. Usage: python streaming_service.py AAPL MSFT GOOGL")
        sys.exit(1)

    try:
        asyncio.run(start_streaming(symbols))
    except KeyboardInterrupt:
        logger.info("Streaming service stopped.")
