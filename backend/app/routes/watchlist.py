from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Watchlist

router = APIRouter()

@router.get("")
@router.get("/")
async def get_watchlist(db: Session = Depends(get_db)):
    watchlist = db.query(Watchlist).all()
    if not watchlist:
        raise HTTPException(status_code=404, detail="No stocks in watchlist")
    return watchlist

@router.post("")
@router.post("/")
async def add_to_watchlist(symbol: str, db: Session = Depends(get_db)):
    existing = db.query(Watchlist).filter(Watchlist.symbol == symbol).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    new_stock = Watchlist(symbol=symbol)
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return {"message": f"{symbol} added to watchlist"}

@router.delete("/{symbol}")
async def remove_from_watchlist(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(Watchlist).filter(Watchlist.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found in watchlist")

    db.delete(stock)
    db.commit()
    return {"message": f"{symbol} removed from watchlist"}
