# Ishara: Algorithmic Trading Platform

Ishara (الإشارة) is a modular algorithmic trading platform designed for:
1. Fetching and integrating alternative data (QuiverQuant, Alpaca, etc.).
2. Conducting quantitative research with historical and real-time data.
3. Backtesting trading strategies.
4. Deploying and monitoring automated trading algorithms.

## **Features**
- **Data Sources**:
  - **QuiverQuant**: Fetch alternative data like congressional trades, sentiment, etc.
  - **Alpaca**: Stream live market data and fetch historical stock data.
- **Backtesting**:
  - Built-in support for backtesting with Backtrader.
- **Dashboard**:
  - Interactive dashboards using Dash and Plotly.
- **Cloud Deployment**:
  - Designed for deployment on AWS using EC2 and RDS.

---

## **Project Structure**
```plaintext
ishara/
├── data/                   # Organized storage for data
│   ├── raw/                # Raw fetched data (e.g., API responses)
│   ├── processed/          # Cleaned and normalized data
│   ├── derived/            # Derived metrics (e.g., P/E ratio, momentum)
├── database/               # Database schema, migrations, and setup scripts
│   ├── schema.sql          # Unified database schema
│   ├── migrations/         # Incremental migration scripts
├── notebooks/              # Jupyter notebooks for research and prototyping
├── src/                    # Source code
│   ├── fetchers/           # API fetchers
│   │   ├── alpaca_fetcher.py
│   │   ├── yahoo_finance_fetcher.py
│   │   ├── google_trends_fetcher.py
│   │   ├── reddit_sentiment_fetcher.py
│   │   ├── websocket_stream.py
│   ├── processors/         # Analysis and computation scripts
│   │   ├── clustering_analysis.py
│   │   ├── regime_analysis.py
│   │   ├── derived_metrics.py
│   ├── backtesting/        # Backtesting engine
│   │   ├── backtrader_engine.py
│   │   ├── strategy_templates/
│   │   │   ├── moving_average.py
│   │   │   ├── momentum_strategy.py
│   ├── dashboard/          # Visualization and dashboard components
│   │   ├── app.py          # Main app file
│   │   ├── components/     # Modular UI components
│   │   │   ├── clustering_chart.py
│   │   │   ├── regime_chart.py
│   │   │   ├── performance_chart.py
│   │   │   ├── data_table.py
│   │   │   ├── tabs.py
│   ├── utils/              # Shared utilities
│   │   ├── database.py     # DB connection and query utilities
│   │   ├── config.py       # Configuration variables
│   │   ├── logger.py       # Logging utilities
├── tests/                  # Unit and integration tests
│   ├── test_fetchers.py
│   ├── test_processors.py
│   ├── test_dashboard.py
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
├── run.py                  # Entry point to launch the system
```

## Data Source Notes

### Feature Selection for Clustering
Here’s a breakdown of the most relevant features for clustering in a financial context:

1. **Price and Volume Metrics**
  - **Use Case**: Cluster symbols based on trading activity and price ranges.
  - **Features**: open, close, high, low, volume.
  - **Why**: These features capture the raw market behavior, which may reveal clusters of high vs. low activity symbols or stocks with similar trading ranges.

2. **Volatility**
  - **Use Case**: Group symbols by their risk profile.
  - **Features**: Standard deviation of returns, or high/low price range divided by the mean.
  - **Why**: Stocks with high volatility often behave differently than low-volatility ones, which can be useful for risk-aware strategies.

3. **Price Momentum**
  - **Use Case**: Detect symbols with similar momentum trends.
  - **Features**: Momentum indicators like close - SMA(close), RSI.
  - **Why**: Momentum clusters can highlight trending vs. mean-reverting stocks.

4. **Returns**
  - **Use Case**: Classify symbols by profitability.
  - **Features**: Daily, weekly, or monthly returns.
  - **Why**: Helps identify outperforming vs. underperforming symbols over various time frames.

5. **Liquidity**
  - **Use Case**: Identify high vs. low liquidity stocks.
  - **Features**: volume, bid-ask spread.
  - **Why**: Liquidity affects transaction costs and volatility.

### Current Approach Plan

1. **Initial Clustering Features**:
  - **Start with**: high/low, volume, and volatility.
  - **Why**: These are straightforward and often reveal meaningful groupings.

2. **Advanced Features**:
  - **Add**: moving averages or returns over a time window for trend analysis.
  - **Use**: volatility-adjusted metrics to refine the clusters.

3. **Normalization**:
  - **Normalize**: all features to ensure scale differences (e.g., volume vs. close) don’t distort the clustering.

4. **Dimensionality Reduction**:
  - **Use**: PCA, t-SNE, or UMAP if the feature space is large, to reduce dimensions while preserving meaningful relationships.
