from zipline.api import order, record, symbol
from zipline import run_algorithm
from zipline.utils.calendar_utils import get_calendar
import pandas as pd
import datetime as dt
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
        self.start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
        self.strategy = strategy
        self.capital = capital
        self.data = None

    def fetch_historical_data(self):
        """
        Fetch historical data from the local database (`historical_market_data` table).
        """
        # Prepare the query
        query = f"""
            SELECT datetime, symbol, open, high, low, close, volume
            FROM historical_market_data
            WHERE symbol IN ({', '.join([f"'{s}'" for s in self.symbols])})
            AND datetime BETWEEN '{self.start_date}' AND '{self.end_date}'
            ORDER BY datetime
        """
        # Fetch the data
        data = fetch_data(query)
        if data.empty:
            raise ValueError("No data available for the specified symbols and date range.")

        # Ensure datetime is properly formatted
        print(f"Before conversion, datetime column dtype: {data['datetime'].dtype}")
        data["datetime"] = pd.to_datetime(data["datetime"], utc=True).dt.tz_localize(None)
        print(f"After conversion, datetime column dtype: {data['datetime'].dtype}")

        # Set index
        data.set_index(["datetime", "symbol"], inplace=True)

        # Align data with the trading calendar
        calendar = get_calendar("XNYS")
        all_sessions = calendar.sessions_in_range(self.start_date, self.end_date)
        print(f"Before conversion, all_sessions dtype: {all_sessions.dtype}")

        # Convert all_sessions to timezone-naive datetime64[ns]
        all_sessions = all_sessions.tz_localize(None).normalize()
        print(f"After conversion, all_sessions dtype: {all_sessions.dtype}")

        aligned_data = []

        for symbol in self.symbols:
            # Slice data for the symbol and reset the index
            symbol_data = data.xs(symbol, level="symbol", drop_level=False).reset_index()

            # Ensure the index is datetime
            print(f"Symbol {symbol} data index dtype before conversion: {symbol_data['datetime'].dtype}")
            symbol_data.set_index("datetime", inplace=True)
            symbol_data.index = pd.to_datetime(symbol_data.index)
            print(f"Symbol {symbol} data index dtype after conversion: {symbol_data.index.dtype}")

            # Align with all_sessions
            symbol_data = symbol_data.reindex(all_sessions, method="pad").fillna(method="bfill")
            aligned_data.append(symbol_data)

        # Combine all aligned data
        self.data = pd.concat(aligned_data)
        print(f"Aligned data:\n{self.data.head()}")

    def run(self):
        """
        Run the backtest using the provided strategy.
        """
        print("Fetching historical data...")
        self.fetch_historical_data()

        print("Running algorithm...")
        # Debug the raw data before pivoting
        print("Data before pivoting:")
        print(self.data.head())

        # Reset index and ensure proper column names
        reset_data = self.data.reset_index().rename(columns={"index": "datetime"})
        print("Data after reset_index and rename:")
        print(reset_data.head())

        # Convert data to a Zipline-compatible format
        panel_data = reset_data.pivot(
            index="datetime", columns="symbol", values=["open", "high", "low", "close", "volume"]
        )

        # Debug the pivoted data
        print("Pivoted data:")
        print(panel_data.head())

        # Run the algorithm
        results = run_algorithm(
            start=self.start_date,
            end=self.end_date,
            capital_base=self.capital,
            data_frequency="daily",
            initialize=self.strategy.initialize,
            handle_data=self.strategy.handle_data,
            trading_calendar=get_calendar("XNYS"),
            data=panel_data,
        )
        print("Backtest completed!")
        return results
    