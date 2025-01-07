from zipline.api import order, record, symbol, schedule_function, date_rules, time_rules
from zipline import run_algorithm
from zipline.data.data_portal import DataPortal
from zipline.data.bundles.core import load
from zipline.data.us_equity_pricing import BcolzDailyBarReader
from zipline.utils.calendars import get_calendar
import pandas as pd
from datetime import datetime
from src.utils.database import fetch_data

class BacktesterZipline:
    def __init__(self, symbols, start_date, end_date, strategy, capital=100000):
        """
        Initialize the BacktesterZipline.

        Args:
            symbols (list): List of stock symbols.
            start_date (str): Start date (YYYY-MM-DD).
            end_date (str): End date (YYYY-MM-DD).
            strategy (BaseStrategy): User-defined trading strategy.
            capital (float): Initial capital for the backtest.
        """
        self.symbols = symbols
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.strategy = strategy
        self.capital = capital
        self.data = None

    def fetch_historical_data(self):
        """
        Fetch historical data from the `historical_market_data` table.
        """
        query = f"""
            SELECT datetime, symbol, open, high, low, close, volume
            FROM historical_market_data
            WHERE symbol IN ({', '.join([f"'{s}'" for s in self.symbols])})
              AND datetime BETWEEN '{self.start_date}' AND '{self.end_date}'
            ORDER BY datetime
        """
        data = fetch_data(query)
        if data.empty:
            raise ValueError("No data available for the specified symbols and date range.")
        
        # Reshape data to Zipline-compatible format
        data["date"] = pd.to_datetime(data["datetime"])
        data.set_index(["date", "symbol"], inplace=True)
        data = data.unstack(level=-1)  # Unstack for multi-column format
        self.data = data

    def run(self):
        """
        Run the backtest with the provided strategy.
        """
        self.fetch_historical_data()

        # Create a Zipline-compatible calendar
        trading_calendar = get_calendar("XNYS")  # Adjust to your market's calendar

        # Create a DataPortal with the historical data
        equity_daily_bar_reader = BcolzDailyBarReader(self.data)
        data_portal = DataPortal(
            asset_finder=None,  # Custom assets can be added here
            trading_calendar=trading_calendar,
            equity_daily_reader=equity_daily_bar_reader,
        )

        # Run the backtest
        results = run_algorithm(
            start=self.start_date,
            end=self.end_date,
            capital_base=self.capital,
            data_frequency="daily",
            initialize=self.strategy.initialize,
            handle_data=self.strategy.handle_data,
            trading_calendar=trading_calendar,
            data_portal=data_portal,
        )
        return results
    