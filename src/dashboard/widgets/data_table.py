class DataTable:
    def layout(self, symbols, start_date, end_date):
        conn = connect_to_db()
        query = f"""
            SELECT *
            FROM historical_market_data
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
              AND datetime BETWEEN '{start_date}' AND '{end_date}'
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return html.Div("⚠️ No data available for the selected criteria.")

        return dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "whiteSpace": "normal"},
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            page_size=10
        )
    