from hmmlearn.hmm import GaussianHMM
import pandas as pd
from src.utils.database import connect_to_db

def perform_regime_analysis():
    conn = connect_to_db()
    query = """
    SELECT symbol, datetime, log_returns
    FROM company_analysis
    """
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Fit HMM for each symbol
    results = []
    for symbol in data["symbol"].unique():
        symbol_data = data[data["symbol"] == symbol].sort_values("datetime")
        X = symbol_data["log_returns"].values.reshape(-1, 1)

        hmm = GaussianHMM(n_components=2, covariance_type="full", random_state=42)
        hmm.fit(X)
        states = hmm.predict(X)

        symbol_data["regime"] = states
        results.append(symbol_data)

    # Concatenate results
    all_results = pd.concat(results)

    # Save regimes back to the database
    conn = connect_to_db()
    for _, row in all_results.iterrows():
        conn.execute("""
        UPDATE company_analysis
        SET regime = %s
        WHERE symbol = %s AND datetime = %s
        """, (row["regime"], row["symbol"], row["datetime"]))
    conn.commit()
    conn.close()

    print("✅ Regime detection results stored in the database.")
