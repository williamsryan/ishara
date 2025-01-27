from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Portfolio
from app.schemas import Portfolio, PortfolioCreate

router = APIRouter()

@router.get("/", response_model=list[Portfolio])
def get_portfolio(db: Session = Depends(get_db)):
    return db.query(Portfolio).all()

@router.post("/", response_model=Portfolio)
def add_to_portfolio(portfolio_item: PortfolioCreate, db: Session = Depends(get_db)):
    db_portfolio_item = Portfolio(**portfolio_item.dict())
    db.add(db_portfolio_item)
    db.commit()
    db.refresh(db_portfolio_item)
    return db_portfolio_item
    