import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from plotly.graph_objs import Scatter, Figure
from src.utils.database import connect_to_db

def perform_regime_analysis(symbols=None):
    """
    Performs regime analysis on company data and returns a visualization.
    Updates regime labels back to the database.
    """
    conn = connect_to_db()
    query = """
    SELECT symbol, datetime, log_returns
    FROM company_analysis
    """
    if symbols:
        symbol_filter = ",".join([f"'{s}'" for s in symbols])
        query += f" WHERE symbol IN ({symbol_filter}) ORDER BY datetime"

    # Fetch data
    data = pd.read_sql_query(query, conn)
    if data.empty:
        print("⚠️ No data available for regime analysis.")
        conn.close()
        return Figure()  # Return an empty figure for the dashboard

    # Preprocessing: Scale log returns
    scaler = StandardScaler()
    data["log_returns_scaled"] = scaler.fit_transform(data[["log_returns"]])

    # Apply Gaussian Mixture Model (GMM) for regime analysis
    gmm = GaussianMixture(n_components=3, random_state=42)
    data["regime"] = gmm.fit_predict(data[["log_returns_scaled"]])

    # Save regime results back to the database
    for _, row in data.iterrows():
        conn.execute("""
        UPDATE company_analysis
        SET regime_label = %s
        WHERE symbol = %s AND datetime = %s
        """, (int(row["regime"]), row["symbol"], row["datetime"]))
    conn.commit()
    conn.close()

    print("✅ Regime analysis results stored in the database.")

    # Generate visualization
    figure = Figure()
    for regime in data["regime"].unique():
        regime_data = data[data["regime"] == regime]
        figure.add_trace(Scatter(
            x=regime_data["datetime"],
            y=regime_data["log_returns"],
            mode="lines",
            name=f"Regime {regime}"
        ))

    figure.update_layout(
        title="Regime Analysis",
        xaxis_title="Datetime",
        yaxis_title="Log Returns",
        template="plotly_white"
    )
    return figure
