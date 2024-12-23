from dash import dcc, html
import dash_bootstrap_components as dbc

def render_sidebar():
    return html.Div(
        style={
            "backgroundColor": "#f8f9fa",
            "padding": "15px",
            "height": "100vh",
            "borderRight": "1px solid #dcdcdc",
        },
        children=[
            html.H4("Navigation", style={"marginBottom": "15px"}),
            dbc.Nav(
                [
                    dbc.NavLink("Price Charts", href="/price-charts", active="exact"),
                    dbc.NavLink("Alternative Data", href="/alternative-data", active="exact"),
                    dbc.NavLink("Data Table", href="/data-table", active="exact"),
                    dbc.NavLink("Analyses", href="/analyses", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
            html.Hr(),
            html.Div(
                [
                    html.H6("Preferences"),
                    dcc.Checklist(
                        options=[
                            {"label": "Dark Mode", "value": "dark"},
                            {"label": "Show Tooltips", "value": "tooltips"},
                        ],
                        value=[],
                        id="preferences-checklist",
                        inline=True,
                    ),
                ],
                style={"marginTop": "15px"},
            ),
        ],
    )
