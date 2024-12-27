from dash import html, dcc

class AnalysisCharts:
    def layout(self, symbols):
        return html.Div(
            children=[
                html.H3("Analyses"),
                dcc.Graph(
                    id="analyses-graph",
                    config={"displayModeBar": False},
                    style={"height": "600px"},
                ),
            ],
        )
    