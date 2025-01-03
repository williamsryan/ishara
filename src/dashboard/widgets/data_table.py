from dash import html, dash_table
import dash_bootstrap_components as dbc
from src.utils.database import fetch_as_dataframe

class DataTable:
    def layout(self, symbols, start_date, end_date):
        """
        Layout for the Data Table with pagination and editable labels.
        """
        if not symbols:
            return html.Div("⚠️ No symbols selected.", className="text-warning p-3")
        
        # Fetch data
        try:
            query = f"""
                SELECT *
                FROM historical_market_data
                WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
                AND datetime BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY datetime DESC
            """
            data = fetch_as_dataframe(query)
            if data.empty:
                return html.Div("⚠️ No data available for the selected symbols and date range.", className="text-warning p-3")
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return html.Div(f"❌ Error fetching data: {str(e)}", className="text-danger p-3")

        # Add editable "Label" column
        data["Label"] = ""

        return html.Div([
            dash_table.DataTable(
                id="data-table",
                columns=[{"name": col, "id": col, "deletable": False, "selectable": True} for col in data.columns],
                data=data.to_dict("records"),
                editable=True,  # Enable editing of all cells
                filter_action="native",  # Allow filtering within the table
                sort_action="native",  # Enable sorting on columns
                sort_mode="multi",  # Allow multi-column sorting
                row_deletable=False,  # Prevent row deletion
                page_action="native",  # Enable pagination
                page_current=0,  # Start at the first page
                page_size=10,  # Number of rows per page
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#f8f9fa",
                    "fontWeight": "bold",
                    "border": "1px solid #dee2e6"
                },
                style_cell={
                    "backgroundColor": "white",
                    "color": "black",
                    "textAlign": "left",
                    "border": "1px solid #dee2e6"
                },
                style_data={
                    "border": "1px solid #dee2e6"
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"}
                ],
                style_filter={
                    "backgroundColor": "white",
                    "border": "1px solid #dee2e6",
                    "padding": "0.5rem"
                }
            )
        ])
    