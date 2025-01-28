import yfinance as yf
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import HistoricalPrice, RealTimePrice

logger = logging.getLogger("YahooFinanceService")

class YahooFinanceService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def convert_unix_to_datetime(unix_timestamp):
        """
        Convert a Unix timestamp to a Python datetime object.
        """
        try:
            if unix_timestamp is None or str(unix_timestamp).strip() == "":
                return None
            return datetime.utcfromtimestamp(int(unix_timestamp))
        except (ValueError, TypeError):
            print(f"⚠️ Invalid Unix timestamp: {unix_timestamp}")
            return None

    @staticmethod
    def safe_convert(value, target_type, default=None):
        """
        Safely convert a value to a specified type.
        """
        try:
            if value is None or isinstance(value, (list, dict)):
                return default
            return target_type(value)
        except (ValueError, TypeError):
            return default

    def fetch_real_time_data(self, symbols):
        """
        Fetch real-time stock data and save to the database.
        """
        try:
            for symbol in symbols:
                logger.info(f"Fetching real-time data for {symbol}...")
                ticker = yf.Ticker(symbol)
                quote = ticker.info

                record = RealTimePrice(
                    symbol=symbol,
                    price=quote.get("regularMarketPrice"),
                    timestamp=datetime.utcnow(),
                )
                self.db.add(record)
            self.db.commit()
            logger.info("Real-time data fetched and saved successfully.")
        except Exception as e:
            logger.error(f"Error fetching real-time data: {e}")
            raise

    def fetch_yahoo_finance_data(self, symbols):
        """
        Fetch historical and key metrics data from Yahoo Finance.
        """
        data_to_insert = []
        options_data_to_insert = []

        for symbol in symbols:
            print(f"📊 Fetching Yahoo Finance data for {symbol}...")
            stock = yf.Ticker(symbol)

            # Fetch historical price data
            try:
                history = stock.history(period="1y", interval="1h")
            except Exception as e:
                print(f"⚠️ Failed to fetch historical data for {symbol}: {e}")
                history = None

            # Fetch stock info
            try:
                info = stock.info
            except Exception as e:
                print(f"⚠️ Failed to fetch stock info for {symbol}: {e}")
                info = {}

            # Fetch dividends and splits
            try:
                dividends = stock.dividends
                splits = stock.splits
            except Exception as e:
                print(f"⚠️ Failed to fetch dividends/splits for {symbol}: {e}")
                dividends, splits = None, None

            # Extract data for each row
            if history is not None:
                for date, row in history.iterrows():
                    data_to_insert.append({
                        "symbol": symbol,
                        "date": date,
                        "open": self.safe_convert(row.get("Open"), float),
                        "high": self.safe_convert(row.get("High"), float),
                        "low": self.safe_convert(row.get("Low"), float),
                        "close": self.safe_convert(row.get("Close"), float),
                        "volume": self.safe_convert(row.get("Volume"), int),
                        "dividend": self.safe_convert(dividends.get(date, None) if dividends else None, float),
                        "split": self.safe_convert(splits.get(date, None) if splits else None, float),
                    })

            # Fetch options data
            try:
                options = stock.options
                for expiration_date in options:
                    options_chain = stock.option_chain(expiration_date)
                    for option_type, data in zip(["call", "put"], [options_chain.calls, options_chain.puts]):
                        for _, row in data.iterrows():
                            options_data_to_insert.append({
                                "symbol": symbol,
                                "expiration_date": expiration_date,
                                "type": option_type,
                                "strike": self.safe_convert(row.get("strike"), float),
                                "last_price": self.safe_convert(row.get("lastPrice"), float),
                                "bid": self.safe_convert(row.get("bid"), float),
                                "ask": self.safe_convert(row.get("ask"), float),
                                "volume": self.safe_convert(row.get("volume"), int),
                                "open_interest": self.safe_convert(row.get("openInterest"), int),
                            })
            except Exception as e:
                print(f"⚠️ Failed to fetch options data for {symbol}: {e}")

        return data_to_insert, options_data_to_insert
        