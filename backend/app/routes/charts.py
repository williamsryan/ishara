from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import StockPrice
from app.config import settings
from app.services.yahoo_service import YahooFinanceService
from app.services.alpaca_service import AlpacaService
import logging

router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_yahoo_service(db: Session = Depends(get_db)):
    """Provides an instance of YahooFinanceService with a DB session."""
    return YahooFinanceService(db=db)

def get_alpaca_service(db: Session = Depends(get_db)):
    """Provides an instance of AlpacaService with a DB session."""
    return AlpacaService(db=db, api_key=settings.ALPACA_API_KEY, secret_key=settings.ALPACA_SECRET_KEY)

@router.get("/historical/")
def fetch_and_store_historical_data(
    symbols: str = Query(..., description="Comma-separated list of ticker symbols (e.g., 'AAPL,MSFT')"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    force_refresh: bool = Query(False, description="Force refetching of data from APIs"),
    db: Session = Depends(get_db),
    yahoo_service: YahooFinanceService = Depends(get_yahoo_service),
    alpaca_service: AlpacaService = Depends(get_alpaca_service),
):
    """
    Fetch historical data for given symbols and date range.
    Checks the database first; fetches missing data from external APIs if needed.

    Args:
        symbols (str): Comma-separated list of stock symbols.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        force_refresh (bool): If True, ignores cached data and refetches.

    Returns:
        dict: A dictionary containing dates and prices for each symbol.
    """
    try:
        # Parse input symbols and date range
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Query database for existing data
        db_data = (
            db.query(StockPrice)
            .filter(StockPrice.symbol.in_(symbol_list))
            .filter(StockPrice.timestamp >= start, StockPrice.timestamp <= end)
            .all()
        )

        # Organize existing data by symbol
        existing_data = {symbol: [] for symbol in symbol_list}
        for record in db_data:
            existing_data[record.symbol].append(record)

        # Determine missing symbols
        missing_symbols = [symbol for symbol in symbol_list if force_refresh or not existing_data[symbol]]

        fetched_data = []
        if missing_symbols:
            logger.info(f"Fetching data for missing symbols: {missing_symbols}")

            # Fetch data from external APIs
            yahoo_data = yahoo_service.fetch_historical_data(missing_symbols, (start_date, end_date))
            alpaca_data = alpaca_service.fetch_historical_data(missing_symbols, (start_date, end_date))

            # Merge and store fetched data
            fetched_data = yahoo_data + alpaca_data
            db.bulk_save_objects(fetched_data)
            db.commit()
            logger.info(f"Saved {len(fetched_data)} new records to database.")

        # Combine database and fetched data
        all_data = db_data + fetched_data
        response = {}
        for record in all_data:
            if record.symbol not in response:
                response[record.symbol] = {"timestamps": [], "prices": []}
            response[record.symbol]["timestamps"].append(record.timestamp.strftime("%Y-%m-%d"))
            response[record.symbol]["prices"].append(record.close)

        return response

    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

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
    try:
        historical_data = (
            db.query(StockPrice)
            .filter(StockPrice.symbol == symbol)
            .order_by(StockPrice.timestamp.desc())
            .limit(100)  # Fetch the latest 100 records
            .all()
        )

        if not historical_data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")

        return {
            "symbol": symbol,
            "dates": [data.timestamp.strftime("%Y-%m-%d") for data in historical_data],
            "prices": [data.close for data in historical_data],
        }

    except Exception as e:
        logger.error(f"Error retrieving chart data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chart data: {str(e)}")

@router.get("/")
@router.get("")
def get_all_charts(db: Session = Depends(get_db)):
    """
    Fetch chart data for all symbols in the database.
    """
    try:
        symbols_data = db.query(StockPrice).all()

        response = {}
        for record in symbols_data:
            if record.symbol not in response:
                response[record.symbol] = {"timestamps": [], "prices": []}
            response[record.symbol]["timestamps"].append(record.timestamp.strftime("%Y-%m-%d"))
            response[record.symbol]["prices"].append(record.close)

        return response
    except Exception as e:
        logger.error(f"Error retrieving all chart data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving all chart data: {str(e)}")
    