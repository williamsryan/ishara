from dash import dcc, html

def render_tabs():
    return dcc.Tabs(
        id="tabs",
        children=[
            dcc.Tab(label="Price Charts", value="price-chart"),
            dcc.Tab(label="Alternative Data", value="alternative-data"),
            dcc.Tab(label="Data Table", value="data-table"),
            dcc.Tab(label="Analyses", value="analyses"),
        ],
        value="price-chart",
        style={"padding": "10px"},
    )
