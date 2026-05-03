# 🔔 Entry Alert

Telegram bot that alerts crypto DCA investors when the market price deviates significantly from their personal average entry (cost basis).

> "BTC is 20% below your avg entry of $45,000 — potential DCA zone."

## Features

- Log trades manually via `/add`
- View your weighted average entry and live deviation via `/mystats`
- Configurable alert threshold and silence window per coin via `/setalert`
- Hourly price checks via CoinGecko free tier (batched, no API key required)
- Alerts fire independently for `below` and `above` directions
- PostgreSQL persistence — no alert spam (per-direction silence window)

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and show welcome |
| `/add BTC 0.5 45000` | Log a trade: coin, amount, price |
| `/mystats` | Show avg entry + live deviation per coin |
| `/setalert BTC 20` | Alert when BTC moves 20% from your avg (24h silence) |
| `/setalert BTC 20 12` | Same, but re-alert after 12h |
| `/help` | Show command reference |

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database (local or [Railway](https://railway.app))
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Local development

```bash
git clone https://github.com/yourname/entry-alert
cd entry-alert

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in TELEGRAM_TOKEN and DATABASE_URL

python -m bot
```

The bot runs migrations automatically on first boot — no manual SQL step needed.

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | Yes | Bot token from @BotFather |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `COINGECKO_API_KEY` | No | CoinGecko Pro key (free tier works without it) |

### Local PostgreSQL with Docker

```bash
docker run -d \
  -e POSTGRES_PASSWORD=pass \
  -p 5432:5432 \
  postgres:16

# DATABASE_URL=postgresql://postgres:pass@localhost:5432/postgres
```

## Deployment (Railway)

1. Create a new project on [Railway](https://railway.app)
2. Add a **PostgreSQL** plugin
3. Connect your repo — Railway will detect the `Procfile` automatically
4. Set environment variables: `TELEGRAM_TOKEN`, `DATABASE_URL` (copy from Railway Postgres plugin)

## Architecture

Single Python process — no Redis, no Celery, no webhooks.

```
Telegram polling (python-telegram-bot)
        │
        ▼
   Command handlers  ──►  asyncpg pool  ──►  PostgreSQL
        │
APScheduler (hourly)
        │
        ▼
  CoinGecko /simple/price  (batch, all coins in one request)
        │
        ▼
  Deviation check per user  ──►  alert_log dedup  ──►  Telegram alert
```

**Average entry** is the weighted average across all logged trades:
```
avg_entry = SUM(amount × price) / SUM(amount)
```

**Alert dedup** is enforced at the DB level — `above` and `below` directions are tracked independently, so a sharp bounce can trigger both within the same silence window.

## Supported coins

BTC, ETH, SOL, BNB, ADA, XRP, DOGE, DOT, AVAX, MATIC, LINK, UNI, LTC, ATOM, TRX, NEAR, APT, ARB, OP, SUI

## Project structure

```
entry-alert/
├── bot/
│   ├── __main__.py        # entrypoint, wires app + scheduler
│   ├── db.py              # asyncpg pool + query helpers
│   ├── coingecko.py       # CoinGecko API client
│   ├── alerts.py          # deviation calc + alert dispatch
│   ├── scheduler.py       # APScheduler setup
│   └── handlers/
│       ├── start.py
│       ├── add.py
│       ├── mystats.py
│       ├── setalert.py
│       └── help.py
├── migrations/
│   └── 001_initial.sql
├── Procfile
├── requirements.txt
└── .env.example
```
