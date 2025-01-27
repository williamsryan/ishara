from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

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
    symbol = Column(String, index=True)  # Foreign key to Stock.symbol
    action = Column(String)  # 'BUY' or 'SELL'
    quantity = Column(Float)
    price = Column(Float)
    total_cost = Column(Float, nullable=True)  # Total cost of the trade
    timestamp = Column(DateTime)  # Time of the trade

class OptionData(Base):
    __tablename__ = "option_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Underlying stock symbol
    expiration_date = Column(DateTime, index=True)  # Expiration date
    option_type = Column(String)  # 'CALL' or 'PUT'
    strike_price = Column(Float)
    last_price = Column(Float, nullable=True)  # Last traded price
    bid = Column(Float, nullable=True)  # Bid price
    ask = Column(Float, nullable=True)  # Ask price
    volume = Column(Integer, nullable=True)  # Option volume
    open_interest = Column(Integer, nullable=True)  # Open interest
    implied_volatility = Column(Float, nullable=True)  # Implied volatility percentage

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
