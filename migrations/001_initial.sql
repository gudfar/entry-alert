-- entry-alert initial schema

CREATE TABLE IF NOT EXISTS users (
    chat_id BIGINT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
    coin TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    price NUMERIC NOT NULL,
    traded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS trades_chat_coin ON trades (chat_id, coin);

CREATE TABLE IF NOT EXISTS alert_settings (
    chat_id BIGINT NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
    coin TEXT NOT NULL,
    threshold_pct NUMERIC NOT NULL DEFAULT 20,
    silence_hours NUMERIC NOT NULL DEFAULT 24,
    PRIMARY KEY (chat_id, coin)
);

-- Add silence_hours to existing deployments that ran the original migration
ALTER TABLE alert_settings ADD COLUMN IF NOT EXISTS silence_hours NUMERIC NOT NULL DEFAULT 24;

-- direction tracked independently: 'below' and 'above' are separate rows
CREATE TABLE IF NOT EXISTS alert_log (
    chat_id BIGINT NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
    coin TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('below', 'above')),
    alerted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (chat_id, coin, direction)
);
