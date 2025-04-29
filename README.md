<<<<<<< HEAD
# الإشارة: Unified Budgeting & Trading Intelligence Platform

**Ishara** is a modular, full-stack platform designed to bring together personal financial management, strategy-driven algorithmic trading, and real-time broker execution into one cohesive and programmable interface.

It is designed with both transparency and extensibility in mind, and is structured as a publishable project for self-documentation and reproducible builds. Users can configure it to connect live broker accounts, simulate trades using historical data, or create their own data workflows for analysis and decision making.

---

## ✨ Features Overview

| Module | Description |
|--------|-------------|
| Google Sheets Integration | OAuth login to Google Drive, select Sheets to connect as data sources (budget or strategy) |
| Budgeting Dashboard | Visual summary of user finances including trends, category grouping, monthly diffs, etc. |
| Trading Strategy Builder | UI-based rule engine for building and editing strategies using visual blocks or schema JSON |
| Broker Management | Dynamic broker selector (Alpaca, IBKR, future support for custom APIs) |
| Strategy Execution Engine | Run strategy logic on live market feeds or backtesting simulations |
| Data Ingestion & Filtering | Modular input/output engine for parsing, transforming, and feeding data into workflows |
| Backtesting Engine | Evaluate strategies historically using candle or tick data |
| Execution Logs | Persistent logging of all orders, trades, and P&L metrics |

---

## 💡 Philosophy

Ishara is built on three core principles:

1. **Modular Composition** — separate concerns into composable units for ingestion, logic, and output.
2. **User Empowerment** — allow anyone to define, test, and improve trading workflows visually or via config.
3. **Transparency & Reproducibility** — log everything, share easily, and enable others to learn and remix.

---

## 🎓 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, React, TailwindCSS, Plotly.js, React Query |
| Backend | Go (Golang), REST API architecture |
| Auth | Google OAuth2 (via NextAuth.js) |
| Brokers | Alpaca (REST/stream), Interactive Brokers (via TWS Gateway) |
| Database | In-memory or SQLite (initial); Postgres/Timescale (future) |
| Storage | Google Sheets, Local JSON, WebSocket/REST API feeds |

---

## 📁 Project Structure

```text
ishara-unified/
├── frontend/                # Next.js UI (React + Tailwind)
│   ├── pages/              # App pages (dashboard, auth, etc.)
│   ├── components/         # Shared UI components
│   ├── lib/                # Client helpers (OAuth, Sheets API)
│   ├── styles/             # Tailwind config and global CSS
│   └── package.json        # Project metadata
├── backend/                # Golang backend
│   ├── cmd/ishara/         # Entrypoint
│   ├── internal/
│   │   ├── handlers/       # HTTP route handlers
│   │   ├── services/       # Sheets, Alpaca, IBKR logic
│   │   ├── config/         # App config (env, YAML, secrets)
│   └── pkg/                # Shared libraries/utilities
├── docs/                   # System design diagrams, blog outlines
├── scripts/                # Utility scripts and automation
└── README.md               # This document
```

---

## ⚙️ Local Development

### Backend Setup
```bash
cd backend
PORT=8080 go run cmd/ishara/main.go
```
Access: [http://localhost:8080/health](http://localhost:8080/health)

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access: [http://localhost:3000](http://localhost:3000)

---

## 🔧 Configuration Options

### `.env` (Frontend)
```dotenv
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxx
NEXT_PUBLIC_GOOGLE_CLIENT_SECRET=xxx
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

### `.env` (Backend)
```dotenv
PORT=8080
ALPACA_API_KEY=xxx
ALPACA_SECRET_KEY=xxx
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
```

### `config.yaml` (Optional override)
```yaml
broker:
  default: "alpaca"
  alpaca:
    paper: true
    key: ${ALPACA_API_KEY}
    secret: ${ALPACA_SECRET_KEY}
  ibkr:
    host: ${IBKR_HOST}
    port: ${IBKR_PORT}

strategy:
  max_positions: 5
  risk_model: "fixed_fraction"
```

---

## 📄 Planned API Endpoints (Backend)

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Server healthcheck |
| `POST /auth/google` | Google OAuth2 callback handler |
| `GET /sheets/list` | Fetch user Sheet list (Google Drive) |
| `POST /sheets/select` | Select sheet for ingest/budget/strategy |
| `POST /strategy/backtest` | Run backtest simulation |
| `POST /strategy/execute` | Execute a live strategy against current data |
| `GET /strategy/logs` | Return recent trade logs |

---

## 📖 Blogging Plan (Live Project Notes)

| Blog # | Title |
|--------|-------|
| 1 | Building a Finance + Trading Dashboard with Google Sheets and React |
| 2 | Visual Strategy Definition: From UI to Execution in Go |
| 3 | Connecting Real Brokers to Your Own Algo Platform |
| 4 | Designing a Modular Trading System for Humans |
| 5 | Lessons Learned Building a Personal Finance Engine From Scratch |

---

## ✈ Future Roadmap

- [ ] Budget visualizations (monthly trends, waterfall charts)
- [ ] Strategy versioning + audit logs
- [ ] Broker auth module UI
- [ ] Live chart overlays (candles, indicators, annotations)
- [ ] Options scanner (based on Greeks)
- [ ] AI co-pilot for strategy hints / anomalies
- [ ] Exportable JSON strategy schema

---

## 🚀 License

TODO.
=======
# الإشارة: Algorithmic Trading Platform

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

---

### Development Notes

The tested version of Python that works with PyTorch is 3.11.6.
This was developed using v3.13 which didn't allow the scraper to work.

#### Backtesting Commands
```bash
python main.py backtest \
    -s QBTS,KULR,PLTR \
    -sd 2023-01-01 \
    -ed 2023-12-31 \
    -st MovingAverageCrossover \
    -a '{"short_window": 50, "long_window": 200}'

python main.py backtest -s "QBTS" -sd "2024-12-01" -ed "2024-12-20" -st MACDStrategy -a '{"capital": 150000}'
```
>>>>>>> b3ebafc428b983414fb9552fc810d712fda6a330
