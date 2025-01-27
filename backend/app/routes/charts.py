from fastapi import APIRouter
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/{symbol}")
def get_chart_data(symbol: str):
    # Simulated chart data
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(10)]
    prices = [round(random.uniform(100, 200), 2) for _ in range(10)]
    return {"symbol": symbol, "dates": dates, "prices": prices}
    