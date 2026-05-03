# ARCHITECTURE

## System Overview

Single Python process running on Railway. Two concurrent concerns:
1. Telegram bot — command handler (event-driven, async)
2. Price checker — scheduled job (hourly, APScheduler)

Both share a single asyncpg connection pool and communicate with the same PostgreSQL database.

## Components

### Telegram Bot (python-telegram-bot)
- Handles commands: /start, /add, /mystats, /setalert, /help
- Uses Application + async handlers
- Runs in polling mode (no webhook for MVP)

### Price Checker (APScheduler)
- AsyncIOScheduler, interval trigger: every 60 minutes
- Fetches current prices from CoinGecko for all coins tracked by any user
- Computes deviation = (current_price - avg_entry) / avg_entry * 100
- Compares against each user's threshold (default: 20%)
- Fires Telegram alert if threshold crossed AND no alert sent for that (coin, direction) in last 24h
- Logs alert to alert_log to enforce per-direction 24h dedup

### CoinGecko API Client
- Free tier, unauthenticated
- Endpoint: /simple/price
- Batch coins per request to minimize calls
- Rate limit: ~30 req/min; batch all coins in one call per cycle

### Database (asyncpg + PostgreSQL on Railway)
- Single connection pool shared across bot and scheduler
- Schema: see Database Schema section

### Deployment (Railway)
- Single Procfile process: `python -m bot`
- Managed Postgres add-on
- Env vars: TELEGRAM_TOKEN, DATABASE_URL, (optional) COINGECKO_API_KEY

## Database Schema

```sql
-- Users registered via /start
CREATE TABLE users (
    chat_id BIGINT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Manually logged trades
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT REFERENCES users(chat_id),
    coin TEXT NOT NULL,           -- e.g. "BTC"
    amount NUMERIC NOT NULL,      -- quantity bought
    price NUMERIC NOT NULL,       -- price per unit at time of purchase
    traded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Per-user, per-coin alert thresholds
CREATE TABLE alert_settings (
    chat_id BIGINT REFERENCES users(chat_id),
    coin TEXT NOT NULL,
    threshold_pct NUMERIC NOT NULL DEFAULT 20,
    PRIMARY KEY (chat_id, coin)
);

-- Alert deduplication log (max 1 alert per coin per direction per 24h)
-- direction tracked independently: a 'below' alert does NOT suppress 'above'
CREATE TABLE alert_log (
    chat_id BIGINT REFERENCES users(chat_id),
    coin TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('below', 'above')),
    alerted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (chat_id, coin, direction)
);
```

## Average Entry Calculation

```
avg_entry(chat_id, coin) = SUM(amount * price) / SUM(amount)
```

Weighted average — accounts for different buy sizes.

## Alert Logic

```
deviation_pct = (current_price - avg_entry) / avg_entry * 100
direction = 'below' if deviation_pct < 0 else 'above'

if abs(deviation_pct) >= threshold_pct:
    if no alert_log entry for (chat_id, coin, direction) within last 24h:
        send alert
        upsert alert_log(chat_id, coin, direction, alerted_at=now)
```

`below` and `above` are tracked independently — a sharp bounce can trigger an `above` alert
even if a `below` alert was already sent within the same 24h window.

Alert message format:
- Below: "BTC is 20.3% below your avg entry of $45,000 — potential DCA zone."
- Above: "BTC is 22.1% above your avg entry of $45,000 — potential take-profit zone."

## Bot Commands

| Command | Args | Description |
|---------|------|-------------|
| /start | — | Register user, show welcome |
| /add | COIN AMOUNT PRICE | Log a trade (e.g. /add BTC 0.5 45000) |
| /mystats | — | Show avg entry + current deviation per coin |
| /setalert | COIN THRESHOLD_PCT | Set alert threshold (e.g. /setalert BTC 20) |
| /help | — | Show command reference |

## Non-Functional Requirements

- Single process, no horizontal scaling for MVP
- Graceful shutdown: drain in-flight handlers before exit
- CoinGecko free tier: batch all coins in one API call per hourly cycle
- No user PII stored; chat_id is the only identifier
- Alert dedup enforced at DB level (upsert on primary key per direction)

## Project Structure (planned)

```
entry-alert/
├── bot/
│   ├── __init__.py
│   ├── __main__.py       # entrypoint, wires app + scheduler
│   ├── handlers/
│   │   ├── start.py
│   │   ├── add.py
│   │   ├── mystats.py
│   │   ├── setalert.py
│   │   └── help.py
│   ├── scheduler.py      # APScheduler setup + price check job
│   ├── coingecko.py      # CoinGecko API client
│   ├── db.py             # asyncpg pool + query helpers
│   └── alerts.py         # alert evaluation + dispatch logic
├── migrations/
│   └── 001_initial.sql
├── docs/
├── agents/
├── tests/
├── Procfile
├── requirements.txt
└── .env.example
```
