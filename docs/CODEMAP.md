# CODEMAP

Code map for the entry-alert project.

## Directory Structure

```
entry-alert/
├── bot/
│   ├── __init__.py
│   ├── __main__.py       # entrypoint: wire Application + AsyncIOScheduler, run polling
│   ├── handlers/
│   │   ├── start.py      # /start — register user
│   │   ├── add.py        # /add COIN AMOUNT PRICE — log trade
│   │   ├── mystats.py    # /mystats — show avg entry + deviation
│   │   ├── setalert.py   # /setalert COIN PCT — set threshold
│   │   └── help.py       # /help — command reference
│   ├── scheduler.py      # APScheduler setup, price_check job definition
│   ├── coingecko.py      # CoinGecko HTTP client, batch price fetcher
│   ├── db.py             # asyncpg pool init, query helpers
│   └── alerts.py         # deviation calc, alert evaluation, dispatch + dedup
├── migrations/
│   └── 001_initial.sql   # full schema: users, trades, alert_settings, alert_log
├── docs/                 # Rosetta documentation
├── agents/               # Rosetta agent files
├── tests/
│   ├── test_alerts.py
│   ├── test_handlers.py
│   └── test_coingecko.py
├── Procfile              # web: python -m bot
├── requirements.txt
├── .env.example
└── README.md
```

## Key Entry Points

| File | Role |
|------|------|
| `bot/__main__.py` | Process entry point |
| `bot/db.py` | DB pool, shared across all modules |
| `bot/alerts.py` | Core business logic |
| `bot/scheduler.py` | Hourly job wiring |
| `migrations/001_initial.sql` | Authoritative schema |
