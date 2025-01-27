from pydantic import BaseModel

# Stock schemas
class StockBase(BaseModel):
    symbol: str
    name: str
    price: float

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int

    class Config:
        orm_mode = True

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
        orm_mode = True
        