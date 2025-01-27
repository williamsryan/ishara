from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.yahoo_service import YahooFinanceService
from app.services.alpaca_service import AlpacaService
from app.models import StockPrice
from app.schemas import Stock

router = APIRouter()

# Define the request schema using Pydantic
class HistoricalDataRequest(BaseModel):
    symbols: list[str]      # List of stock symbols
    start_date: str         # Start date in YYYY-MM-DD format
    end_date: str           # End date in YYYY-MM-DD format
    timeframe: str = "1Day" # Timeframe, default is "1Day"

@router.post("/yahoo/{symbol}")
def fetch_yahoo_data(symbol: str, db: Session = Depends(get_db)):
    yahoo_service = YahooFinanceService()
    try:
        data = yahoo_service.fetch_yahoo_finance_data(symbol)
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

@router.post("/alpaca/historical")
def fetch_and_store_historical_data(
    request: HistoricalDataRequest,  # Automatically validate request body
    db: Session = Depends(get_db)
):
    """
    Fetch historical data from Alpaca for multiple symbols and store it in the database.
    """
    alpaca_service = AlpacaService()
    try:
        # Call AlpacaService to fetch and store data
        record_count = alpaca_service.insert_historical_data(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            timeframe=request.timeframe,
            db=db
        )
        return {"message": f"Historical data for {len(request.symbols)} symbols inserted successfully.", "count": record_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

