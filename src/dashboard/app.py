from dash import Dash, dcc, html, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from threading import Thread
import pandas as pd
import plotly.graph_objs as go
from src.fetchers.alpaca_realtime import fetch_real_time_data
from src.dashboard.components.header import Header
from src.dashboard.widgets.controls import Controls
from src.dashboard.widgets.chart_components import PriceChart, AlternativeDataCharts
from src.dashboard.widgets.data_table import DataTable
from src.dashboard.widgets.analyses import Analyses
from src.dashboard.widgets.strategy_editor import StrategyEditor
from src.processors.analysis import Analysis
from src.utils.database import fetch_as_dataframe

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
strategy_editor = StrategyEditor()

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
                    dcc.Tab(label="🛠️ Strategy Builder", value="strategies"),
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

HISTORICAL_SYMBOLS = [{"label": symbol, "value": symbol} for symbol in fetch_as_dataframe(
    "SELECT DISTINCT symbol FROM historical_market_data"
)["symbol"].tolist()]

@app.callback(
    Output("symbol-selector", "options"),
    Input("symbol-selector", "search_value"),
    State("data-source-selector", "value"),
    prevent_initial_call=True
)
def update_symbol_selector(search_value, data_source):
    """
    Dynamically fetch symbols based on the search input and data source.
    """
    if not search_value:
        raise PreventUpdate

    if data_source == "real_time_market_data":
        if not search_value:
            # If no search value is provided, show top popular symbols or an empty list
            query = """
            SELECT DISTINCT symbol FROM symbols
            LIMIT 20
            """
        else:
            # Perform a search with the given value
            query = f"""
            SELECT DISTINCT symbol FROM symbols
            WHERE symbol ILIKE '%{search_value}%'
            LIMIT 20
            """
    else:
        # Historical data source query
        return HISTORICAL_SYMBOLS
    try:
        results = fetch_as_dataframe(query)
        if results.empty:
            return [{"label": "No matches found", "value": ""}]
        options = [{"label": symbol, "value": symbol} for symbol in results["symbol"].tolist()]
        return options
    except Exception as e:
        print(f"❌ Error fetching symbols: {e}")
        return [{"label": "Error fetching symbols", "value": ""}]

@app.callback(
    Output("date-picker", "disabled"),
    Input("data-source-selector", "value")
)
def toggle_date_picker(data_source):
    """
    Disable the date picker if the data source is 'real_time_market_data'.
    """
    disabled_state = data_source == "real_time_market_data"
    # print(f"Data source: {data_source} | Date Picker Disabled: {disabled_state}")
    return disabled_state

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
    Output("price-chart", "figure"),
    [
        Input("symbol-selector", "value"),
        Input("data-source-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("indicator-selector", "value"),
        Input("update-interval", "n_intervals"),
    ]
)
def update_price_chart(symbols, data_source, start_date, end_date, selected_indicators, n_intervals):
    if not symbols:
        return go.Figure()
    
    if data_source == "real_time_market_data":
        # Ensure date filters are ignored for real-time data
        start_date, end_date = None, None

    return PriceChart.layout(
                    symbols=symbols, 
                    data_source=data_source, 
                    start_date=start_date, 
                    end_date=end_date,
                    selected_indicators=selected_indicators
                ).children[1].figure

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
        Input("data-source-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ]
)
def update_tab_content(tab, symbols, data_source, start_date, end_date):
    """
    Update the content of the selected tab dynamically.
    """

    # Ensure a default data source
    if not data_source:
        data_source = "historical_market_data"
    if not symbols and tab != "strategies":
        return html.Div("⚠️ Please select symbols to display data.", className="text-warning p-3")

    try:
        if tab == "price-chart":
            return price_chart.layout(
                    symbols=symbols, 
                    data_source=data_source, 
                    start_date=start_date, 
                    end_date=end_date
                )
        elif tab == "alternative-data":
            return alternative_data_charts.layout(symbols)
        elif tab == "data-table":
            return data_table.layout(symbols, start_date, end_date)
        elif tab == "analyses":
            return analyses.layout(symbols, start_date, end_date)
        elif tab == "strategies":
            return strategy_editor.layout()
        else:
            return html.Div("⚠️ Invalid tab selected.", className="text-danger p-3")

    except Exception as e:
        print(f"❌ Error updating tab content: {e}")
        return html.Div(f"❌ Error loading content: {str(e)}", className="text-danger p-3")
    
