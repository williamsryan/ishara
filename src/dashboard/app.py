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
    dbc.Row(dbc.Col(html.H2("📊 Ishara Trading Platform", className="text-center bg-dark text-light py-3"))),

    # Sidebar and Tabs
    dbc.Row([
        dbc.Col(
            controls.render(), 
            width=3, 
            className="bg-light p-3 border-end vh-100 sticky-top"
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
            html.Div(id="tab-content", className="p-3"),
        ], width=9),
    ]),
])

# Callback to dynamically update tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("symbol-selector", "value"),
     Input("date-picker", "start_date"), Input("date-picker", "end_date"),
     Input("overlay-toggle", "value")]
)
def update_content(tab, symbols, start_date, end_date, overlay_toggle):
    """
    Update the tab content dynamically based on the selected tab and user inputs.
    """
    # Ensure symbols are selected
    if not symbols:
        return dcc.Loading(
            type="circle",
            children=html.Div("⚠️ Please select symbols to display data.", className="text-warning p-3"),
        )

    try:
        # Render content for each tab
        if tab == "price-chart":
            # Render the Price Chart
            return dcc.Loading(
                type="circle",
                children=price_chart.layout(symbols, start_date, end_date)
            )
        elif tab == "alternative-data":
            # Render Alternative Data Charts
            return dcc.Loading(
                type="circle",
                children=alternative_data.layout(symbols, start_date, end_date, overlay_toggle)
            )
        elif tab == "data-table":
            # Render the Data Table
            return dcc.Loading(
                type="circle",
                children=data_table.layout(symbols, start_date, end_date)
            )
        elif tab == "analyses":
            # Render Analyses Tab
            return dcc.Loading(
                type="circle",
                children=analyses.layout()
            )
        else:
            # Handle invalid tab selections
            return dcc.Loading(
                type="circle",
                children=html.Div("⚠️ Invalid tab selected.", className="text-danger p-3"),
            )
    except Exception as e:
        # Handle errors and display a user-friendly message
        return dcc.Loading(
            type="circle",
            children=html.Div(
                f"❌ An error occurred while loading the content: {str(e)}",
                className="text-danger p-3"
            ),
        )

@app.callback(
    [Output("analysis-status", "children"), Output("tab-content", "children")],
    [Input("run-analysis", "n_clicks")],
    [State("symbol-selector", "value"), State("date-picker", "start_date"), State("date-picker", "end_date")]
)
def run_analysis(n_clicks, symbols, start_date, end_date):
    if not n_clicks:
        return "", html.Div("⚠️ Please select symbols and run an analysis.")

    # Display running status
    status_message = "⏳ Running analyses... This may take a few moments."

    # Call the analysis function
    perform_clustering_analysis(symbols)

    # Update results in the tab
    analyses_tab = Analyses().layout()
    status_message = "✅ Analysis complete! Results are updated."

    return status_message, analyses_tab

# Run the dashboard and real-time data streamer
def run_dashboard():
    stream_thread = Thread(target=fetch_real_time_data)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard()
