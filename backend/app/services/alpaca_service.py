import logging
import asyncio
from alpaca.data.live.stock import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime
from app.config import settings
from sqlalchemy.orm import Session
from app.models import StockPrice
from zoneinfo import ZoneInfo
import pandas as pd

class AlpacaService:
    def __init__(self):
        # Initialize trading, historical data, and live streaming clients
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
            url_override=settings.ALPACA_WS_URL,
        )
        self.trading_stream_client = TradingStream(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            url_override=settings.ALPACA_WS_URL,
            paper=True
        )
        self.logger = logging.getLogger("AlpacaService")

    def get_account_info(self):
        """
        Fetch account details from Alpaca.
        """
        account = self.trading_client.get_account()
        return account.__dict__  # Convert the account object to a dictionary

    def fetch_stock_data(self, symbols, start_date, end_date, timeframe, db: Session):
        """
        Fetch historical stock data from Alpaca and save to the database.
        """
        try:
            self.logger.info(f"Fetching stock data for symbols: {symbols}")
            timeframe_obj = TimeFrame(amount=1, unit=TimeFrameUnit.Day) if timeframe == "1Day" else TimeFrame.Minute
            stock_request = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=timeframe_obj,
                start=datetime.fromisoformat(start_date),
                end=datetime.fromisoformat(end_date),
            )
            bars = self.data_client.get_stock_bars(stock_request).df
            self.logger.info(f"Fetched stock data: {bars.head()}")

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

            db.add_all(records)
            db.commit()
            self.logger.info(f"Inserted {len(records)} stock price records into the database.")
        except Exception as e:
            self.logger.error(f"Error fetching stock data: {e}")
            raise

    async def stream_stock_data(self, symbols: list, db: Session):
        """
        Stream real-time stock data using Alpaca's StockDataStream client and save to the database.
        """
        try:
            self.logger.info(f"Starting real-time streaming for symbols: {symbols}")

            # Handler for real-time stock data
            async def stock_data_handler(data):
                self.logger.info(f"Received data: {data}")
                if "symbol" in data and "price" in data:
                    stock_price = StockPrice(
                        symbol=data["symbol"],
                        price=data["price"],
                        timestamp=data["timestamp"]
                    )
                    db.add(stock_price)
                    db.commit()
                    self.logger.info(f"Inserted real-time stock data for {data['symbol']} into the database.")

            # Subscribe to trades and quotes
            self.logger.info("Subscribing to quotes...")
            await self.stock_stream_client.subscribe_quotes(stock_data_handler, *symbols)

            self.logger.info("Subscribing to trades...")
            await self.stock_stream_client.subscribe_trades(stock_data_handler, *symbols)

            # Run the streaming client
            self.logger.info("Starting the WebSocket client...")
            await self.stock_stream_client.run()

        except Exception as e:
            self.logger.error(f"Error in streaming stock data: {e}")
            raise

    def place_order(self, symbol: str, qty: int, side: str):
        """
        Place a trade order via Alpaca.
        Args:
            symbol (str): Stock symbol to trade.
            qty (int): Quantity of shares to trade.
            side (str): 'buy' or 'sell'.

        Returns:
            Order object as a dictionary.
        """
        side_enum = "buy" if side.lower() == "buy" else "sell"
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side_enum,
            time_in_force="gtc"
        )
        order = self.trading_client.submit_order(order_request)
        return order.__dict__  # Convert order object to a dictionary
