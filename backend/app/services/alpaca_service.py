from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient
from datetime import datetime, timedelta
import logging
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

    def fetch_historical_data(self, symbols, start_date, end_date, timeframe="1Day"):
        """
        Fetch and save historical stock data from Alpaca.
        """
        try:
            request_params = StockBarsRequest(
                symbol_or_symbols=symbols,
                start=start_date,
                end=end_date,
                timeframe=timeframe,
            )
            bars = self.data_client.get_stock_bars(request_params).df

            for (symbol, date), row in bars.iterrows():
                # Avoid duplicate entries
                exists = self.db.query(HistoricalPrice).filter(
                    HistoricalPrice.symbol == symbol,
                    HistoricalPrice.date == date.to_pydatetime()
                ).first()
                if exists:
                    logger.info(f"Skipping existing entry for {symbol} on {date}.")
                    continue

                # Insert new record
                record = HistoricalPrice(
                    symbol=symbol,
                    date=date.to_pydatetime(),
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                )
                self.db.add(record)

            self.db.commit()
            logger.info("Historical data fetched and saved successfully.")
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
        