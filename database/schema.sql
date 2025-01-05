-- Connect to the default 'postgres' database first
-- \c postgres;

-- -- Terminate all active connections to the target database
-- DO $$ BEGIN
--     PERFORM pg_terminate_backend(pg_stat_activity.pid)
--     FROM pg_stat_activity
--     WHERE pg_stat_activity.datname = 'ishara' AND pid <> pg_backend_pid();
-- END $$;

-- Drop the database if it exists
-- DROP DATABASE IF EXISTS ishara;

-- Create the database
-- CREATE DATABASE ishara;

-- Connect to the new database
-- \c ishara;

CREATE TABLE IF NOT EXISTS symbols (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,  -- Stock ticker symbol
    name TEXT NOT NULL,           -- Company name
    sector TEXT,                  -- Sector/Industry
    exchange TEXT,                -- Exchange (e.g., NASDAQ, NYSE)
    created_at TIMESTAMP DEFAULT NOW()
);

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
    analysis_id TEXT UNIQUE,      -- Unique identifier for the analysis
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trade_logs (
    id SERIAL PRIMARY KEY,
    strategy TEXT NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price FLOAT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    pnl FLOAT NOT NULL
);

-- Table for Yahoo Finance data (historical and metrics)
CREATE TABLE IF NOT EXISTS yahoo_finance_data (
    id SERIAL PRIMARY KEY,                  -- Unique identifier for each record
    symbol TEXT NOT NULL,                   -- Stock ticker symbol (e.g., AAPL, MSFT)
    datetime TIMESTAMPTZ NOT NULL,          -- Datetime of the record
    open NUMERIC,                           -- Opening price
    high NUMERIC,                           -- Highest price
    low NUMERIC,                            -- Lowest price
    close NUMERIC,                          -- Closing price
    volume BIGINT,                          -- Volume of shares traded
    dividends NUMERIC,                      -- Dividends paid on this date (if available)
    splits NUMERIC,                         -- Stock splits (e.g., 2.0 for a 2-for-1 split)
    target_est NUMERIC,                     -- 1-year target estimate
    beta NUMERIC,                           -- Beta (5Y monthly)
    eps NUMERIC,                            -- Earnings per share (TTM)
    earnings_date TIMESTAMPTZ,              -- Earnings date (parsed to a single timestamp)
    ex_dividend_date TIMESTAMPTZ,           -- Ex-dividend date (parsed to a single timestamp)
    forward_div_yield NUMERIC,              -- Forward dividend yield (as a percentage)
    pe_ratio NUMERIC,                       -- Price-to-earnings ratio (TTM)
    market_cap NUMERIC,                     -- Market capitalization (in dollars)
    UNIQUE(symbol, datetime)                -- Ensure no duplicate records for the same symbol and datetime
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

-- Table for backtest results
CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,                       -- Unique identifier for each backtest result
    strategy_name TEXT NOT NULL,                 -- Name of the strategy used in the backtest
    symbol TEXT NOT NULL,                        -- Stock symbol being backtested
    start_date TIMESTAMPTZ NOT NULL,             -- Start date of the backtest
    end_date TIMESTAMPTZ NOT NULL,               -- End date of the backtest
    initial_value NUMERIC NOT NULL,              -- Initial value of the portfolio
    final_value NUMERIC NOT NULL,                -- Final value of the portfolio
    return_percentage NUMERIC NOT NULL,          -- Percentage return over the backtest period
    details JSONB,                               -- Additional details about the backtest
    created_at TIMESTAMP DEFAULT NOW()           -- Timestamp of when the result was added
);

CREATE TABLE IF NOT EXISTS symbol_labels (
    id SERIAL PRIMARY KEY, -- Unique identifier for each label entry
    symbol TEXT NOT NULL,  -- Symbol for the stock or entity being labeled
    label TEXT NOT NULL,   -- User-defined label
    created_at TIMESTAMP DEFAULT NOW(), -- Timestamp of when the label was created
    UNIQUE(symbol, label) -- Ensure unique symbol-label combinations
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_historical_market_data ON historical_market_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_yahoo_finance_data ON yahoo_finance_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_real_time_market_data ON real_time_market_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_alternative_data ON alternative_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_derived_metrics ON derived_metrics (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_backtest_results ON backtest_results (strategy_name, symbol, created_at DESC);
