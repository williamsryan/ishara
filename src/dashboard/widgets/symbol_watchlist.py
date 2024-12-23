from dash import dcc, html

class SymbolWatchlist:
    def layout(self):
        return html.Div([
            html.H4("Symbol Watchlist"),
            dcc.Dropdown(
                id="symbol-selector",
                options=[],  # Populated dynamically
                multi=True,
                placeholder="Select symbols (e.g., AAPL, MSFT)"
            ),
            html.Button("Refresh Symbols", id="refresh-symbols", n_clicks=0)
        ])
    