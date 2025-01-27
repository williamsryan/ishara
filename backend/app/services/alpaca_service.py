from app.config import settings
import alpaca_trade_api as tradeapi

class AlpacaService:
    def __init__(self):
        self.api = tradeapi.REST(
            key_id=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            base_url=settings.ALPACA_BASE_URL
        )

    def get_account_info(self):
        """
        Fetch account details from Alpaca.
        """
        return self.api.get_account()

    def place_order(self, symbol: str, qty: float, side: str, type: str = "market", time_in_force: str = "gtc"):
        """
        Place a trade order via Alpaca.
        """
        return self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            time_in_force=time_in_force
        )
        