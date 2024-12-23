import dash
from dash import dcc, html

def create_layout():
    return html.Div(
        children=[
            dcc.Tabs(
                id="tabs",
                value="tab-1",
                children=[
                    dcc.Tab(label="Market Overview", value="tab-1"),
                    dcc.Tab(label="Backtesting", value="tab-2"),
                    dcc.Tab(label="Portfolio", value="tab-3"),
                    dcc.Tab(label="Sentiment Analysis", value="tab-4"),
                ],
            ),
            html.Div(id="tab-content"),
        ],
    )
