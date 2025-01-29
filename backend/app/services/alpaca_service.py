from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta
import logging
import numpy as np
from sqlalchemy.orm import Session
from app.models import HistoricalPrice

logger = logging.getLogger("AlpacaService")

class AlpacaService:
    def __init__(self, db: Session, api_key: str, secret_key: str):
        self.data_client = StockHistoricalDataClient(
            api_key=api_key,
            secret_key=secret_key,
        )
        self.trading_client = TradingClient(
            api_key=api_key,
            secret_key=secret_key,
        )
        self.logger = logging.getLogger("AlpacaService")
        self.db = db

    @staticmethod
    def safe_convert(value, target_type, default=None):
        """
        Safely convert a value to a specified type, handling NumPy types.

        Args:
            value: The value to convert.
            target_type: The type to convert to (e.g., float, int).
            default: The default value to return if conversion fails.

        Returns:
            Converted value in target_type or default if conversion fails.
        """
        try:
            if value is None or isinstance(value, (list, dict)):  # Ensure value is not a complex type
                return default
            
            # Handle NumPy numeric types
            if isinstance(value, (np.float64, np.float32, np.int64, np.int32)):
                value = value.item()  # Convert NumPy types to Python native

            return target_type(value)
        except (ValueError, TypeError):
            return default

    def search_symbols(self, query: str):
        """
        Fetch stock symbol suggestions from Alpaca using TradingClient.

        Args:
            query (str): Search term for stock symbols.

        Returns:
            list: A list of matching stock symbols and their names.
        """
        try:
            # Use TradingClient to fetch all tradable assets
            assets = self.trading_client.get_all_assets(status="active")

            # Filter the results based on the query
            matching_assets = [
                {"symbol": asset.symbol, "name": asset.name}
                for asset in assets if query.upper() in asset.symbol
            ]

            return matching_assets
        except Exception as e:
            self.logger.error(f"Error searching symbols: {e}")
            return []

    def fetch_historical_data(self, symbols: list, date_range: tuple):
        """
        Fetch historical stock data from Alpaca.

        Args:
            symbols (list): List of stock symbols.
            date_range (tuple): Tuple containing start_date and end_date in YYYY-MM-DD format.

        Returns:
            List of StockPrice objects to be inserted into the database.
        """
        start_date, end_date = date_range  # Unpack tuple

        try:
            logger.info(f"📊 Fetching Alpaca historical data for {symbols} from {start_date} to {end_date}...")

            request = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=TimeFrame(amount=1, unit=TimeFrameUnit.Day),  # ✅ Correct TimeFrame format
                start=datetime.strptime(start_date, "%Y-%m-%d"),
                end=datetime.strptime(end_date, "%Y-%m-%d"),
            )

            bars = self.data_client.get_stock_bars(request).df

            if bars.empty:
                logger.warning(f"⚠️ No historical data found for {symbols}.")
                return []

            # Convert DataFrame into StockPrice objects
            stock_prices = []
            for symbol in symbols:
                if symbol in bars.index:
                    for _, row in bars.loc[symbol].iterrows():
                        stock_prices.append(HistoricalPrice(
                            symbol=symbol,
                            date=row.name.to_pydatetime(),
                            open=self.safe_convert(row["open"], float),
                            high=self.safe_convert(row["high"], float),
                            low=self.safe_convert(row["low"], float),
                            close=self.safe_convert(row["close"], float),
                            volume=self.safe_convert(row["volume"], int),
                            timestamp=datetime.utcnow(),
                            source="Alpaca"
                        ))

            return stock_prices
        except Exception as e:
            logger.error(f"❌ Error fetching Alpaca historical data: {e}")
            return []
        