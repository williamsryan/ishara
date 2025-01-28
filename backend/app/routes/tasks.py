from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.yahoo_service import YahooFinanceService
from app.services.alpaca_service import AlpacaService
from app.config import settings
from pydantic import BaseModel

router = APIRouter()

class SymbolsRequest(BaseModel):
    symbols: list[str]

@router.post("/yahoo/historical")
def fetch_yahoo_historical(request: SymbolsRequest, db: Session = Depends(get_db)):
    """
    Fetch historical stock data from Yahoo Finance for given symbols.
    """
    if not request.symbols:
        raise HTTPException(status_code=400, detail="No symbols provided.")
    
    yahoo_service = YahooFinanceService(db)
    try:
        # Pass the actual list of symbols to the service
        yahoo_service.fetch_historical_data(request.symbols)
        return {"message": f"Historical data for {', '.join(request.symbols)} has been fetched and stored."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Yahoo Finance data: {e}")

@router.post("/yahoo/options")
def fetch_yahoo_options(symbols: list[str], db: Session = Depends(get_db)):
    """
    Fetch options data from Yahoo Finance for given symbols.
    """
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided.")
    
    yahoo_service = YahooFinanceService(db)
    try:
        yahoo_service.fetch_historical_data(symbols)  # Includes options fetching
        return {"message": f"Options data for {', '.join(symbols)} has been fetched and stored."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Yahoo Finance options data: {e}")

@router.post("/alpaca/historical")
def fetch_alpaca_historical(symbols: list[str], start_date: str, end_date: str, db: Session = Depends(get_db)):
    """
    Fetch historical stock data from Alpaca for given symbols and date range.
    """
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided.")
    
    alpaca_service = AlpacaService(db, settings.ALPACA_API_KEY, settings.ALPACA_SECRET_KEY)
    try:
        alpaca_service.fetch_historical_data(symbols, start_date, end_date)
        return {"message": f"Historical data for {', '.join(symbols)} has been fetched and stored."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Alpaca historical data: {e}")

# @router.post("/tasks/alpaca/realtime")
# def fetch_alpaca_realtime(symbols: list[str], db: Session = Depends(get_db)):
#     """
#     Start real-time streaming of stock data from Alpaca for given symbols.
#     """
#     if not symbols:
#         raise HTTPException(status_code=400, detail="No symbols provided.")
    
#     alpaca_service = AlpacaService(db, settings.ALPACA_API_KEY, settings.ALPACA_SECRET_KEY)
#     try:
#         alpaca_service.stream_stock_data(symbols)
#         return {"message": f"Real-time streaming for {', '.join(symbols)} has started."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error starting Alpaca real-time streaming: {e}")

@router.post("/alpaca/options")
def fetch_alpaca_options(symbols: list[str], db: Session = Depends(get_db)):
    """
    Fetch options data from Alpaca for given symbols.
    """
    # Add the implementation for Alpaca options data fetching when ready
    return {"message": "Options data fetching from Alpaca is not implemented yet."}
