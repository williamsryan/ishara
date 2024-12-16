-- Historical and real-time stock market data
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT
);

-- Alternative data (e.g., QuiverQuant's congressional trades)
CREATE TABLE alternative_data (
    id SERIAL PRIMARY KEY,
    data_source TEXT NOT NULL,       -- Name of the source (e.g., "QuiverQuant")
    symbol TEXT,                     -- Stock symbol
    date TIMESTAMP,                  -- Date of the record
    key_metric TEXT NOT NULL,        -- Metric name (e.g., "Sentiment Score")
    value TEXT NOT NULL              -- Metric value (as string for flexibility)
);

-- Trade execution logs for analysis and backtesting
CREATE TABLE trade_logs (
    id SERIAL PRIMARY KEY,
    strategy_name TEXT NOT NULL,     -- Name of the trading strategy
    symbol TEXT NOT NULL,            -- Stock symbol
    action TEXT NOT NULL,            -- "BUY" or "SELL"
    quantity INT NOT NULL,           -- Number of shares traded
    price_per_share DOUBLE PRECISION NOT NULL, -- Price at execution
    datetime TIMESTAMP NOT NULL,     -- Execution timestamp
    pnl DOUBLE PRECISION             -- Profit and loss (for tracking results)
);

CREATE TABLE backtest_results (
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
