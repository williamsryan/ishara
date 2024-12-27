from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from threading import Thread
import pandas as pd
import plotly.graph_objs as go
from src.fetchers.alpaca_realtime import fetch_real_time_data
from src.dashboard.components.header import Header
from src.dashboard.components.sidebar import Sidebar
from src.dashboard.widgets.controls import Controls
from src.dashboard.widgets.chart_components import PriceChart, AlternativeDataCharts
from src.dashboard.widgets.data_table import DataTable
from src.dashboard.widgets.analyses import Analyses

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "📊 Ishara Trading Dashboard"

# Instantiate components and widgets
header = Header()
sidebar = Sidebar()
controls = Controls()
price_chart = PriceChart()
alternative_data = AlternativeDataCharts()
data_table = DataTable()
analyses = Analyses()

# App Layout
app.layout = dbc.Container(fluid=True, children=[
    # Header
    dbc.Row(dbc.Col(header.render(), width=12)),

    # Sidebar and Main Content
    dbc.Row([
        # dbc.Col(sidebar.render(), width=3, style={"backgroundColor": "#f8f9fa"}),
        dbc.Col([
            controls.render(),
            dcc.Tabs(id="tabs", value="price-chart", children=[
                dcc.Tab(label="📈 Price Chart", value="price-chart"),
                dcc.Tab(label="📊 Alternative Data", value="alternative-data"),
                dcc.Tab(label="🗃 Data Table", value="data-table"),
                dcc.Tab(label="📐 Analyses", value="analyses"),
            ]),
            html.Div(id="tab-content", className="p-3")
        ], width=9)
    ])
])

# Callback to dynamically update tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("symbol-selector", "value"),
     Input("date-picker", "start_date"), Input("date-picker", "end_date"),
     Input("overlay-toggle", "value")]
)
def update_content(tab, symbols, start_date, end_date, overlay_toggle):
    if not symbols:
        return html.Div("⚠️ Please select symbols to display data.")

    # Render the appropriate tab content
    if tab == "price-chart":
        return price_chart.layout(symbols, start_date, end_date)
    elif tab == "alternative-data":
        return alternative_data.layout(symbols, start_date, end_date, overlay_toggle)
    elif tab == "data-table":
        return data_table.layout(symbols, start_date, end_date)
    elif tab == "analyses":
        return analyses.layout(symbols, start_date, end_date)
    else:
        return html.Div("⚠️ Invalid tab selected!")

# Callback to trigger analyses
@app.callback(
    [Output("clustering-result", "figure"), Output("regime-result", "figure")],
    [Input("run-analyses", "n_clicks")],
    [Input("symbol-selector", "value"),
     Input("date-picker", "start_date"),
     Input("date-picker", "end_date")]
)
def trigger_analyses(n_clicks, symbols, start_date, end_date):
    if not n_clicks or not symbols:
        return go.Figure(), go.Figure()

    clustering_fig = analyses.run_clustering_analysis(symbols)
    regime_fig = analyses.run_regime_analysis(symbols)
    return clustering_fig, regime_fig

# Run the dashboard and real-time data streamer
def run_dashboard():
    stream_thread = Thread(target=fetch_real_time_data)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard()
