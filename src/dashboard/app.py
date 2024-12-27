from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from threading import Thread
from src.utils.database import connect_to_db
from src.fetchers.alpaca_realtime import fetch_real_time_data
from src.dashboard.components.header import Header
from src.dashboard.components.sidebar import Sidebar
from src.dashboard.widgets.controls import Controls
from src.dashboard.widgets.chart_components import PriceChart, AlternativeDataCharts

# Initialize the app with a sleek theme
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "📊 Ishara Trading Dashboard"

# Instantiate components and widgets
header = Header()
sidebar = Sidebar()
controls = Controls()
price_chart = PriceChart()
alternative_data = AlternativeDataCharts()

# App Layout
app.layout = dbc.Container(fluid=True, children=[
    # Header
    dbc.Row(dbc.Col(header.render(), width=12)),

    # Sidebar and Content
    dbc.Row([
        dbc.Col(sidebar.render(), width=3, style={"backgroundColor": "#f8f9fa"}),
        dbc.Col([
            controls.render(),
            dcc.Tabs(id="tabs", value="price-chart", children=[
                dcc.Tab(label="📈 Price Chart", value="price-chart"),
                dcc.Tab(label="📊 Alternative Data", value="alternative-data"),
            ]),
            html.Div(id="tab-content", className="p-3")
        ], width=9)
    ])
])

# Callbacks
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("symbol-selector", "value")]
)
def update_content(tab, symbols):
    if not symbols:
        return html.Div("⚠️ Please select symbols to display data.")

    if tab == "price-chart":
        return price_chart.layout(symbols)
    elif tab == "alternative-data":
        return alternative_data.layout(symbols)
    else:
        return html.Div("⚠️ Invalid tab selected!")

# Run Dashboard with Streaming
def run_dashboard():
    stream_thread = Thread(target=fetch_real_time_data)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard()
