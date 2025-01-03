from dash import dash_table, html, Input, Output, State, callback
import pandas as pd
from src.utils.database import insert_data, fetch_data

class DataTable:
    @staticmethod
    def layout(symbols, start_date=None, end_date=None):
        """
        Create a data table layout with editable labels.
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
                return html.Div("⚠️ No data available for the selected symbols.", className="text-warning p-3")
            
            # Ensure Label column exists
            if "label" not in results.columns:
                results["label"] = ""
            
            return html.Div([
                dash_table.DataTable(
                    id="data-table",
                    data=results.to_dict("records"),
                    columns=[
                        {"name": "id", "id": "id", "type": "numeric"},
                        {"name": "symbol", "id": "symbol", "type": "text"},
                        {"name": "datetime", "id": "datetime", "type": "datetime"},
                        {"name": "open", "id": "open", "type": "numeric"},
                        {"name": "high", "id": "high", "type": "numeric"},
                        {"name": "low", "id": "low", "type": "numeric"},
                        {"name": "close", "id": "close", "type": "numeric"},
                        {"name": "volume", "id": "volume", "type": "numeric"},
                        {"name": "label", "id": "label", "editable": True, "presentation": "dropdown"}
                    ],
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_deletable=False,
                    page_size=15,  # Paginated view
                    dropdown={
                        "label": {
                            "options": [
                                {"label": "Red", "value": "#ffcccc"},
                                {"label": "Blue", "value": "#cce5ff"},
                                {"label": "Green", "value": "#d4edda"},
                                {"label": "Yellow", "value": "#fff3cd"},
                                {"label": "White", "value": "#ffffff"},
                            ]
                        }
                    },
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
                        # Default styling for rows based on color
                        {
                            "if": {"column_id": "color"},
                            "backgroundColor": "inherit",
                        }
                    ]
                )
            ])
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return html.Div(f"❌ Error loading data: {str(e)}", className="text-danger p-3")

    @staticmethod
    @callback(
        [
            Output("data-table", "style_data_conditional"),
            Output("data-table", "data"),
        ],
        [
            Input("data-table", "data_previous"),
            Input("data-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_table_updates(previous_data, updated_data):
        style_data_conditional = []

        if updated_data:
            # Apply user-defined styles for rows
            for row in updated_data:
                if "label" in row and row["label"]:
                    style_data_conditional.append({
                        "if": {"filter_query": f"{{label}} = '{row['label']}'"},
                        "backgroundColor": row.get("color", "#ffffff"),
                        "color": "black",
                    })

            # Save changed labels and colors to the database
            if previous_data:
                for new_row, old_row in zip(updated_data, previous_data):
                    if new_row.get("label") != old_row.get("label") or new_row.get("color") != old_row.get("color"):
                        try:
                            insert_data("symbol_labels", [{
                                "symbol": new_row["symbol"],
                                "label": new_row["label"],
                                "color": new_row.get("color", "#ffffff"),
                            }])
                        except Exception as e:
                            print(f"❌ Error inserting label/color: {e}")

        # Fetch and update the table data
        return style_data_conditional, updated_data
    