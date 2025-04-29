from fastapi import APIRouter, HTTPException
import requests
from app.config import settings

router = APIRouter()

ALPACA_NEWS_URL = "https://data.alpaca.markets/v1beta1/news"

@router.get("")
@router.get("/")
async def get_market_news(symbols: str = None):
    headers = {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY
    }
    
    params = {}
    if symbols:
        params["symbols"] = symbols  # Filter news by tickers

    response = requests.get(ALPACA_NEWS_URL, headers=headers, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch news")

    return response.json()
