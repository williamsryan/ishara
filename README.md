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
├── data/                     # Data storage
│   ├── raw/                  # Raw data fetched from APIs
│   ├── processed/            # Cleaned and normalized data
├── database/                 # Database schema and SQL scripts
├── notebooks/                # Jupyter notebooks for exploration
├── src/                      # Core source code
│   ├── fetchers/             # API fetchers
│   ├── algorithms/           # Trading algorithms
│   ├── backtesting/          # Backtesting utilities
│   ├── dashboard/            # Visualization tools
│   ├── utils/                # Utilities for config and database connections
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation