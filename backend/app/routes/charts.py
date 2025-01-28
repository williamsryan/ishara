from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import StockPrice

router = APIRouter()

@router.get("/{symbol}")
def get_chart_data(symbol: str, db: Session = Depends(get_db)):
    """
    Fetch historical chart data for a given stock symbol from the database.

    Args:
        symbol (str): Stock symbol to fetch chart data for.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Dictionary containing dates and prices for the stock symbol.
    """
    # Query the database for historical price data
    historical_data = (
        db.query(StockPrice)
        .filter(StockPrice.symbol == symbol)
        .order_by(StockPrice.timestamp.desc())  # Sort by most recent
        .limit(100)  # Fetch the latest 100 records
        .all()
    )

    if not historical_data:
        raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")

    # Prepare chart data
    dates = [data.timestamp.strftime("%Y-%m-%d") for data in historical_data]
    prices = [data.close for data in historical_data]

    return {"symbol": symbol, "dates": dates, "prices": prices}

@router.get("/")
@router.get("")
def get_all_charts(db: Session = Depends(get_db)):
    """
    Fetch chart data for all symbols in the database.
    """
    try:
        symbols_data = db.query(StockPrice).all()

        # Format response: group by symbol
        response = {}
        for record in symbols_data:
            if record.symbol not in response:
                response[record.symbol] = {
                    "timestamps": [],
                    "prices": [],
                }
            response[record.symbol]["timestamps"].append(record.timestamp)
            response[record.symbol]["prices"].append(record.price)

        return response
    except Exception as e:
        return {"error": str(e)}
    