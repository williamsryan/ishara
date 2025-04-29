from pydantic import BaseModel
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.alpaca_service import AlpacaService
from app.services.yahoo_service import YahooFinanceService
from app.schemas import SymbolsRequest

router = APIRouter()

# @router.post("/stocks")
# def fetch_stock_data(
#     symbols: list[str],
#     start_date: str,
#     end_date: str,
#     timeframe: str = "1Day",
#     db: Session = Depends(get_db),
# ):
#     try:
#         alpaca_service = AlpacaService(db)
#         alpaca_service.fetch_stock_data(symbols, start_date, end_date, timeframe)
#         return {"message": "Stock data fetched and saved successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/options")
# def fetch_options_data(
#     symbols: list[str],
#     expiration_dates: list[str],
#     db: Session = Depends(get_db),
# ):
#     try:
#         alpaca_service = AlpacaService(db)
#         alpaca_service.fetch_options_data(symbols, expiration_dates)
#         return {"message": "Options data fetched and saved successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/historical")
# def fetch_historical(
#     symbols: list[str],
#     start_date: str,
#     end_date: str,
#     db: Session = Depends(get_db),
# ):
#     yahoo_service = YahooFinanceService(db)
#     yahoo_service.fetch_historical_data(symbols, start_date, end_date)
#     return {"message": "Historical data fetched and saved successfully."}

@router.post("/real-time")
def fetch_real_time(symbols: list[str], db: Session = Depends(get_db)):
    yahoo_service = YahooFinanceService(db)
    yahoo_service.fetch_real_time_data(symbols)
    return {"message": "Real-time data fetched and saved successfully."}
    