# MEMORY

Agent memory for entry-alert. Root causes, patterns, lessons learned.

## Architecture Decisions

- alert_log PRIMARY KEY is (chat_id, coin, direction) — NOT (chat_id, coin). Reason: below/above alerts are independent events. A sharp bounce after a dip must be able to trigger an 'above' alert even within the same 24h window.
- CoinGecko uses coin IDs (bitcoin, not BTC). Always resolve symbol→id via SYMBOL_TO_ID before API calls.
- /mystats shows ALL logged coins (not just ones with alert thresholds set).
- silence_hours is stored in alert_settings alongside threshold_pct. Default 24h. Passed explicitly to was_alerted_recently() — never hardcoded.
- Decimal (not float) used for AMOUNT and PRICE throughout — avoids floating point precision issues with trade values.

## /recommend Scoring Logic

score = abs(deviation_pct) / position_value_usd

Rationale: prioritises coins that are underweighted in the portfolio AND have a large drawdown.
A coin with a small position gets higher score than a large position with the same drawdown —
$200 invested in a $300 position has more relative impact than in a $5,000 position.
Only below-avg coins are candidates. Above-avg coins shown separately without recommendation.

## DB Migration Pattern

- Migrations run automatically on boot via _run_migrations() reading 001_initial.sql.
- Schema uses CREATE TABLE IF NOT EXISTS — idempotent on fresh boot.
- For additive changes to existing tables, use ALTER TABLE ... ADD COLUMN IF NOT EXISTS in the same migration file — handles both fresh and existing deployments.

## Known Constraints

- CoinGecko free tier: 5-15 req/min (unstable). Demo plan (free): stable 30 req/min. Set COINGECKO_API_KEY env var.
- Railway single process: no celery, no redis, no worker queues. APScheduler runs inside the same event loop as python-telegram-bot.
- Single asyncio event loop, 1 OS thread. All I/O is async (asyncpg, httpx, PTB). No blocking calls in handlers.
- Decimal input format: dot separator only. Comma causes InvalidOperation. Any number of decimal places accepted.

## Phase 2 Backlog (do not implement unless asked)

- /remove command + cascading cleanup of alert_settings and alert_log
- /deleteaccount (GDPR requirement before public launch)
- Binance API integration — auto-import trades via /connect binance
- Dynamic SYMBOL_TO_ID via CoinGecko /coins/list
- Behavioral analytics: FOMO detector, Discipline Score, What-if engine, Entry quality score
- Webhook mode (replace polling)
- Web interface
