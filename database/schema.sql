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

-- Table for Yahoo Finance data
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
    earnings NUMERIC
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

-- Table for derived metrics (e.g., technical indicators)
CREATE TABLE IF NOT EXISTS derived_metrics (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    log_returns NUMERIC,
    pe_ratio NUMERIC,
    market_cap NUMERIC,
    UNIQUE(symbol, datetime)
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_historical_market_data ON historical_market_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_yahoo_finance_data ON yahoo_finance_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_real_time_market_data ON real_time_market_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_alternative_data ON alternative_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_derived_metrics ON derived_metrics (symbol, datetime DESC);
