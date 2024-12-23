-- CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Historical and real-time stock market data
CREATE TABLE IF NOT EXISTS historical_market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT
);
-- SELECT create_hypertable('historical_market_data', 'datetime');

CREATE TABLE IF NOT EXISTS real_time_market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    pe_ratio NUMERIC,
    market_cap BIGINT
);
-- SELECT create_hypertable('real_time_market_data', 'datetime');

CREATE TABLE IF NOT EXISTS yahoo_finance_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT
);

-- Trade execution logs for analysis and backtesting
CREATE TABLE IF NOT EXISTS trade_logs (
    id SERIAL PRIMARY KEY,
    strategy_name TEXT NOT NULL,     -- Name of the trading strategy
    symbol TEXT NOT NULL,            -- Stock symbol
    action TEXT NOT NULL,            -- "BUY" or "SELL"
    quantity INT NOT NULL,           -- Number of shares traded
    price_per_share DOUBLE PRECISION NOT NULL, -- Price at execution
    datetime TIMESTAMP NOT NULL,     -- Execution timestamp
    pnl DOUBLE PRECISION             -- Profit and loss (for tracking results)
);

CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(255) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_value NUMERIC NOT NULL,
    final_value NUMERIC NOT NULL,
    return_percentage NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alternative_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,        -- Source of the data (e.g., 'yfinance', 'google_trends')
    symbol VARCHAR(10) NOT NULL,        -- Stock symbol
    datetime TIMESTAMP NOT NULL,        -- Date and time of data
    metric VARCHAR(50),                 -- Metric name (e.g., 'search_volume', 'sentiment_score')
    value NUMERIC,                      -- Metric value
    details TEXT                        -- Optional extra information (e.g., JSON payload)
);

CREATE TABLE IF NOT EXISTS company_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    log_returns DOUBLE PRECISION,
    pe_ratio DOUBLE PRECISION,
    market_cap DOUBLE PRECISION,
    cluster_id INTEGER,
    regime VARCHAR(50),
    CONSTRAINT unique_symbol_datetime UNIQUE (symbol, datetime)
);

CREATE TABLE IF NOT EXISTS derived_metrics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    value NUMERIC,
    details TEXT,
    CONSTRAINT unique_metric_symbol_datetime UNIQUE (symbol, metric_name, datetime)
);
