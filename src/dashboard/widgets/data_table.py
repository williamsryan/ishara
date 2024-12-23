from dash import dash_table, html
from src.utils.database import connect_to_db
import pandas as pd

class DataTableWidget:
    def layout(self, symbols):
        conn = connect_to_db()
        query = f"SELECT * FROM historical_market_data WHERE symbol IN ({','.join([f'\'{s}\'' for s in symbols])})"
        data = pd.read_sql(query, conn)
        conn.close()

        if data.empty:
            return html.Div("⚠️ No data available for the selected symbols.")
        
        return dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
            style_cell={"textAlign": "left"},
            filter_action="native",
            sort_action="native",
            page_size=10
        )
    