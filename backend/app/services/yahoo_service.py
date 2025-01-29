import yfinance as yf
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import HistoricalPrice, RealTimePrice, Option

logger = logging.getLogger("YahooFinanceService")

class YahooFinanceService:
    def __init__(self, db: Session):
        self.db = db

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

    def fetch_historical_data(self, symbols: list, date_range: tuple):
        """
        Fetch historical stock data and options data for a list of symbols within a given date range.

        Args:
            symbols (list): List of stock symbols to fetch data for.
            date_range (tuple): A tuple of (start_date, end_date) in `YYYY-MM-DD` format.

        Returns:
            list: A list of `HistoricalPrice` and `Option` objects.
        """
        start_date, end_date = date_range  # Unpack the tuple
        historical_data = []
        options_data = []

        for symbol in symbols:
            logger.info(f"📊 Fetching Yahoo Finance data for {symbol} from {start_date} to {end_date}...")
            stock = yf.Ticker(symbol)

            # Fetch historical price data within the date range
            try:
                history = stock.history(start=start_date, end=end_date, interval="1d")
                if history.empty:
                    logger.warning(f"⚠️ No historical data found for {symbol} within {start_date} to {end_date}.")
                    continue
            except Exception as e:
                logger.error(f"❌ Failed to fetch historical data for {symbol}: {e}")
                continue

            # Fetch dividends and splits
            dividends, splits = {}, {}
            try:
                dividends = stock.dividends.to_dict() if not stock.dividends.empty else {}
                splits = stock.splits.to_dict() if not stock.splits.empty else {}
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch dividends/splits for {symbol}: {e}")

            # Save historical data
            for date, row in history.iterrows():
                date = date.to_pydatetime()

                # Ensure we don't duplicate data
                exists = self.db.query(HistoricalPrice).filter(
                    HistoricalPrice.symbol == symbol,
                    HistoricalPrice.date == date
                ).first()
                if exists:
                    logger.info(f"Skipping existing record for {symbol} on {date}.")
                    continue

                historical_data.append(HistoricalPrice(
                    symbol=symbol,
                    date=date,
                    open=self.safe_convert(row.get("Open"), float),
                    high=self.safe_convert(row.get("High"), float),
                    low=self.safe_convert(row.get("Low"), float),
                    close=self.safe_convert(row.get("Close"), float),
                    volume=self.safe_convert(row.get("Volume"), int),
                    dividend=self.safe_convert(dividends.get(date, None), float),
                    split=self.safe_convert(splits.get(date, None), float),
                    source="Yahoo Finance",
                ))

            # Fetch options data within the date range
            try:
                options = stock.options
                for expiration_date in options:
                    expiration_datetime = datetime.strptime(expiration_date, "%Y-%m-%d")
                    if not (start_date <= expiration_date <= end_date):  # Ensure expiration falls within range
                        continue

                    options_chain = stock.option_chain(expiration_date)
                    for option_type, data in zip(["call", "put"], [options_chain.calls, options_chain.puts]):
                        for _, row in data.iterrows():
                            options_data.append(Option(
                                symbol=symbol,
                                strike_price=self.safe_convert(row.get("strike"), float),
                                expiration_date=expiration_datetime,
                                option_type=option_type,
                                last_price=self.safe_convert(row.get("lastPrice"), float),
                                bid_price=self.safe_convert(row.get("bid"), float),
                                ask_price=self.safe_convert(row.get("ask"), float),
                                volume=self.safe_convert(row.get("volume"), int),
                                open_interest=self.safe_convert(row.get("openInterest"), int),
                                implied_volatility=self.safe_convert(row.get("impliedVolatility"), float),
                                # timestamp=datetime.utcnow(),
                            ))
            except Exception as e:
                logger.error(f"⚠️ Failed to fetch options data for {symbol}: {e}")

        # Insert data into the database
        try:
            if historical_data:
                self.db.bulk_save_objects(historical_data)
            if options_data:
                self.db.bulk_save_objects(options_data)
            self.db.commit()
            logger.info(f"✅ Historical and options data fetched for {len(symbols)} symbols.")
        except Exception as e:
            logger.error(f"⚠️ Failed to save data to the database: {e}")
            self.db.rollback()

        # ✅ Ensure this function always returns lists, avoiding `NoneType` errors
        return historical_data + options_data

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
                    price=self.safe_convert(quote.get("regularMarketPrice"), float),
                    timestamp=datetime.utcnow(),
                )
                self.db.add(record)
            self.db.commit()
            logger.info("✅ Real-time data fetched successfully.")
        except Exception as e:
            logger.error(f"⚠️ Error fetching real-time data: {e}")
