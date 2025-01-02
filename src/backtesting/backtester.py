import backtrader as bt
import pandas as pd
from datetime import datetime
from src.utils.database import fetch_data, insert_backtest_results
from src.backtesting.strategies.moving_avg import MovingAverageCrossover
from src.backtesting.strategies.momentum import MomentumStrategy
import plotly.graph_objects as go

class BacktestManager:
    """
    Manages backtesting execution and results visualization.
    """
    strategies = {
        "MovingAverageCrossover": MovingAverageCrossover,
        "MomentumStrategy": MomentumStrategy,
    }

    def __init__(self):
        self.results = None
        self.cerebro = bt.Cerebro()

    def perform_backtest(self, strategy_input, symbols, start_date, end_date):
        """
        Executes the backtest logic.
        """
        # Determine if `strategy_input` is a string (predefined strategy) or callable (custom strategy)
        if isinstance(strategy_input, str):
            if strategy_input not in self.strategies:
                raise ValueError(f"Invalid strategy name. Available strategies: {list(self.strategies.keys())}")
            strategy_class = self.strategies[strategy_input]
        elif callable(strategy_input):
            strategy_class = self._wrap_dynamic_strategy(strategy_input)
        else:
            raise ValueError("Invalid strategy input. Provide a strategy name or a callable function.")

        # Clear previous data
        self.cerebro = bt.Cerebro()

        for symbol in symbols:
            query = f"""
            SELECT datetime, open, high, low, close, volume
            FROM historical_market_data
            WHERE symbol = '{symbol}' 
            AND datetime BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY datetime ASC
            """
            data = fetch_data(query)

            if data.empty:
                raise ValueError(f"No data found for symbol {symbol} in the specified range.")

            # Prepare the data feed for Backtrader
            data_feed = bt.feeds.PandasData(
                dataname=data,
                datetime="datetime",
                open="open",
                high="high",
                low="low",
                close="close",
                volume="volume",
                timeframe=bt.TimeFrame.Days,
            )
            self.cerebro.adddata(data_feed, name=symbol)

        # Add the selected strategy
        self.cerebro.addstrategy(strategy_class)

        # Run the backtest
        initial_value = 10000
        self.cerebro.broker.setcash(initial_value)
        self.cerebro.run()

        # Process and store results
        self.results = self._process_results(strategy_input, symbols, start_date, end_date, initial_value)
        return self.results
    
    def _wrap_dynamic_strategy(self, strategy_func):
        """
        Wraps a dynamic strategy function into a Backtrader-compatible strategy class.
        """
        class DynamicStrategy(bt.Strategy):
            def __init__(self):
                self.strategy_func = strategy_func

            def next(self):
                data = {field: getattr(self.data, field)[0] for field in ['datetime', 'open', 'high', 'low', 'close', 'volume']}
                decision = self.strategy_func(data)
                if decision.get("buy"):
                    self.buy()
                if decision.get("sell"):
                    self.sell()

        return DynamicStrategy

    def _process_results(self, strategy_name, symbols, start_date, end_date, initial_value):
        """
        Extracts and formats backtesting results for database storage and visualization.
        """
        results = []
        final_value = self.cerebro.broker.getvalue()
        return_percentage = ((final_value - initial_value) / initial_value) * 100

        # Gather results for each symbol
        for symbol in symbols:
            result = {
                "strategy": strategy_name,
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "initial_value": initial_value,
                "final_value": final_value,
                "return_percentage": return_percentage,
            }
            results.append(result)

        # Insert results into the database
        self._store_results(results)
        return pd.DataFrame(results)

    def _store_results(self, results):
        """
        Save backtest results to the database.
        """
        data_to_insert = [
            (
                result["strategy"],
                result["symbol"],
                result["start_date"],
                result["end_date"],
                result["initial_value"],
                result["final_value"],
                result["return_percentage"]
            )
            for result in results
        ]
        insert_backtest_results(data_to_insert)

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
    