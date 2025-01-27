import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta
from app.config import settings
from sqlalchemy.orm import Session
from app.models import StockPrice
from zoneinfo import ZoneInfo
import pandas as pd

class AlpacaService:
    def __init__(self):
        # Initialize trading and historical data clients
        self.trading_client = TradingClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            paper=True 
        )
        self.data_client = StockHistoricalDataClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY
        )
        self.logger = logging.getLogger("AlpacaService")

    def get_account_info(self):
        """
        Fetch account details from Alpaca.
        """
        account = self.trading_client.get_account()
        return account.__dict__  # Convert the account object to a dictionary

    def fetch_historical_data(self, symbols: list, start_date: str, end_date: str, timeframe: str = "1Day"):
        """
        Fetch historical stock data from Alpaca.

        Args:
            symbols (list): List of stock symbols.
            start_date (str): Start date (YYYY-MM-DD).
            end_date (str): End date (YYYY-MM-DD).
            timeframe (str): Timeframe for data ('1Day', '1Min', etc.).

        Returns:
            list[dict]: Historical stock data.
        """
        try:
            self.logger.info(f"Fetching historical data for symbols: {symbols}")

            # Convert timeframe string to Alpaca's TimeFrame
            alpaca_timeframe = (
                TimeFrame(amount=1, unit=TimeFrameUnit.Day) if timeframe == "1Day" else
                TimeFrame(amount=1, unit=TimeFrameUnit.Minute)
            )

            # Construct the request
            stock_bars_request = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=alpaca_timeframe,
                start=datetime.fromisoformat(start_date),
                end=datetime.fromisoformat(end_date),
            )

            # Fetch data using the constructed request
            bars = self.data_client.get_stock_bars(stock_bars_request).df

            # Debugging: Log DataFrame structure
            self.logger.info(f"DataFrame structure: {bars.head()}")
            self.logger.info(f"DataFrame columns: {bars.columns}")
            self.logger.info(f"DataFrame index: {bars.index}")

            # If 'symbol' is not a column, handle it from the index
            if "symbol" not in bars.columns:
                if isinstance(bars.index, pd.MultiIndex) and "symbol" in bars.index.names:
                    bars = bars.reset_index()  # Move 'symbol' from the index to a column
                else:
                    raise Exception("Symbol information is missing from the returned data.")

            # Ensure 'timestamp' is a datetime column
            if "timestamp" not in bars.columns:
                raise Exception("Timestamp column is missing in the returned data.")
            bars["timestamp"] = pd.to_datetime(bars["timestamp"])

            # Process the fetched data
            historical_data = []
            for _, row in bars.iterrows():
                historical_data.append({
                    "symbol": row["symbol"],
                    "datetime": row["timestamp"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                })

            self.logger.info(f"Successfully fetched data for {len(symbols)} symbols.")
            return historical_data

        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            raise Exception(f"Error fetching historical data: {str(e)}")

    def insert_historical_data(self, symbols: list, start_date: str, end_date: str, timeframe: str, db: Session):
        """
        Fetch and insert historical stock data into the database.

        Args:
            symbols (list): List of stock symbols.
            start_date (str): Start date (YYYY-MM-DD).
            end_date (str): End date (YYYY-MM-DD).
            timeframe (str): Timeframe for data ('1Day', '1Min', etc.).
            db (Session): SQLAlchemy session for database operations.

        Returns:
            int: Number of records successfully inserted.
        """
        try:
            # Fetch historical data
            historical_data = self.fetch_historical_data(symbols, start_date, end_date, timeframe)
            if not historical_data:
                self.logger.warning("No historical data fetched.")
                return 0

            # Prepare data for bulk insertion
            stock_prices = []
            for record in historical_data:
                try:
                    stock_price = StockPrice(
                        symbol=record["symbol"],
                        price=record["close"],
                        timestamp=record["datetime"]
                    )
                    stock_prices.append(stock_price)
                except KeyError as e:
                    self.logger.error(f"Missing key in record: {record}. Error: {e}")
                    continue

            # Insert all records in bulk
            if stock_prices:
                db.add_all(stock_prices)
                db.commit()
                self.logger.info(f"Inserted {len(stock_prices)} records into the database.")
                return len(stock_prices)
            else:
                self.logger.warning("No valid data to insert.")
                return 0

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error inserting historical data: {e}")
            raise Exception(f"Error inserting historical data: {str(e)}")

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
        side_enum = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side_enum,
            time_in_force=TimeInForce.GTC
        )
        order = self.trading_client.submit_order(order_request)
        return order.__dict__  # Convert order object to a dictionary
