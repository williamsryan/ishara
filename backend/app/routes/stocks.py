from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.alpaca_service import AlpacaService
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stock  # SQLAlchemy model
from app.schemas import Stock as StockSchema  # Pydantic schema

router = APIRouter()

@router.get("/stocks", response_model=list[StockSchema])
def read_stocks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    stocks = db.query(Stock).offset(skip).limit(limit).all()
    return stocks

@router.get("/stocks/{stock_id}", response_model=StockSchema)
def read_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.get("/stocks/search")
def search_stocks(query: str = Query(..., description="Stock symbol search query"), db: Session = Depends(get_db)):
    """
    Search for stock symbols that match the query.
    """
    alpaca_service = AlpacaService(db)
    results = alpaca_service.search_symbols(query)
    return results
