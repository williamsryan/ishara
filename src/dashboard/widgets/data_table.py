from dash import html, dash_table
from src.utils.database import fetch_data


class DataTable:
    def layout(self, symbols, start_date, end_date):
        """
        Generate the layout for the data table.

        Args:
            symbols (list): List of symbols to fetch data for.
            start_date (str): Start date for the query range.
            end_date (str): End date for the query range.

        Returns:
            dash.html.Div or dash.dash_table.DataTable: DataTable or message if no data available.
        """
        # Construct the query
        query = f"""
            SELECT *
            FROM historical_market_data
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
              AND datetime BETWEEN %s AND %s
            ORDER BY datetime DESC
        """
        params = tuple(symbols) + (start_date, end_date)

        try:
            # Fetch data using fetch_data
            results = fetch_data(query, params=params)

            if not results or len(results) == 0:
                return html.Div("⚠️ No data available for the selected criteria.", className="text-warning p-3")

            # Convert to columns and rows for Dash DataTable
            columns = [{"name": col, "id": col} for col in results[0].keys()]
            data = [row for row in results]

            return dash_table.DataTable(
                id="data-table",
                columns=columns,
                data=data,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "whiteSpace": "normal"},
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_selectable="multi",
                page_size=10,
            )
        except Exception as e:
            return html.Div(f"❌ Error loading data: {str(e)}", className="text-danger p-3")
        