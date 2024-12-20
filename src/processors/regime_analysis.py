import pandas as pd
import numpy as np
from plotly.graph_objs import Box, Figure
from src.utils.database import connect_to_db

def perform_regime_analysis(data, symbols=None):
    """
    Identifies market regimes and returns a visualization.
    """
    if data.empty:
        print("⚠️ No data available for regime analysis.")
        return Figure()

    # Define regimes based on log returns
    data["Regime"] = pd.cut(
        data["log_returns"],
        bins=[-np.inf, -0.02, 0.02, np.inf],
        labels=["Bearish", "Neutral", "Bullish"]
    )

    # Save regime labels to the database
    conn = connect_to_db()
    for _, row in data.iterrows():
        conn.execute("""
        UPDATE company_analysis
        SET regime_label = %s
        WHERE symbol = %s
        """, (row["Regime"], row["symbol"]))
    conn.commit()
    conn.close()

    print("✅ Regime analysis results stored in the database.")

    # Generate visualization
    figure = Figure()
    for regime in data["Regime"].unique():
        regime_data = data[data["Regime"] == regime]
        figure.add_trace(Box(
            y=regime_data["log_returns"],
            name=f"{regime} Regime",
            boxmean=True
        ))

    figure.update_layout(
        title="Regime Analysis",
        yaxis_title="Log Returns",
        template="plotly_dark"
    )
    return figure
