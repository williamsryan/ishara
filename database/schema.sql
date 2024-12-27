-- Connect to the default 'postgres' database first
\c postgres;

-- Terminate all active connections to the target database
DO $$ BEGIN
    PERFORM pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = 'ishara' AND pid <> pg_backend_pid();
END $$;

-- Drop the database if it exists
DROP DATABASE IF EXISTS ishara;

-- Create the database
CREATE DATABASE ishara;

-- Connect to the new database
\c ishara;

-- Table for historical market data (e.g., OHLC data)
CREATE TABLE IF NOT EXISTS historical_market_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    UNIQUE(symbol, datetime)
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    analysis_type TEXT NOT NULL,  -- E.g., 'clustering', 'regime_detection'
    cluster_id INTEGER,           -- Nullable for other analyses
    result JSONB,                 -- To store additional analysis data in a flexible format
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enhanced Table for Yahoo Finance data
CREATE TABLE IF NOT EXISTS yahoo_finance_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    dividends NUMERIC,
    target_est NUMERIC,               -- 1y Target Estimate
    beta NUMERIC,                     -- Beta (5Y Monthly)
    eps NUMERIC,                      -- Earnings per share (TTM)
    earnings_date TEXT,               -- Earnings Date (parsed as a range string)
    ex_dividend_date TEXT,            -- Ex-Dividend Date
    forward_div_yield TEXT,           -- Forward Dividend & Yield (parsed as string)
    pe_ratio NUMERIC,                 -- Price-to-Earnings Ratio (TTM)
    market_cap NUMERIC,               -- Market Cap (converted to numeric)
    UNIQUE(symbol, datetime)
);

CREATE TABLE IF NOT EXISTS options_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    expiration_date DATE NOT NULL,
    option_type TEXT NOT NULL CHECK (option_type IN ('call', 'put')),
    strike NUMERIC,
    last_price NUMERIC,
    bid NUMERIC,
    ask NUMERIC,
    change NUMERIC,
    percent_change NUMERIC,
    volume BIGINT,
    open_interest BIGINT,
    implied_volatility NUMERIC,
    UNIQUE(symbol, expiration_date, option_type, strike)
);

-- Table for real-time market data
CREATE TABLE IF NOT EXISTS real_time_market_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    price NUMERIC,
    UNIQUE(symbol, datetime)
);

-- Table for alternative data (e.g., sentiment, trends)
CREATE TABLE IF NOT EXISTS alternative_data (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    symbol TEXT NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    metric TEXT NOT NULL,
    value NUMERIC,
    details TEXT,
    UNIQUE(symbol, datetime, metric)
);

-- Create the new derived_metrics table with additional fields
CREATE TABLE IF NOT EXISTS derived_metrics (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    log_returns NUMERIC,               -- Logarithmic returns
    pe_ratio NUMERIC,                  -- Price-to-earnings ratio
    market_cap NUMERIC,                -- Market capitalization
    moving_avg_50 NUMERIC,             -- 50-day moving average
    moving_avg_200 NUMERIC,            -- 200-day moving average
    rsi NUMERIC,                       -- Relative Strength Index
    macd NUMERIC,                      -- Moving Average Convergence Divergence
    UNIQUE(symbol, datetime)
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_historical_market_data ON historical_market_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_yahoo_finance_data ON yahoo_finance_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_real_time_market_data ON real_time_market_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_alternative_data ON alternative_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_derived_metrics ON derived_metrics (symbol, datetime DESC);
