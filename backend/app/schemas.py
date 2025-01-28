from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Stock schemas
class StockBase(BaseModel):
    symbol: str  # Stock symbol (e.g., AAPL)
    name: Optional[str] = None  # Name of the stock or company
    price: Optional[float] = None  # Current price of the stock
    open: Optional[float] = None  # Opening price
    high: Optional[float] = None  # Highest price of the day
    low: Optional[float] = None  # Lowest price of the day
    close: Optional[float] = None  # Closing price
    volume: Optional[int] = None  # Trading volume

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class OptionSchema(BaseModel):
    id: int
    symbol: str
    strike_price: float
    expiration_date: datetime
    option_type: str
    last_price: Optional[float]
    bid_price: Optional[float]
    ask_price: Optional[float]
    volume: Optional[int]
    open_interest: Optional[int]
    implied_volatility: Optional[float]
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True

# Portfolio schemas
class PortfolioBase(BaseModel):
    symbol: str
    shares: float
    avg_price: float

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int

    class Config:
        from_attributes = True
        
class SymbolsRequest(BaseModel):
    symbols: List[str]
