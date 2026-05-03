# CONTEXT

entry-alert is a Telegram bot that alerts crypto DCA investors when the current market price deviates significantly from their personal average entry (cost basis). It is not a generic market alert tool — every alert is relative to the user's own logged trades.

## Target Users

Solo crypto investors who dollar-cost average (DCA) into Bitcoin and other coins and want to be notified when the market moves meaningfully relative to their personal cost basis — signalling a potential DCA opportunity or a significant profit zone.

## Core Value Proposition

"BTC is 20% below your avg entry of $45,000 — potential DCA zone."

The alert is personal, actionable, and noise-free (max 1 alert per coin per 24 hours).

## MVP Scope

- Telegram bot interface (commands only, no web UI)
- Manual trade logging via /add command
- Personal stats via /mystats
- Custom alert thresholds via /setalert
- Hourly price check via CoinGecko free tier
- Alert when price is X% below or above personal average entry
- PostgreSQL persistence on Railway
- Single-process deployment on Railway

## Out of Scope (MVP)

- Web UI or dashboard
- Exchange API integrations (auto trade import)
- Portfolio performance tracking / PnL calculations
- Multi-currency fiat support
- Push notifications outside Telegram
- Compliance, KYC, or auth beyond Telegram chat_id
- Behavioral analytics (FOMO detector, Discipline Score, etc.) — Phase 2
