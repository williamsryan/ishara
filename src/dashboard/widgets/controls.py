from dash import dcc, html
import dash_bootstrap_components as dbc

class Controls:
    def render(self):
        return html.Div([
            html.H4("Controls", className="mb-3"),
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
            html.Label("Select Symbols"),
            dcc.Dropdown(
                id="symbol-selector",
                multi=True,
                placeholder="Loading symbols...",
                className="mb-3"
            ),
            html.Label("Select Time Range"),
            dcc.DatePickerRange(
                id="date-picker",
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                display_format="YYYY-MM-DD",
                className="mb-3"
            ),
            dbc.Checklist(
                options=[{"label": "Overlay Alternative Data", "value": 1}],
                id="overlay-toggle",
                switch=True,
                className="mt-3",
            ),
        ], className="p-3 bg-white rounded shadow-sm")
    