from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stock
from app.schemas import Stock, StockCreate

router = APIRouter()

@router.get("/stocks", response_model=list[Stock])
def read_stocks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    stocks = db.query(Stock).offset(skip).limit(limit).all()
    return stocks

@router.get("/stocks/{stock_id}", response_model=Stock)
def read_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock
