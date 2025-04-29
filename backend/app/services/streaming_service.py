import asyncio
from threading import Thread
import logging
from alpaca.data.live import StockDataStream
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import StockPrice, Trade
from app.config import settings

# Initialize logger
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.WARN)
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

class StreamingService:
    def __init__(self, symbols):
        self.symbols = symbols
        self.thread = None
        self.running = False

    # Handler for processing quote data
    async def quote_data_handler(self, data):
        """Handles incoming quote data from Alpaca."""
        try:
            # Save quote data to the database
            quote_record = StockPrice(
                symbol=data.symbol,
                price=data.bid_price or data.ask_price,  # Use bid_price if available, otherwise ask_price
                open=data.bid_price,  # Assign bid_price to open
                high=data.ask_price,  # Assign ask_price to high
                low=data.bid_price,   # Assign bid_price to low
                close=data.ask_price,  # Assign ask_price to close
                volume=data.bid_size,  # Assign bid_size to volume
                timestamp=datetime.now()  # Use the current timestamp
            )

            if settings.DEBUG:
                print(f"""
                ---- Quote Data ----
                Symbol: {data.symbol}
                Timestamp: {data.timestamp}
                Bid: {data.bid_price} (Size: {data.bid_size}, Exchange: {data.bid_exchange})
                Ask: {data.ask_price} (Size: {data.ask_size}, Exchange: {data.ask_exchange})
                Conditions: {data.conditions}
                Tape: {data.tape}
                --------------------
                """)

            db.add(quote_record)
            db.commit()
            db.close()

        except Exception as e:
            logger.error(f"Error processing quote data: {e}")

    # Handler for processing trade data
    async def trade_data_handler(self, data):
        """Handles incoming trade data from Alpaca."""
        try:
            # Extract trade data attributes
            symbol = getattr(data, "symbol", None)
            price = getattr(data, "price", None)  # Trade price
            size = getattr(data, "size", None)    # Trade size (volume)
            timestamp = getattr(data, "timestamp", None)  # Timestamp
            exchange = getattr(data, "exchange", None)  # Exchange where the trade occurred
            conditions = getattr(data, "conditions", None)  # Trade conditions
            tape = getattr(data, "tape", None)  # Trade tape identifier

            # Debug: Print trade data if DEBUG mode is enabled
            if settings.DEBUG:
                print(
                    f"Trade Data -> Symbol: {symbol}, Price: {price}, Size: {size}, "
                    f"Timestamp: {timestamp}, Exchange: {exchange}, Conditions: {conditions}, Tape: {tape}"
                )

            # Save trade data to the database
            trade_record = Trade(
                symbol=symbol,
                price=price,
                size=size,
                timestamp=timestamp,
                exchange=exchange,
                conditions=str(conditions),  # Store as a string for database compatibility
                tape=tape,
            )
            db.add(trade_record)
            db.commit()
            db.close()

        except Exception as e:
            logger.error(f"Error processing trade data: {e}")

    def run_streaming_client(self):
        """Run the StockDataStream client in a thread."""
        try:
            stock_stream_client.subscribe_quotes(self.quote_data_handler, *self.symbols)
            stock_stream_client.subscribe_trades(self.trade_data_handler, *self.symbols)
            stock_stream_client.run()
        except Exception as e:
            logger.error(f"Error running StockDataStream: {e}")

    def start(self):
        """Start the streaming service."""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.run_streaming_client)
            self.thread.start()
            logger.info("Streaming service started.")

    def stop(self):
        """Stop the streaming service."""
        if self.running and self.thread:
            stock_stream_client.stop()
            self.thread.join()
            self.running = False
            logger.info("Streaming service stopped.")

