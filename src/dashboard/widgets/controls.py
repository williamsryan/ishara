from dash import dcc, html
import dash_bootstrap_components as dbc
from src.utils.database import fetch_data

class Controls:
    def render(self, symbol_options):
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

        # Define options for feature selection
        feature_options = [
            {"label": "Low", "value": "low"},
            {"label": "High", "value": "high"},
            {"label": "Open", "value": "open"},
            {"label": "Close", "value": "close"},
            {"label": "Volume", "value": "volume"}
        ]

        return html.Div([
            html.H4("Controls", className="mb-3"),

            html.Label("Select Symbols"),
            dcc.Dropdown(
                id="symbol-selector",
                multi=True,
                options=symbol_options,
                placeholder="Loading symbols...",
                className="mb-3",
            ),
            # Select/Deselect Buttons
            dbc.Row([
                dbc.Col(dbc.Button("Select All", id="select-all", color="primary", className="me-2"), width="auto"),
                dbc.Col(dbc.Button("Deselect All", id="deselect-all", color="secondary"), width="auto"),
            ], className="mb-3"),

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

            # Feature Selection Dropdowns
            html.Label("Select Features for Analysis"),
            dcc.Dropdown(
                id="feature-selector",
                options=[
                    {"label": "Open", "value": "open"},
                    {"label": "Close", "value": "close"},
                    {"label": "High", "value": "high"},
                    {"label": "Low", "value": "low"},
                    {"label": "Volume", "value": "volume"},
                ],
                multi=True,
                placeholder="Select features for clustering",
                value=["low", "high"],  # Default features
            ),

            # Reduction Method Dropdown
            html.Label("Select Dimensionality Reduction Method"),
            dcc.Dropdown(
                id="reduction-method-dropdown",
                options=[
                    {"label": "t-SNE", "value": "tsne"},
                    {"label": "PCA", "value": "pca"},
                ],
                value="tsne",  # Default
                clearable=False,
                className="mb-3",
            ),

            dbc.Checklist(
                options=[{"label": "Overlay Alternative Data", "value": 1}],
                id="overlay-toggle",
                switch=True,
                className="mt-3",
            ),
        ], className="p-3 bg-white rounded shadow-sm")
    