# Callback for triggering analyses
@app.callback(
    Output("analyses-tab-content", "children"),
    [Input("run-analysis", "n_clicks")],
    [
        State("analysis-type-dropdown", "value"),
        State("symbol-selector", "value"),
        State("date-picker", "start_date"),
        State("date-picker", "end_date"),
        State("feature-selector", "value"),
        State("reduction-method-dropdown", "value"), 
    ],
)
def run_and_fetch_analysis(n_clicks, analysis_type, symbols, start_date, end_date, selected_features, reduction_method):
    if not n_clicks:
        return html.Div("⚠️ Please click 'Run Analysis' to start.", className="text-warning p-3")

    try:
        if analysis_type == "knn_clustering":
            Analysis.perform_knn_clustering(
                selected_symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                selected_features=selected_features,
                reduction_method=reduction_method
            )
            results = Analysis.fetch_clustering_results("knn_clustering")
            if results.empty:
                return html.Div("⚠️ No results found for K-NN clustering.", className="text-warning p-3")
            
            scatter_fig, bar_fig, heatmap_fig = Analysis.plot_cluster_dashboard(results)
            return html.Div([
                dcc.Graph(figure=scatter_fig, id="knn-scatter-chart"),
                dcc.Graph(figure=bar_fig, id="knn-bar-chart"),
                dcc.Graph(figure=heatmap_fig, id="knn-heatmap-chart"),
            ])
        elif analysis_type == "graph_clustering":
            Analysis.perform_graph_clustering(
                selected_symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                selected_features=selected_features
            )
            results = Analysis.fetch_clustering_results("graph_clustering")
            visualization = Analysis.plot_graph_clusters(results)
            return dcc.Graph(figure=visualization, id="graph-clustering-chart")
        elif analysis_type == "regime_analysis":
            try:
                data = Analysis.fetch_regime_results(selected_symbols=symbols)
                fig_2d = Analysis.plot_regime_dashboard(data, view="2d")
                fig_3d = Analysis.plot_regime_dashboard(data, view="3d")
                return html.Div([
                    html.Div(dcc.Graph(figure=fig_2d), className="mb-4"),
                    html.Div(dcc.Graph(figure=fig_3d), className="mb-4"),
                ])
            except Exception as e:
                return html.Div(f"❌ Error displaying regime dashboard: {str(e)}")
        else:
            return html.Div("⚠️ Unsupported analysis type.", className="text-warning p-3")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return html.Div(f"❌ Error performing analysis: {str(e)}", className="text-danger p-3")
    
@app.callback(
    Output("knn-chart", "figure"),
    [Input("x-feature", "value"), Input("y-feature", "value")],
    [State("symbol-selector", "value"), State("date-picker", "start_date"), State("date-picker", "end_date")]
)
def update_knn_chart(x_feature, y_feature, selected_symbols, start_date, end_date):
    if not selected_symbols:
        return go.Figure(layout={"title": "Please select symbols."})

    try:
        # Fetch or run the KNN clustering analysis
        results = Analysis.fetch_clustering_results("knn_clustering", selected_symbols)
        if results.empty:
            results = Analysis.perform_knn_clustering(selected_symbols, start_date, end_date)

        # Generate the clustering scatter plot
        return Analysis.plot_cluster_scatter(results, [x_feature, y_feature])

    except Exception as e:
        print(f"❌ Error updating KNN chart: {e}")
        return go.Figure(layout={"title": "Error generating chart."})
    
# Run the dashboard and real-time data streamer
def run_dashboard():
    stream_thread = Thread(target=fetch_real_time_data)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(host="0.0.0.0", port="8050", debug=True)

if __name__ == "__main__":
    run_dashboard()
