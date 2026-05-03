# IMPLEMENTATION

Current implementation state of entry-alert.

## Status: MVP Complete

Full bot implemented, running locally. All source files created and verified.

## Completed

- [x] Rosetta workspace initialization
- [x] CONTEXT.md, ARCHITECTURE.md, TECHSTACK.md, CODEMAP.md, DEPENDENCIES.md
- [x] ASSUMPTIONS.md, MEMORY.md, PATTERNS/
- [x] Project scaffolding: requirements.txt, Procfile, .env.example, .gitignore
- [x] migrations/001_initial.sql — full schema with indexes + ALTER TABLE for silence_hours
- [x] bot/db.py — asyncpg pool, migrations runner, all query helpers
- [x] bot/coingecko.py — batch price fetch, SYMBOL_TO_ID (20 coins)
- [x] bot/handlers/start.py — /start, upsert user
- [x] bot/handlers/add.py — /add COIN AMOUNT PRICE, Decimal parsing, validation
- [x] bot/handlers/mystats.py — /mystats with live deviation, 📈/📉 arrows
- [x] bot/handlers/setalert.py — /setalert COIN PCT [SILENCE_HOURS]
- [x] bot/handlers/help.py — /help, clean formatting
- [x] bot/alerts.py — deviation calc, per-user silence window, alert dispatch
- [x] bot/scheduler.py — APScheduler, configurable interval
- [x] bot/__main__.py — entrypoint, wires app + scheduler, graceful shutdown
- [x] README.md

## Key Implementation Details

- `Decimal` used for AMOUNT and PRICE in /add (not float) — avoids floating point precision issues
- `silence_hours` is per-user per-coin — stored in alert_settings, defaults to 24h
- `/setalert BTC 20` → threshold 20%, silence 24h; `/setalert BTC 20 12` → silence 12h
- Migrations run automatically on boot via `_run_migrations()` — `ADD COLUMN IF NOT EXISTS` handles existing deployments
- CoinGecko free tier: batch all coins in single /simple/price call per cycle
- Graceful shutdown via SIGINT/SIGTERM signal handlers

## Next Up

- [ ] tests/ — unit tests for deviation logic, handler validation, db helpers

## Change Log

### 2026-05-03
- Workspace initialized via Rosetta init-workspace-flow
- Architecture designed: single-process, asyncpg, APScheduler, polling mode
- alert_log PRIMARY KEY: (chat_id, coin, direction) — below/above tracked independently

### 2026-05-04
- Full MVP implementation: all source files created
- Emojis added to all bot messages
- AMOUNT/PRICE parsing switched from float to Decimal
- silence_hours column added to alert_settings (configurable per coin)
- /setalert updated to accept optional SILENCE_HOURS argument
- was_alerted_recently() uses per-user silence_hours instead of hardcoded 24h
- README.md created
- deps: asyncpg bumped to 0.30.0
