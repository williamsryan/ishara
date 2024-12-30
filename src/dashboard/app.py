from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from threading import Thread
import pandas as pd
import plotly.graph_objs as go
from src.fetchers.alpaca_realtime import fetch_real_time_data
from src.dashboard.components.header import Header
from src.dashboard.components.sidebar import Sidebar
from src.dashboard.widgets.controls import Controls
from src.dashboard.widgets.chart_components import PriceChart, AlternativeDataCharts
from src.processors.clustering_analysis import perform_clustering_analysis
from src.dashboard.widgets.data_table import DataTable
from src.dashboard.widgets.analyses import Analyses
from src.utils.database import fetch_data

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "📊 Ishara Trading Dashboard"
app.config.suppress_callback_exceptions = True

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
    dbc.Row(dbc.Col(header.render(), className="bg-dark text-light py-3")),

    # Sidebar and Tabs
    dbc.Row([
        dbc.Col(
            controls.render(),
            width=3,
            className="bg-light p-4 border-end vh-100 sticky-top overflow-auto"
        ),
        dbc.Col([
            dcc.Tabs(
                id="tabs",
                value="price-chart",
                children=[
                    dcc.Tab(label="📈 Price Chart", value="price-chart"),
                    dcc.Tab(label="📊 Alternative Data", value="alternative-data"),
                    dcc.Tab(label="🗃 Data Table", value="data-table"),
                    dcc.Tab(label="📐 Analyses", value="analyses"),
                ],
                className="mb-3"
            ),
            dcc.Loading(
                id="tab-content-loading",
                type="circle",
                children=html.Div(id="tab-content", className="p-3")
            ),
        ], width=9),
    ]),
])

# Callback to update the symbol dropdown dynamically
@app.callback(
    [Output("symbol-selector", "options"), Output("symbol-selector", "value")],
    Input("tabs", "value")
)
def update_symbols(tab):
    # Determine the data source based on the selected tab
    data_source = {
        "price-chart": "real_time_market_data",
        "alternative-data": "alternative_data",
        "data-table": "yahoo_finance_data",
        "analyses": "analysis_results",
    }.get(tab, "real_time_market_data")

    # Fetch symbols from the appropriate data source
    query = f"SELECT DISTINCT symbol FROM {data_source}"
    symbols_data = fetch_data(query)

    # Handle empty results
    if symbols_data.empty:
        return [], None

    # Generate dropdown options
    options = [{"label": symbol, "value": symbol} for symbol in symbols_data["symbol"].unique()]
    # Preserve the current selection if still valid
    if tab in [opt["value"] for opt in options]:
        return options, tab
    default_value = options[0]["value"] if options else None
    return options, default_value

# Callback to dynamically update tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("symbol-selector", "value"),
     Input("date-picker", "start_date"), Input("date-picker", "end_date")]
)
def update_content(tab, stored_symbols, start_date, end_date):
    if not stored_symbols:
        return html.Div("⚠️ Please select symbols to display data.", className="text-warning p-3")

    try:
        if tab == "data-table":
            return data_table.layout(stored_symbols, start_date, end_date)

        elif tab == "price-chart":
            return price_chart.layout(stored_symbols, start_date, end_date, "real_time_market_data")

        elif tab == "alternative-data":
            return alternative_data.layout(stored_symbols, start_date, end_date)

        elif tab == "analyses":
            return analyses.layout()

        else:
            return html.Div("⚠️ Invalid tab selected.", className="text-danger p-3")
    except Exception as e:
        print(f"Error loading tab content: {e}")
        return html.Div(f"❌ Error loading content: {str(e)}", className="text-danger p-3")

# Callback for triggering analyses
@app.callback(
    Output("analysis-status", "children"),
    [Input("run-analysis", "n_clicks")],
    [State("symbol-selector", "value"), State("date-picker", "start_date"), State("date-picker", "end_date")]
)
def run_analysis(n_clicks, symbols, start_date, end_date):
    if not n_clicks:
        return html.Div("⚠️ Please select symbols to display data.", className="text-warning p-3"), ""

    # Display running status
    status_message = "⏳ Running analyses... This may take a few moments."

    try:
        print(f"Running analysis for symbols: {symbols}")
        perform_clustering_analysis(symbols)

        # Update results in the tab
        analyses_tab = analyses.layout()
        status_message = "✅ Analysis complete! Results are updated."
        return analyses_tab, status_message
    except Exception as e:
        print(f"Error during analysis: {e}")
        return html.Div(f"❌ Error during analysis: {str(e)}", className="text-danger p-3"), ""

# Run the dashboard and real-time data streamer
def run_dashboard():
    stream_thread = Thread(target=fetch_real_time_data)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard()
