from dash import dcc

class Tabs:
    def __init__(self):
        self.tabs = [
            {"label": "Price Chart", "value": "price-chart"},
            {"label": "Alternative Data", "value": "alternative-data"},
            {"label": "Data Table", "value": "data-table"},
            {"label": "Analyses", "value": "analyses"},
        ]

    def render(self):
        return dcc.Tabs(
            id="tabs",
            value="price-chart",
            children=[
                dcc.Tab(label=tab["label"], value=tab["value"]) for tab in self.tabs
            ],
        )
    