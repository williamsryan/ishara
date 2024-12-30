from dash import Dash, dcc, html, Input, Output, State
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
# sidebar = Sidebar()
controls = Controls()
price_chart = PriceChart()
alternative_data = AlternativeDataCharts()
data_table = DataTable()
analyses = Analyses()

# Fetch distinct symbols once
def get_symbols():
    data_source = "real_time_market_data"  # Default data source
    query = f"SELECT DISTINCT symbol FROM {data_source}"
    data = fetch_data(query)

    if data.empty:
        print("⚠️ No symbols found in the database.")
        return []

    return [{"label": symbol, "value": symbol} for symbol in data["symbol"].unique()]

# Load symbols globally
SYMBOL_OPTIONS = get_symbols()

# App Layout
app.layout = dbc.Container(fluid=True, children=[
    # Header
    dbc.Row(dbc.Col(header.render(), className="bg-dark text-light py-3")),

    # Sidebar and Tabs
    dbc.Row([
        dbc.Col(
            controls.render(symbol_options=SYMBOL_OPTIONS),
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
                className="mb-3",
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
# @app.callback(
#     [Output("symbol-selector", "options"), Output("symbol-selector", "value")],
#     [Input("symbol-selector", "value")]
# )
# def update_symbols(current_value):
#     # Determine the data source based on logic (or keep default)
#     data_source = "real_time_market_data"  # Or default to a primary data source

#     # Fetch distinct symbols from the data source
#     query = f"SELECT DISTINCT symbol FROM {data_source}"
#     data = fetch_data(query)

#     if data.empty:
#         print(f"No symbols found for data source: {data_source}")
#         return [], None

#     options = [{"label": symbol, "value": symbol} for symbol in data["symbol"].unique()]

#     # Preserve the current selection if it is valid
#     if current_value and current_value in [opt["value"] for opt in options]:
#         return options, current_value

#     # Reset to None if the current value is invalid
#     return options, None

@app.callback(
    Output("alternative-data-graphs", "children"),
    [Input("symbol-selector", "value"), Input("metric-filter", "value")]
)
def update_alternative_data_graphs(selected_symbols, selected_metrics):
    if not selected_symbols or not selected_metrics:
        return html.Div("⚠️ Please select symbols and metrics to display data.", className="text-warning p-3")

    # Render graphs dynamically based on selected metrics
    return alternative_data.render_graphs(selected_symbols, selected_metrics)

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("symbol-selector", "value"),
     Input("date-picker", "start_date"), Input("date-picker", "end_date"),
     Input("overlay-toggle", "value")]
)
def update_content(tab, symbols, start_date, end_date, overlay_toggle):
    if not symbols:
        return html.Div("⚠️ Please select symbols to display data.")
    
    # start_date = start_date or data["datetime"].min() if not data.empty else None
    # end_date = end_date or data["datetime"].max() if not data.empty else None
    # start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)

    try:
        if tab == "data-table":
            return data_table.layout(symbols, start_date, end_date)

        elif tab == "price-chart":
            return price_chart.layout(symbols, start_date, end_date, "historical_market_data")

        elif tab == "alternative-data":
            return alternative_data.layout(symbols)

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
