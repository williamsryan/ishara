from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.yahoo_service import YahooFinanceService
from app.services.alpaca_service import AlpacaService
from app.models import StockPrice
from app.schemas import Stock

router = APIRouter()

@router.post("/yahoo/{symbol}")
def fetch_yahoo_data(symbol: str, db: Session = Depends(get_db)):
    yahoo_service = YahooFinanceService()
    try:
        data = yahoo_service.fetch_stock_data(symbol)
        # Save to database or return data
        return {"message": f"Yahoo Finance data fetched for {symbol}", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data for {symbol}: {str(e)}")

@router.get("/alpaca/account")
def get_account_info():
    """
    Fetch Alpaca account details.
    """
    try:
        alpaca_service = AlpacaService()
        account_info = alpaca_service.get_account_info()
        return {"account_info": account_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch account info: {str(e)}")

@router.post("/alpaca/order")
def place_order(symbol: str, qty: int, side: str):
    """
    Place an order via Alpaca.
    Args:
        symbol (str): Stock symbol.
        qty (int): Quantity of shares.
        side (str): 'buy' or 'sell'.

    Returns:
        Order confirmation details.
    """
    try:
        alpaca_service = AlpacaService()
        order = alpaca_service.place_order(symbol, qty, side)
        return {"message": "Order placed successfully", "order": order}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

@router.get("/alpaca/historical/{symbol}")
def get_historical_data(symbol: str, days: int = 1):
    """
    Fetch historical data for a symbol from Alpaca.
    """
    try:
        alpaca_service = AlpacaService()
        data = alpaca_service.get_historical_data(symbol, days)
        return {"symbol": symbol, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(e)}")
        
