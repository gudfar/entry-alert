# MEMORY

Agent memory for entry-alert. Root causes, patterns, lessons learned.

## Architecture Decisions

- alert_log PRIMARY KEY is (chat_id, coin, direction) — NOT (chat_id, coin). Reason: below/above alerts are independent events. A sharp bounce after a dip must be able to trigger an 'above' alert even within the same 24h window.
- CoinGecko uses coin IDs (bitcoin, not BTC). Always resolve symbol→id via SYMBOL_TO_ID before API calls.
- /mystats shows ALL logged coins (not just ones with alert thresholds set).

## Known Constraints

- CoinGecko free tier: ~30 req/min. Batch all active coins in a single /simple/price call per hourly cycle.
- Railway single process: no celery, no redis, no worker queues. APScheduler runs inside the same event loop as python-telegram-bot.

## Phase 2 Backlog (do not implement in MVP)

- /remove command + cascading cleanup of alert_settings and alert_log
- /deleteaccount
- Dynamic SYMBOL_TO_ID via CoinGecko /coins/list
- Behavioral analytics (FOMO detector, Discipline Score)
- Webhook mode (replace polling)
