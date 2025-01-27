from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.timeframe import TimeFrame
from app.config import settings
from datetime import datetime, timedelta

class AlpacaService:
    def __init__(self):
        # Initialize trading and historical data clients
        self.trading_client = TradingClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            paper=True  # Set to True for paper trading
        )
        self.data_client = StockHistoricalDataClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY
        )

    def get_account_info(self):
        """
        Fetch account details from Alpaca.
        """
        account = self.trading_client.get_account()
        return account.__dict__  # Convert the account object to a dictionary

    def get_historical_data(self, symbol: str, days: int = 1):
        """
        Fetch historical price data for a symbol from Alpaca.
        Args:
            symbol (str): Stock symbol.
            days (int): Number of days to fetch data for.

        Returns:
            List of dictionaries with datetime and close price.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        bars = self.data_client.get_stock_bars(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Minute,
            start=start_date,
            end=end_date,
        )
        return [
            {"Datetime": bar.timestamp, "Close": bar.close}
            for bar in bars[symbol]
        ]

    def place_order(self, symbol: str, qty: int, side: str):
        """
        Place a trade order via Alpaca.
        Args:
            symbol (str): Stock symbol to trade.
            qty (int): Quantity of shares to trade.
            side (str): 'buy' or 'sell'.

        Returns:
            Order object as a dictionary.
        """
        side_enum = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side_enum,
            time_in_force=TimeInForce.GTC
        )
        order = self.trading_client.submit_order(order_request)
        return order.__dict__  # Convert order object to a dictionary
        