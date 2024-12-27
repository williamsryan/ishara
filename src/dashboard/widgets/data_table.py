from dash import dash_table, html

class DataTableWidget:
    def layout(self, symbols):
        return html.Div(
            children=[
                html.H3("Data Table"),
                dash_table.DataTable(
                    id="data-table",
                    columns=[{"name": col, "id": col} for col in ["Symbol", "Price", "Volume"]],
                    data=[{"Symbol": s, "Price": "N/A", "Volume": "N/A"} for s in symbols],
                    style_table={"overflowX": "auto"},
                ),
            ]
        )
    