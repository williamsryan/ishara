from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.yahoo_service import YahooFinanceService
from app.services.alpaca_service import AlpacaService
from app.models import StockPrice
from app.schemas import Stock

router = APIRouter()

@router.get("/yahoo/{symbol}")
def fetch_yahoo_data(symbol: str, db: Session = Depends(get_db)):
    """
    Fetch stock data for a symbol from Yahoo Finance.
    """
    yahoo_service = YahooFinanceService()
    data = yahoo_service.fetch_stock_data(symbol)

    # Save data to the database
    for record in data:
        db_record = StockPrice(
            symbol=symbol,
            price=record["Close"],
            timestamp=record["Datetime"]
        )
        db.add(db_record)
    db.commit()

    return {"message": f"Stock data for {symbol} fetched successfully", "data": data}

@router.get("/alpaca/account")
def get_alpaca_account():
    """
    Fetch account information from Alpaca.
    """
    alpaca_service = AlpacaService()
    account_info = alpaca_service.get_account_info()
    return account_info

@router.post("/alpaca/order")
def place_alpaca_order(symbol: str, qty: float, side: str):
    """
    Place a trade order via Alpaca.
    """
    alpaca_service = AlpacaService()
    order = alpaca_service.place_order(symbol, qty, side)
    return order
    