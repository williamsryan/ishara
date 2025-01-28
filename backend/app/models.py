from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class DataType(enum.Enum):
    HISTORICAL = "historical"
    REALTIME = "realtime"

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)  # Stock name (e.g., Apple Inc.)
    sector = Column(String, nullable=True)  # Sector (e.g., Technology)
    industry = Column(String, nullable=True)  # Industry (e.g., Consumer Electronics)
    market_cap = Column(Float, nullable=True)  # Market capitalization
    beta = Column(Float, nullable=True)  # Beta value
    dividend_yield = Column(Float, nullable=True)  # Dividend yield percentage
    pe_ratio = Column(Float, nullable=True)  # Price-to-earnings ratio
    created_at = Column(DateTime)  # Timestamp when the stock was added

    # Relationships
    prices = relationship("StockPrice", back_populates="stock")

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)  # Stock symbol (e.g., AAPL)
    strike_price = Column(Float, nullable=False)         # Strike price of the option
    expiration_date = Column(DateTime, nullable=False)   # Expiration date of the option
    option_type = Column(String, nullable=False)         # Option type: 'call' or 'put'
    last_price = Column(Float)                           # Last traded price
    bid_price = Column(Float)                            # Bid price
    ask_price = Column(Float)                            # Ask price
    volume = Column(Integer)                             # Trading volume
    open_interest = Column(Integer)                      # Open interest
    implied_volatility = Column(Float)                   # Implied volatility
    timestamp = Column(DateTime)                         # Timestamp of the data

    def __repr__(self):
        return (f"<Option(symbol={self.symbol}, strike_price={self.strike_price}, "
                f"expiration_date={self.expiration_date}, option_type={self.option_type}, "
                f"last_price={self.last_price}, bid_price={self.bid_price}, "
                f"ask_price={self.ask_price}, volume={self.volume}, "
                f"open_interest={self.open_interest}, "
                f"implied_volatility={self.implied_volatility}, timestamp={self.timestamp})>")

# TODO: use this generic later to consolidate data
# class Price(Base):
#     __tablename__ = "prices"

#     id = Column(Integer, primary_key=True, index=True)
#     symbol = Column(String, nullable=False, index=True)  # Stock symbol (e.g., AAPL)
#     timestamp = Column(DateTime, nullable=False, index=True)  # Time of the price data
#     open = Column(Float, nullable=True)
#     high = Column(Float, nullable=True)
#     low = Column(Float, nullable=True)
#     close = Column(Float, nullable=True)
#     volume = Column(Integer, nullable=True)
#     bid = Column(Float, nullable=True)  # For real-time prices
#     ask = Column(Float, nullable=True)  # For real-time prices
#     data_type = Column(Enum(DataType), nullable=False)  # Either "historical" or "realtime"

#     # Prevent duplicates (symbol + timestamp + data_type must be unique)
#     __table_args__ = (
#         UniqueConstraint("symbol", "timestamp", "data_type", name="uq_symbol_timestamp_data_type"),
#     )
    
class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Foreign key to Stock.symbol
    price = Column(Float)
    open = Column(Float, nullable=True)  # Opening price
    high = Column(Float, nullable=True)  # High price
    low = Column(Float, nullable=True)  # Low price
    close = Column(Float, nullable=True)  # Closing price
    volume = Column(Integer, nullable=True)  # Trade volume
    timestamp = Column(DateTime, index=True)  # Time of the price record

    # Relationships
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    stock = relationship("Stock", back_populates="prices")

class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Foreign key to Stock.symbol
    shares = Column(Float, nullable=False)  # Number of shares owned
    avg_price = Column(Float, nullable=False)  # Average price per share
    total_cost = Column(Float, nullable=True)  # Total cost of the position
    created_at = Column(DateTime)  # Timestamp when the portfolio entry was created

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)  # Stock symbol (e.g., AAPL)
    price = Column(Float, nullable=False)    # Trade price
    size = Column(Integer, nullable=False)   # Trade size (volume)
    timestamp = Column(DateTime, nullable=False)  # Trade timestamp
    exchange = Column(String)  # Exchange where the trade occurred
    conditions = Column(String)  # Trade conditions as a string (can store as JSON if needed)
    tape = Column(String)  # Trade tape identifier

class Earnings(Base):
    __tablename__ = "earnings"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Foreign key to Stock.symbol
    earnings_date = Column(DateTime, index=True)  # Date of earnings report
    eps = Column(Float, nullable=True)  # Earnings per share
    revenue = Column(Float, nullable=True)  # Revenue in millions
    forecast_eps = Column(Float, nullable=True)  # Forecasted EPS
    actual_eps = Column(Float, nullable=True)  # Actual EPS
    surprise_percent = Column(Float, nullable=True)  # EPS surprise percentage

class KeyMetrics(Base):
    __tablename__ = "key_metrics"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Foreign key to Stock.symbol
    metric_name = Column(String, nullable=False)  # Name of the metric (e.g., P/E ratio, Debt/Equity)
    value = Column(Float, nullable=True)  # Metric value
    timestamp = Column(DateTime)  # Time when the metric was recorded

class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    dividend = Column(Float, nullable=True) 
    split = Column(Float, nullable=True) 

class RealTimePrice(Base):
    __tablename__ = "real_time_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)
