from zipline.api import order, record, symbol, schedule_function, date_rules, time_rules
from zipline import run_algorithm
from zipline.utils.calendar_utils import get_calendar
from zipline.data.bundles import register
from zipline.data.bundles.core import ingest
from zipline.assets.asset_writer import AssetDBWriter
from zipline.assets import AssetFinder
from sqlalchemy import create_engine
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

        # Ensure data is indexed by date and symbol for Zipline compatibility
        data["datetime"] = pd.to_datetime(data["datetime"], utc=True)  # Ensure UTC alignment
        data.set_index(["datetime", "symbol"], inplace=True)
        self.data = data

    def _create_asset_finder(self):
        """
        Create an AssetFinder with metadata stored in an in-memory SQLite database.
        """
        print("Generating asset metadata...")

        # Create asset metadata DataFrame
        asset_metadata = pd.DataFrame({
            "sid": range(len(self.symbols)),  # Asset IDs
            "symbol": self.symbols,
            "asset_name": self.symbols,
            "start_date": [pd.Timestamp(self.start_date)] * len(self.symbols),
            "end_date": [pd.Timestamp(self.end_date)] * len(self.symbols),
            "exchange": ["NYSE"] * len(self.symbols),
        })

        print(f"Asset metadata:\n{asset_metadata}")

        # Create an in-memory SQLite database
        engine = create_engine("sqlite:///:memory:")

        # Write metadata to the in-memory database
        writer = AssetDBWriter(engine)
        writer.write(asset_metadata)

        # Return an AssetFinder connected to the in-memory database
        return AssetFinder(engine)

    def _register_custom_bundle(self):
        """
        Register a custom Zipline data bundle using the `self.data` DataFrame.
        """
        # Get the trading calendar
        trading_calendar = get_calendar("XNYS")
        all_sessions = trading_calendar.sessions_in_range(self.start_date, self.end_date)

        # Create a mapping of symbols to integer SIDs
        symbol_to_sid = {symbol: i for i, symbol in enumerate(self.symbols)}

        def custom_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer,
                        adjustment_writer, calendar, start_session, end_session, cache,
                        show_progress, output_dir):
            """
            Custom bundle for ingesting data from a Pandas DataFrame.
            """
            # Prepare the data for each SID
            daily_data = []
            for symbol, sid in symbol_to_sid.items():
                # Extract data for the symbol
                symbol_data = self.data.xs(symbol, level="symbol")
                symbol_data = symbol_data.reindex(all_sessions).fillna(0)  # Align with trading calendar
                symbol_data = symbol_data.reset_index()  # Flatten the index
                symbol_data["sid"] = sid  # Add the SID column
                daily_data.append((sid, symbol_data))

            # Write the data to the daily bar writer
            daily_bar_writer.write(
                daily_data,
                show_progress=show_progress,
            )
            adjustment_writer.write()

        # Register the custom bundle
        register("custom_bundle", custom_bundle)

        # Ingest the bundle directly
        ingest("custom_bundle")

    def run(self):
        """
        Run the backtest with the provided strategy.
        """
        print("Fetching historical data...")
        self.fetch_historical_data()

        print("Registering custom data bundle...")
        self._register_custom_bundle()

        # Ensure the first trading day is naive
        first_trading_day = self.data.index.get_level_values(0).min()
        first_trading_day = first_trading_day.normalize()
        print(f"First trading day (naive): {first_trading_day}")

        trading_calendar = get_calendar("XNYS")

        print("Running algorithm...")
        # Run the backtest
        results = run_algorithm(
            start=self.start_date,
            end=self.end_date,
            capital_base=self.capital,
            data_frequency="daily",
            initialize=self.strategy.initialize,
            handle_data=self.strategy.handle_data,
            trading_calendar=trading_calendar,
        )
        print("Backtest completed!")
        return results
    