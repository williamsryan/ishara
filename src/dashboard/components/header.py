from dash import html

def render_header():
    return html.Div(
        style={"backgroundColor": "#2b3e50", "padding": "10px"},
        children=[
            html.H1(
                "Ishara Trading Dashboard",
                style={"color": "white", "textAlign": "center", "marginBottom": "0"}
            ),
            html.P(
                "Real-time market analysis, alternative data insights, and predictive modeling",
                style={"color": "lightgray", "textAlign": "center", "marginTop": "5px"}
            ),
        ]
    )