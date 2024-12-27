from dash import html

class Sidebar:
    def render(self):
        return html.Div(
            className="p-3 bg-light rounded shadow-sm",
            children=[
                html.H4("Navigation"),
                html.Ul([
                    html.Li(html.A("Price Chart", href="#price-chart")),
                    html.Li(html.A("Alternative Data", href="#alternative-data")),
                    html.Li(html.A("Data Table", href="#data-table")),
                    html.Li(html.A("Analyses", href="#analyses")),
                ])
            ]
        )
    