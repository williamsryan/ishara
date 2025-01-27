from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stock
from app.schemas import Stock, StockCreate

router = APIRouter()

@router.get("/", response_model=list[Stock])
def get_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()

@router.post("/", response_model=Stock)
def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    db_stock = Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock
    