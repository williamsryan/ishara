import backtrader as bt
import pandas as pd
from src.utils.database import fetch_data, insert_backtest_results
from src.backtesting.strategies.moving_avg import MovingAverageCrossover
from src.backtesting.strategies.momentum import MomentumStrategy
import plotly.graph_objects as go

class BacktestManager:
    """
    Manages backtesting execution and results visualization.
    """
    def __init__(self):
        self.results = None

    def perform_backtest(self, strategy_name, symbols, start_date, end_date):
        """
        Executes the backtest logic.
        """
        # Simulate fetching historical data for the backtest
        query = f"""
        SELECT * FROM historical_market_data
        WHERE symbol IN ({','.join(f"'{s}'" for s in symbols)})
        AND datetime BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY datetime ASC
        """
        data = fetch_data(query)

        if data.empty:
            raise ValueError("No historical data available for the selected symbols and date range.")

        # Simulate backtesting logic based on strategy
        results = []
        for symbol in symbols:
            symbol_data = data[data["symbol"] == symbol].copy()
            symbol_data["strategy"] = strategy_name
            symbol_data["returns"] = symbol_data["close"].pct_change().fillna(0)
            results.append(symbol_data)

        # Combine results for all symbols
        self.results = pd.concat(results)
        self._store_results(strategy_name, symbols, start_date, end_date)
        return self.results

    def _store_results(self, strategy_name, symbols, start_date, end_date):
        """
        Stores the backtest results in the database.
        """
        if self.results is None:
            raise ValueError("No results to store.")

        for _, row in self.results.iterrows():
            insert_backtest_results(
                symbol=row["symbol"],
                strategy=strategy_name,
                datetime=row["datetime"],
                returns=row["returns"],
                start_date=start_date,
                end_date=end_date,
            )

    def generate_performance_chart(self):
        """
        Generates a performance chart for the backtest.
        """
        if self.results is None:
            raise ValueError("No backtest results available for visualization.")

        fig = go.Figure()
        for symbol, group in self.results.groupby("symbol"):
            fig.add_trace(
                go.Scatter(
                    x=group["datetime"],
                    y=(1 + group["returns"]).cumprod(),
                    mode="lines",
                    name=symbol,
                    line=dict(width=2)
                )
            )

        fig.update_layout(
            title="Backtest Performance",
            xaxis_title="Date",
            yaxis_title="Cumulative Returns",
            template="plotly_white"
        )
        return fig

    def generate_trades_chart(self):
        """
        Generates a trades chart to visualize entries and exits.
        """
        if self.results is None:
            raise ValueError("No backtest results available for visualization.")

        fig = go.Figure()
        for symbol, group in self.results.groupby("symbol"):
            fig.add_trace(
                go.Scatter(
                    x=group["datetime"],
                    y=group["close"],
                    mode="markers",
                    name=f"{symbol} Trades",
                    marker=dict(size=6, symbol="circle")
                )
            )

        fig.update_layout(
            title="Trades Overview",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )
        return fig

    def generate_trades_table(self):
        """
        Generates a table of trade results.
        """
        if self.results is None:
            raise ValueError("No backtest results available for visualization.")

        trades = self.results[["datetime", "symbol", "close", "returns"]].copy()
        trades.rename(
            columns={
                "datetime": "Date",
                "symbol": "Symbol",
                "close": "Price",
                "returns": "Daily Return"
            },
            inplace=True
        )
        trades["Daily Return"] = trades["Daily Return"].round(4)
        return trades