import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from threading import Thread
from src.utils.database import connect_to_db
from src.fetchers.alpaca_realtime import start_stream
from src.processors.regime_analysis import perform_regime_analysis
from src.processors.clustering_analysis import perform_clustering_analysis

# Initialize the app with a sleek theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "📊 Ishara Trading Dashboard"

# Helper to fetch data
def fetch_data(table, symbols=None, limit=10):
    """
    Fetch data from the specified table in the database.
    """
    try:
        engine = connect_to_db()
        symbol_filter = f"WHERE symbol IN ({','.join([f'\'{s}\'' for s in symbols])})" if symbols else ""
        query = f"SELECT * FROM {table} {symbol_filter} ORDER BY datetime DESC LIMIT {limit}"
        print(f"🔍 Query: {query}")
        data = pd.read_sql(query, con=engine)

        if data.empty:
            print(f"⚠️ No data found in table {table} for symbols {symbols}.")
            return pd.DataFrame()

        print(f"✅ Data fetched:\n{data.head()}")
        data["datetime"] = pd.to_datetime(data["datetime"])
        return data

    except Exception as e:
        print(f"❌ Error fetching data from {table}: {e}")
        return pd.DataFrame()

# Layout Components
def create_tabs():
    return dcc.Tabs(id="tabs", value="price-chart", children=[
        dcc.Tab(label="📈 Price Chart", value="price-chart"),
        dcc.Tab(label="📊 Alternative Data", value="alternative-data"),
        dcc.Tab(label="🗃 Data Table", value="table-view"),
        dcc.Tab(label="📐 Analyses", value="analyses"),
    ])

controls = dbc.Col([
    html.Div([
        html.H4("User Controls", className="mb-3"),

        # Data Source Dropdown
        html.Label("Select Data Source"),
        dcc.Dropdown(
            id="data-source",
            options=[
                {"label": "Real-Time Data", "value": "real_time_market_data"},
                {"label": "Yahoo Finance", "value": "yahoo_finance_data"},
                {"label": "Alternative Data", "value": "alternative_data"}
            ],
            value="real_time_market_data",
            clearable=True,
            className="mb-3"
        ),

        # Symbol Selector
        html.Label("Select Symbols"),
        dcc.Dropdown(
            id="symbol-selector",
            multi=True,
            placeholder="Select symbols (e.g., AAPL, MSFT)",
            className="mb-3"
        ),

        # Time Range Picker
        html.Label("Select Time Range"),
        dcc.DatePickerRange(
            id="date-picker",
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            display_format="YYYY-MM-DD",
            className="mb-3"
        ),

        # Overlay Toggle
        dbc.Checklist(
            options=[{"label": "Overlay Alternative Data", "value": 1}],
            id="overlay-toggle",
            switch=True,
            className="mt-3",
        ),
    ], className="bg-light p-3 rounded shadow-sm")
], width=3)

# Main Layout
app.layout = dbc.Container(fluid=True, children=[
    # Header
    dbc.Row([
        dbc.Col(html.H2("📊 Ishara Trading Platform", className="text-center text-light bg-dark p-3"), width=12)
    ]),

    # Controls and Tabs
    dbc.Row([
        controls,
        dbc.Col([
            create_tabs(),
            html.Div(id="tab-content", className="p-3"),
        ], width=9)
    ])
])

