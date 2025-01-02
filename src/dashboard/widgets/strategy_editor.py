from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
from dash_ace import DashAceEditor
from src.utils.database import fetch_as_dataframe
from src.backtesting.backtester import BacktestManager

class StrategyEditor:
    @staticmethod
    def layout():
        """
        Layout for the Strategy Editor tab, rendered with or without symbol selection.
        """
        return html.Div([
            # Strategy Editor Section
            html.Div([
                DashAceEditor(
                    id="strategy-editor",
                    value="""# Define your strategy here
def strategy(data):
    # Example: Buy when close < SMA, sell otherwise
    sma = data['close'].rolling(10).mean()
    return data['close'] < sma
""",
                    mode="python",
                    theme="monokai",
                    tabSize=4,
                    enableBasicAutocompletion=True,
                    enableLiveAutocompletion=True,
                    placeholder="Write your strategy...",
                    style={"width": "100%", "height": "300px"},
                ),
                html.Div([
                    html.Label("Select Symbols for Backtesting"),
                    dcc.Dropdown(
                        id="backtest-symbol-selector",
                        options=[],  # Will be dynamically populated
                        multi=True,
                        placeholder="Select symbols",
                        style={"width": "100%"}
                    ),
                ]),
                dbc.Button("Run Backtest", id="run-backtest", color="primary", className="mt-3"),
            ], className="mb-4"),
            # Results Section
            dcc.Loading(
                id="backtest-loading",
                type="circle",
                children=html.Div(id="backtest-results", className="mt-3")
            )
        ])

    @staticmethod
    @callback(
        Output("backtest-symbol-selector", "options"),
        [Input("strategy-editor", "value")]
    )
    def update_symbol_options(_):
        """
        Populate the symbol dropdown options dynamically.
        """
        try:
            # Populate symbols from database
            symbols = [{"label": symbol, "value": symbol} for symbol in fetch_as_dataframe(
                "SELECT DISTINCT symbol FROM historical_market_data"
            )["symbol"].tolist()]
            return symbols
        except Exception as e:
            print(f"❌ Error fetching symbol options: {str(e)}")
            return []

    @staticmethod
    @callback(
        Output("backtest-results", "children"),
        [Input("run-backtest", "n_clicks")],
        [
            State("strategy-editor", "value"),
            State("backtest-symbol-selector", "value"),
            State("date-picker", "start_date"),
            State("date-picker", "end_date"),
        ],
    )
    def run_backtest(n_clicks, strategy_code, symbols, start_date, end_date):
        """
        Execute the backtest and display results.
        """
        if not n_clicks:
            return html.Div("⚠️ Please click 'Run Backtest' to start.", className="text-warning p-3")

        if not strategy_code or not symbols or not start_date or not end_date:
            return html.Div("⚠️ Please provide all inputs to run the backtest.", className="text-warning")

        try:
            # Compile and validate the strategy
            strategy_namespace = {}
            exec(strategy_code, {}, strategy_namespace)
            strategy_function = strategy_namespace.get("strategy")
            if not callable(strategy_function):
                raise ValueError("No valid strategy function defined in the editor.")

            # Perform the backtest
            backtest_manager = BacktestManager()
            backtest_manager.perform_backtest(strategy_function, symbols, start_date, end_date)

            # Generate visualizations
            performance_chart = dcc.Graph(figure=backtest_manager.generate_performance_chart())
            trades_chart = dcc.Graph(figure=backtest_manager.generate_trades_chart())
            trades_table = dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in backtest_manager.generate_trades_table().columns],
                data=backtest_manager.generate_trades_table().to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left"},
            )

            return html.Div([
                dbc.Row(dbc.Col(performance_chart, width=12)),
                dbc.Row(dbc.Col(trades_chart, width=12)),
                dbc.Row(dbc.Col(trades_table, width=12))
            ])
        except Exception as e:
            print(f"❌ Error running backtest: {str(e)}")
            return html.Div(f"❌ Error running backtest: {str(e)}", className="text-danger p-3")
        