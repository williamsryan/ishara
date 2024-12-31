from dash import Dash, dcc, html, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
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
from src.processors.analysis import Analysis
from src.utils.database import fetch_data

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "📊 Ishara Trading Dashboard"
app.config.suppress_callback_exceptions = True

# Instantiate components and widgets
header = Header()
# sidebar = Sidebar()
controls = Controls()
data_table = DataTable()
analyses = Analyses()

# Instantiate chart components
price_chart = PriceChart()
alternative_data_charts = AlternativeDataCharts()

# Fetch distinct symbols once
def get_symbols():
    data_source = "historical_market_data"  # Default data source
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

@app.callback(
    Output("symbol-selector", "value"),
    [Input("select-all", "n_clicks"), Input("deselect-all", "n_clicks")],
    State("symbol-selector", "options"),
    prevent_initial_call=True
)
def select_deselect_symbols(select_all_clicks, deselect_all_clicks, options):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    # Identify which button was clicked
    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if clicked_id == "select-all":
        # Select all options
        return [option["value"] for option in options]
    elif clicked_id == "deselect-all":
        # Deselect all options
        return []

@app.callback(
    Output("alternative-data-graphs", "children"),
    [
        Input("metric-filter", "value"),
        State("symbol-selector", "value")
    ]
)
def update_alternative_data_graphs(selected_metrics, symbols):
    """
    Update the alternative data graphs based on selected metrics and symbols.
    """
    if not symbols or not selected_metrics:
        return html.Div("⚠️ Please select symbols and metrics to display data.", className="text-warning p-3")

    try:
        return alternative_data_charts.render_graphs(symbols, selected_metrics)
    except Exception as e:
        print(f"❌ Error updating alternative data graphs: {e}")
        return html.Div(f"❌ Error loading alternative data graphs: {str(e)}", className="text-danger p-3")

# Callback to update tab content based on symbol and date selections
@app.callback(
    Output("tab-content", "children"),
    [
        Input("tabs", "value"),
        Input("symbol-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date")
    ]
)
def update_tab_content(tab, symbols, start_date, end_date):
    """
    Update the content of the selected tab dynamically.
    """
    if not symbols:
        return html.Div("⚠️ Please select symbols to display data.", className="text-warning p-3")

    try:
        if tab == "price-chart":
            return price_chart.layout(symbols, start_date, end_date, "historical_market_data")
        elif tab == "alternative-data":
            return alternative_data_charts.layout(symbols)
        elif tab == "data-table":
            return data_table.layout(symbols, start_date, end_date)
        elif tab == "analyses":
            return analyses.layout(symbols, start_date, end_date)
        else:
            return html.Div("⚠️ Invalid tab selected.", className="text-danger p-3")

    except Exception as e:
        print(f"❌ Error updating tab content: {e}")
        return html.Div(f"❌ Error loading content: {str(e)}", className="text-danger p-3")
    
# Callback for triggering analyses
@app.callback(
    [
        Output("analysis-status", "children"),
        Output("analyses-tab-content", "children"),
    ],
    [Input("run-analysis", "n_clicks")],
    [
        State("analysis-type-dropdown", "value"),
        State("symbol-selector", "value"),
        State("date-picker", "start_date"),
        State("date-picker", "end_date"),
    ],
)
def run_and_fetch_analysis(n_clicks, analysis_type, symbols, start_date, end_date):
    """
    Run the selected analysis and update the analyses tab content.
    """
    if not n_clicks:
        return (
            html.Div("⚠️ Please click 'Run Analysis' to start.", className="text-warning p-3"),
            html.Div("⚠️ No analysis results to display.", className="text-warning p-3"),
        )

    if not symbols or not analysis_type:
        return (
            html.Div("⚠️ Please select symbols and analysis type.", className="text-warning p-3"),
            html.Div("⚠️ No analysis results to display.", className="text-warning p-3"),
        )

    try:
        # Step 1: Run the selected analysis
        if analysis_type == "knn_clustering":
            data = Analysis.perform_knn_clustering(symbols, start_date, end_date)
        elif analysis_type == "graph_clustering":
            graph, communities = Analysis.perform_graph_clustering(symbols, start_date, end_date)
        else:
            return (
                html.Div("⚠️ Unsupported analysis type.", className="text-warning p-3"),
                html.Div("⚠️ No analysis results to display.", className="text-warning p-3"),
            )

        # Step 2: Fetch the results for visualization
        if analysis_type == "knn_clustering":
            results = Analysis.fetch_clustering_results("knn_clustering")
            # print(f"DEBUG: Fetched KNN clustering results: {results.head()}")
            if results.empty:
                return (
                    html.Div("⚠️ No clustering results found.", className="text-warning p-3"),
                    html.Div("⚠️ No visualization data available.", className="text-warning p-3"),
                )
            visualization = Analysis.plot_cluster_scatter(results, features=["low", "high"])
        elif analysis_type == "graph_clustering":
            results = Analysis.fetch_clustering_results("graph_clustering")
            print(f"DEBUG: Fetched graph clustering results: {results.head()}")
            if results.empty:
                return (
                    html.Div("⚠️ No graph clustering results found.", className="text-warning p-3"),
                    html.Div("⚠️ No visualization data available.", className="text-warning p-3"),
                )
            visualization = Analysis.plot_graph_clusters(results)
        else:
            visualization = html.Div("⚠️ Visualization not supported for this analysis type.", className="text-warning p-3")

        # Step 3: Return success message and visualization
        return (
            html.Div("✅ Analysis complete! Results are updated.", className="text-success p-3"),
            dcc.Graph(figure=visualization),
        )

    except Exception as e:
        # Handle any errors during analysis or visualization
        print(f"❌ Error during analysis: {e}")
        return (
            html.Div(f"❌ Error performing analysis: {str(e)}", className="text-danger p-3"),
            html.Div(f"❌ Error displaying results: {str(e)}", className="text-danger p-3"),
        )

# Run the dashboard and real-time data streamer
def run_dashboard():
    stream_thread = Thread(target=fetch_real_time_data)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard()