# Callbacks
@app.callback(
    [Output("symbol-selector", "options"), Output("symbol-selector", "value")],
    Input("data-source", "value")
)
def update_symbols(source):
    data = fetch_data(source, limit=1000)
    if data.empty:
        return [], []
    symbols = [{"label": symbol, "value": symbol} for symbol in data["symbol"].unique()]
    return symbols, [symbols[0]["value"]] if symbols else []

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("data-source", "value"), Input("symbol-selector", "value"),
     Input("date-picker", "start_date"), Input("date-picker", "end_date"),
     Input("overlay-toggle", "value")]
)
def update_content(tab, source, symbols, start_date, end_date, overlay_toggle):
    if not symbols:
        return html.Div("⚠️ Please select symbols to display data.")

    data = fetch_data(source, symbols=symbols, limit=1000)

    # Separate fetching for alternative data (independent of overlay toggle)
    alt_data = fetch_data("alternative_data", symbols=symbols, limit=1000) if tab == "alternative-data" else None

    if data.empty and tab not in ["analyses", "alternative-data"]:
        return html.Div("⚠️ No data available for the selected criteria.", className="error-message")

    start_date = start_date or data["datetime"].min() if not data.empty else None
    end_date = end_date or data["datetime"].max() if not data.empty else None
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)

    if tab == "price-chart":
        # Price Chart Tab
        figure = go.Figure()
        for symbol in symbols:
            symbol_data = data[(data["symbol"] == symbol) &
                               (data["datetime"] >= start_date) &
                               (data["datetime"] <= end_date)]
            if not symbol_data.empty:
                figure.add_trace(go.Scatter(x=symbol_data["datetime"], y=symbol_data["close"],
                                            mode="lines", name=f"{symbol} Price"))
        figure.update_layout(title="Price Chart", template="seaborn")
        return dcc.Graph(figure=figure)

    elif tab == "alternative-data":
        if alt_data is None or alt_data.empty:
            return html.Div("⚠️ No alternative data available for the selected symbols.")

        sentiment_data = alt_data[alt_data["metric"] == "sentiment_score"]
        mentions_data = alt_data[alt_data["metric"] == "mentions"]

        sentiment_figure = go.Figure()
        mentions_figure = go.Figure()

        # Sentiment Graph
        for symbol in symbols:
            symbol_sentiment = sentiment_data[sentiment_data["symbol"] == symbol]
            sentiment_figure.add_trace(go.Scatter(
                x=symbol_sentiment["datetime"], y=symbol_sentiment["value"],
                mode="lines", name=f"{symbol} Sentiment"
            ))
        sentiment_figure.update_layout(
            title="Sentiment Trend Over Time", xaxis_title="Datetime", yaxis_title="Sentiment Score",
            template="seaborn"
        )

        # Mentions Graph
        for symbol in symbols:
            symbol_mentions = mentions_data[mentions_data["symbol"] == symbol]
            mentions_figure.add_trace(go.Bar(
                x=symbol_mentions["datetime"], y=symbol_mentions["value"],
                name=f"{symbol} Mentions"
            ))
        mentions_figure.update_layout(
            title="Google Mentions Over Time", xaxis_title="Datetime", yaxis_title="Mentions",
            template="plotly_white"
        )

        # Display graphs and table
        return html.Div([
            dcc.Graph(figure=sentiment_figure),
            dcc.Graph(figure=mentions_figure),
            dash_table.DataTable(
                id="alt-data-table",
                columns=[{"name": col, "id": col} for col in alt_data.columns],
                data=alt_data.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                style_cell={"textAlign": "left", "whiteSpace": "normal"},
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_selectable="multi",
                page_size=10,
                selected_rows=[],
            )
        ], className="p-3")

    elif tab == "table-view":
        # Historical Data Table
        data = fetch_data("historical_market_data", symbols=symbols)
        return dash_table.DataTable(
            id="historical_data_table",
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
            style_cell={"textAlign": "left", "whiteSpace": "normal"},
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            page_size=10,
            selected_rows=[],
        )

    elif tab == "analyses":
        # Analyses Tab
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H4("Clustering Analysis", className="mt-3"),
                    dcc.Graph(id="clustering-result")
                ], width=6),
                dbc.Col([
                    html.H4("Regime Analysis", className="mt-3"),
                    dcc.Graph(id="regime-result")
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Run Analyses", id="run-analyses", color="primary", className="mt-3"),
                ], width=12, className="d-flex justify-content-center")
            ])
        ])
    
# Callbacks to Trigger Analyses
@app.callback(
    [Output("clustering-result", "figure"), Output("regime-result", "figure")],
    [Input("run-analyses", "n_clicks")],
    [dash.dependencies.State("symbol-selector", "value"),
     dash.dependencies.State("data-source", "value")]
)
def run_analyses(n_clicks, symbols, source):
    if not n_clicks or not symbols:
        return go.Figure(), go.Figure()

    try:
        # Perform Clustering Analysis
        clustering_results = perform_clustering_analysis(symbols=symbols)
        clustering_fig = go.Figure()

        # Visualize Clustering Results
        for cluster_id, cluster_data in clustering_results.groupby("cluster"):
            clustering_fig.add_trace(go.Scatter(
                x=cluster_data["x"],
                y=cluster_data["y"],
                mode="markers",
                name=f"Cluster {cluster_id}",
                marker=dict(size=10)
            ))

        clustering_fig.update_layout(
            title="Clustering Analysis Results",
            xaxis_title="Feature 1",
            yaxis_title="Feature 2",
            template="plotly_white"
        )

        # Perform Regime Analysis
        regime_results = perform_regime_analysis(symbols=symbols)
        regime_fig = go.Figure()

        # Visualize Regime Results
        for regime_id, regime_data in regime_results.groupby("regime"):
            regime_fig.add_trace(go.Scatter(
                x=regime_data["datetime"],
                y=regime_data["value"],
                mode="lines",
                name=f"Regime {regime_id}"
            ))

        regime_fig.update_layout(
            title="Regime Analysis Results",
            xaxis_title="Datetime",
            yaxis_title="Metric Value",
            template="plotly_white"
        )

        return clustering_fig, regime_fig
    except Exception as e:
        print(f"❌ Error performing analyses: {e}")
        return go.Figure(), go.Figure()

# Run Streamer
def run_dashboard_with_stream():
    stream_thread = Thread(target=start_stream)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard_with_stream()
