from pydantic import BaseModel
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.alpaca_service import AlpacaService

# Define the Pydantic model
class SymbolsRequest(BaseModel):
    symbols: List[str]  # List of stock symbols

router = APIRouter()

@router.post("/stocks")
def fetch_stock_data(
    symbols: list[str],
    start_date: str,
    end_date: str,
    timeframe: str = "1Day",
    db: Session = Depends(get_db),
):
    try:
        alpaca_service = AlpacaService()
        alpaca_service.fetch_stock_data(symbols, start_date, end_date, timeframe, db)
        return {"message": "Stock data fetched and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/options")
def fetch_options_data(
    symbols: list[str],
    expiration_dates: list[str],
    db: Session = Depends(get_db),
):
    try:
        alpaca_service = AlpacaService()
        alpaca_service.fetch_options_data(symbols, expiration_dates, db)
        return {"message": "Options data fetched and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_stock_stream(request: SymbolsRequest, db: Session = Depends(get_db)):
    """
    Start real-time stock data streaming.
    """
    try:
        alpaca_service = AlpacaService()
        await alpaca_service.stream_stock_data(request.symbols, db)
        return {"message": f"Streaming started for symbols: {request.symbols}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in streaming: {str(e)}")
