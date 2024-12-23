from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from threading import Thread
from src.dashboard.widgets.symbol_watchlist import SymbolWatchlist
from src.dashboard.widgets.data_table import DataTableWidget
from src.dashboard.widgets.chart_components import PriceChart, AlternativeDataCharts
from src.dashboard.widgets.analyses import AnalysisCharts
from src.fetchers.alpaca_realtime import start_stream
from src.utils.database import connect_to_db

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "📊 Ishara Trading Dashboard"

# Instantiate widgets
symbol_watchlist = SymbolWatchlist()
data_table = DataTableWidget()
price_chart = PriceChart()
alt_data_charts = AlternativeDataCharts()
analysis_charts = AnalysisCharts()

# App Layout
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H2("📊 Ishara Trading Platform", className="text-center p-3"))),
    dbc.Row([
        dbc.Col(symbol_watchlist.layout(), width=3),
        dbc.Col([
            dcc.Tabs(id="tabs", value="price-chart", children=[
                dcc.Tab(label="📈 Price Chart", value="price-chart"),
                dcc.Tab(label="📊 Alternative Data", value="alternative-data"),
                dcc.Tab(label="🗃 Data Table", value="data-table"),
                dcc.Tab(label="📐 Analyses", value="analyses")
            ]),
            html.Div(id="tab-content")
        ], width=9)
    ])
], fluid=True)

# Callbacks for Tab Updates
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("symbol-selector", "value")]
)
def render_tab_content(tab, symbols):
    if not symbols:
        return html.Div("⚠️ Please select a symbol to view data.")
    
    if tab == "price-chart":
        return price_chart.layout(symbols)
    elif tab == "alternative-data":
        return alt_data_charts.layout(symbols)
    elif tab == "data-table":
        return data_table.layout(symbols)
    elif tab == "analyses":
        return analysis_charts.layout(symbols)
    else:
        return html.Div("⚠️ Invalid tab selected.")

# Start Dashboard with Streaming
def run_dashboard_with_stream():
    stream_thread = Thread(target=start_stream)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard_with_stream()
    