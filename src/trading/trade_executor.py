import alpaca_trade_api as tradeapi
from src.utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

def execute_trade(symbol, qty, side):
    """Execute a live trade."""
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')
    
    if side == "buy":
        api.submit_order(symbol=symbol, qty=qty, side="buy", type="market", time_in_force="gtc")
    elif side == "sell":
        api.submit_order(symbol=symbol, qty=qty, side="sell", type="market", time_in_force="gtc")

def run_live_trading():
    """Example live trading execution."""
    execute_trade(symbol="AAPL", qty=10, side="buy")
