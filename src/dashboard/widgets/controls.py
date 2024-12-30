from dash import dcc, html
import dash_bootstrap_components as dbc
from src.utils.database import fetch_data

class Controls:
    def render(self):
        # Fetch the default date range from the database
        query = """
            SELECT MIN(datetime) AS start_date, MAX(datetime) AS end_date
            FROM historical_market_data
        """
        results = fetch_data(query)

        if results.empty:
            start_date = None
            end_date = None
        else:
            start_date = results.iloc[0]["start_date"]
            end_date = results.iloc[0]["end_date"]

        return html.Div([
            html.H4("Controls", className="mb-3"),
            # html.Label("Select Data Source"),
            # dcc.Dropdown(
            #     id="data-source",
            #     options=[
            #         {"label": "Real-Time Data", "value": "real_time_market_data"},
            #         {"label": "Yahoo Finance", "value": "yahoo_finance_data"},
            #         {"label": "Alternative Data", "value": "alternative_data"}
            #     ],
            #     value="real_time_market_data",
            #     clearable=True,
            #     className="mb-3"
            # ),
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
                start_date_placeholder_text="Start Date (optional)",
                end_date_placeholder_text="End Date (optional)",
                start_date=start_date,
                end_date=end_date,
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
    