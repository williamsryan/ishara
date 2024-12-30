from dash import html, dash_table
from src.utils.database import fetch_data

class DataTable:
    def layout(self, symbols, start_date=None, end_date=None):
        """
        Generate the layout for the data table.

        Args:
            symbols (list): List of symbols to fetch data for.
            start_date (str, optional): Start date for the query range.
            end_date (str, optional): End date for the query range.

        Returns:
            dash.html.Div or dash.dash_table.DataTable: DataTable or message if no data available.
        """

        if not symbols:
            return html.Div("⚠️ No symbols selected. Please select symbols to display data.", className="text-warning p-3")

        # Construct the query dynamically
        query = f"""
            SELECT *
            FROM historical_market_data
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
        """
        params = list(symbols)

        # Add date range filter only if start_date and end_date are provided
        if start_date and end_date:
            query += " AND datetime BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        query += " ORDER BY datetime DESC"

        try:
            results = fetch_data(query, tuple(params))

            if results.empty:
                return html.Div("⚠️ No data available for the selected criteria.", className="text-warning p-3")

            columns = [{"name": col, "id": col} for col in results.columns]
            return dash_table.DataTable(
                id="data-table",
                columns=columns,
                data=results.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "whiteSpace": "normal"},
                filter_action="native",
                sort_action="native",
                page_size=10,
            )
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return html.Div(f"❌ Error loading data: {str(e)}", className="text-danger p-3")
        