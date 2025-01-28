from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stock, StockPrice, Option, Trade, Portfolio, Earnings, KeyMetrics, HistoricalPrice, RealTimePrice

router = APIRouter()

@router.get("")
@router.get("/")
def get_portfolio(db: Session = Depends(get_db)):
    """
    Returns all relevant financial data for the portfolio, grouped by type.
    """
    return {
        "stocks": db.query(Stock).all(),
        "stock_prices": db.query(StockPrice).all(),
        "options": db.query(Option).all(),
        "trades": db.query(Trade).all(),
        "portfolio": db.query(Portfolio).all(),
        "earnings": db.query(Earnings).all(),
        "key_metrics": db.query(KeyMetrics).all(),
        "historical_prices": db.query(HistoricalPrice).all(),
        "real_time_prices": db.query(RealTimePrice).all(),
    }
