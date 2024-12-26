from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from threading import Thread
from src.dashboard.components.header import render_header
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.tabs import render_tabs
from src.dashboard.widgets.symbol_watchlist import SymbolWatchlist
from src.dashboard.widgets.data_table import DataTableWidget
from src.dashboard.widgets.chart_components import PriceChart, AlternativeDataCharts
from src.dashboard.widgets.analyses import AnalysisCharts
from src.fetchers.alpaca_realtime import fetch_real_time_data

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Widgets and layouts
symbol_watchlist = SymbolWatchlist()
data_table = DataTableWidget()
price_chart = PriceChart()
alt_data_charts = AlternativeDataCharts()
analysis_charts = AnalysisCharts()

# App layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(dbc.Col(render_header(), width=12)),
        dbc.Row(
            className="g-0",  # Use Bootstrap class for no gutters
            children=[
                dbc.Col(render_sidebar(), width=3),
                dbc.Col(
                    [
                        render_tabs(),
                        html.Div(id="tab-content"),
                    ],
                    width=9,
                ),
            ],
        ),
    ],
)

# Callbacks
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
)
def update_tab(tab_value):
    if tab_value == "price-chart":
        return price_chart.layout(["AAPL", "GOOGL"])  # Default symbols
    elif tab_value == "alternative-data":
        return alt_data_charts.layout(["AAPL", "GOOGL"])
    elif tab_value == "data-table":
        return data_table.layout(["AAPL", "GOOGL"])
    elif tab_value == "analyses":
        return analysis_charts.layout(["AAPL", "GOOGL"])
    else:
        return html.Div("Invalid tab selected!")

# Start Dashboard with Streaming
def run_dashboard():
    stream_thread = Thread(target=fetch_real_time_data)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard()
