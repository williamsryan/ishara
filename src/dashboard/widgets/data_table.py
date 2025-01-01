from dash import html, dash_table
from src.utils.database import fetch_data

class DataTable:
    @staticmethod
    def layout(symbols, start_date=None, end_date=None):
        """
        Generate the layout for the data table with enhanced features.

        Args:
            symbols (list): List of symbols to fetch data for.
            start_date (str, optional): Start date for the query range.
            end_date (str, optional): End date for the query range.

        Returns:
            dash.html.Div or dash.dash_table.DataTable: DataTable or message if no data available.
        """
        if not symbols:
            return html.Div("⚠️ No symbols selected. Please select symbols to display data.", className="text-warning p-3")

        query = f"""
            SELECT *
            FROM historical_market_data
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
        """
        params = list(symbols)
        if start_date and end_date:
            query += " AND datetime BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        query += " ORDER BY datetime DESC"

        try:
            results = fetch_data(query, tuple(params))
            if results.empty:
                return html.Div("⚠️ No data available for the selected criteria.", className="text-warning p-3")

            return dash_table.DataTable(
                data=results.to_dict("records"),
                columns=[{"name": col, "id": col} for col in results.columns],
                style_table={"overflowX": "auto", "marginTop": "20px"},
                style_header={
                    "backgroundColor": "#202020",
                    "fontWeight": "bold",
                    "border": "1px solid white",
                    "color": "white",
                },
                style_cell={
                    "padding": "10px",
                    "textAlign": "left",
                    "border": "1px solid grey",
                    "backgroundColor": "#303030",
                    "color": "#F0F0F0",
                    "fontFamily": "Arial, sans-serif",
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#282828"},
                ],
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_current=0,
                page_size=15,
                export_format="csv",
                export_headers="display",
                merge_duplicate_headers=True,
            )
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return html.Div(f"❌ Error loading data: {str(e)}", className="text-danger p-3")
        