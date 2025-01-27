from app.config import settings
import yfinance as yf

class YahooFinanceService:
    def fetch_stock_data(self, symbol: str):
        """
        Fetch stock price data for a given symbol from Yahoo Finance.
        """
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d", interval="1m")
        prices = hist.reset_index().to_dict(orient="records")
        return prices
        