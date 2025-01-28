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

    def fetch_historical_data(self, symbols):
        """
        Fetch historical stock data and options data for a list of symbols.
        """
        data_to_insert = []
        options_data_to_insert = []

        for symbol in symbols:
            logger.info(f"📊 Fetching Yahoo Finance data for {symbol}...")
            stock = yf.Ticker(symbol)

            # Fetch historical price data
            try:
                history = stock.history(period="1y", interval="1h")
            except Exception as e:
                logger.error(f"⚠️ Failed to fetch historical data for {symbol}: {e}")
                continue

            # Fetch dividends and splits
            dividends, splits = None, None
            try:
                dividends = stock.dividends
                splits = stock.splits
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch dividends/splits for {symbol}: {e}")

            # Save historical data
            for date, row in history.iterrows():
                # Ensure the date is a Python datetime object
                date = date.to_pydatetime()

                # Check for duplicates
                exists = self.db.query(HistoricalPrice).filter(
                    HistoricalPrice.symbol == symbol,
                    HistoricalPrice.date == date
                ).first()
                if exists:
                    logger.info(f"Skipping existing record for {symbol} on {date}.")
                    continue

                # Add the data to the insertion list
                data_to_insert.append(HistoricalPrice(
                    symbol=symbol,
                    date=date,
                    open=self.safe_convert(row.get("Open"), float),
                    high=self.safe_convert(row.get("High"), float),
                    low=self.safe_convert(row.get("Low"), float),
                    close=self.safe_convert(row.get("Close"), float),
                    volume=self.safe_convert(row.get("Volume"), int),
                    dividend=self.safe_convert(dividends.get(date, None) if dividends is not None else None, float),
                    split=self.safe_convert(splits.get(date, None) if splits is not None else None, float),
                ))

            # Fetch options data
            try:
                options = stock.options
                for expiration_date in options:
                    options_chain = stock.option_chain(expiration_date)
                    for option_type, data in zip(["call", "put"], [options_chain.calls, options_chain.puts]):
                        for _, row in data.iterrows():
                            options_data_to_insert.append(Option(
                                symbol=symbol,
                                strike_price=self.safe_convert(row.get("strike"), float),         # Match strike_price in model
                                expiration_date=datetime.strptime(expiration_date, "%Y-%m-%d"),  # Convert expiration_date to datetime
                                option_type=option_type,                                         # 'call' or 'put'
                                last_price=self.safe_convert(row.get("lastPrice"), float),       # Match last_price in model
                                bid_price=self.safe_convert(row.get("bid"), float),              # Match bid_price in model
                                ask_price=self.safe_convert(row.get("ask"), float),              # Match ask_price in model
                                volume=self.safe_convert(row.get("volume"), int),                # Match volume in model
                                open_interest=self.safe_convert(row.get("openInterest"), int),   # Match open_interest in model
                                implied_volatility=self.safe_convert(row.get("impliedVolatility"), float),  # Match implied_volatility in model
                                timestamp=datetime.utcnow(),                                     # Set the current timestamp
                            ))
            except Exception as e:
                logger.error(f"⚠️ Failed to fetch options data for {symbol}: {e}")

        # Insert data into the database
        try:
            if data_to_insert:
                self.db.bulk_save_objects(data_to_insert)
            if options_data_to_insert:
                self.db.bulk_save_objects(options_data_to_insert)
            self.db.commit()
            logger.info(f"✅ Historical and options data fetched for {len(symbols)} symbols.")
        except Exception as e:
            logger.error(f"⚠️ Failed to save data to the database: {e}")
            self.db.rollback()

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
