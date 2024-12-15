CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    datetime TIMESTAMP,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT
);

CREATE TABLE congressional_trades (
    id SERIAL PRIMARY KEY,
    representative TEXT,
    ticker TEXT,
    date TIMESTAMP,
    transaction TEXT,
    amount TEXT
);