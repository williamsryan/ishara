import logging
import asyncio
from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime
from app.config import settings
from app.models import StockPrice
from sqlalchemy.orm import Session
import pandas as pd

class AlpacaService:
    def __init__(self, db: Session):
        self.trading_client = TradingClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            paper=True
        )
        self.data_client = StockHistoricalDataClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY
        )
        self.stock_stream_client = StockDataStream(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            url_override=None
        )
        self.logger = logging.getLogger("AlpacaService")
        self.db = db

    def fetch_stock_data(self, symbols, start_date, end_date, timeframe="1Day"):
        """
        Fetch historical stock data from Alpaca and save to the database.
        """
        try:
            self.logger.info(f"Fetching stock data for symbols: {symbols}")
            timeframe_obj = TimeFrame.Day if timeframe == "1Day" else TimeFrame.Minute
            stock_request = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=timeframe_obj,
                start=datetime.fromisoformat(start_date),
                end=datetime.fromisoformat(end_date),
            )
            bars = self.data_client.get_stock_bars(stock_request).df
            bars["timestamp"] = pd.to_datetime(bars.index)
            records = [
                StockPrice(
                    symbol=row["symbol"],
                    price=row["close"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                    timestamp=row["timestamp"],
                )
                for _, row in bars.iterrows()
            ]
            self.db.add_all(records)
            self.db.commit()
            self.logger.info(f"Inserted {len(records)} stock price records into the database.")
        except Exception as e:
            self.logger.error(f"Error fetching stock data: {e}")
            raise

    async def stock_data_stream_handler(self, data):
        """
        Handle real-time streaming data and save to the database.
        """
        try:
            record = StockPrice(
                symbol=data.symbol,
                price=data.bid_price or data.ask_price,
                open=data.bid_price,  # Placeholder for real data
                high=data.ask_price,  # Placeholder for real data
                low=data.bid_price,   # Placeholder for real data
                close=data.ask_price, # Placeholder for real data
                volume=data.bid_size, # Placeholder for real data
                timestamp=data.timestamp
            )
            self.db.add(record)
            self.db.commit()
            self.logger.info(f"Inserted real-time data for {data.symbol} into the database.")

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
            self.logger.error(f"Error processing streaming data: {e}")
        