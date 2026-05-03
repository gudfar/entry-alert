# ASSUMPTIONS

Assumptions and open questions for entry-alert.

## Confirmed by User

- chat_id is the sole user identifier; no auth layer needed for MVP
- No PII stored beyond chat_id, coin symbols, amounts, prices
- CoinGecko free tier is sufficient for MVP (batch all coins in one /simple/price call per hour)
- Polling mode (not webhook) for MVP on Railway
- Single Railway process + managed Postgres; no horizontal scaling
- Alert threshold is symmetric: same % applies to both below and above
- alert_log dedup is per (chat_id, coin, direction) — below and above are independent
- /mystats shows ALL logged coins, not only ones with active alerts
- No /deleteaccount command for MVP
- If all trades for a coin are deleted: reset alert_settings + alert_log for that coin. Phase 2 concern (no /remove in MVP).
- CoinGecko requires coin IDs (bitcoin, ethereum), not symbols (BTC, ETH). MVP uses a hardcoded SYMBOL_TO_ID dict in coingecko.py. Phase 2: fetch dynamically from /coins/list.

## Assumptions (AI-inferred, not explicitly confirmed)

| # | Assumption | Impact if wrong |
|---|-----------|----------------|
| A1 | Default alert threshold is 20% | Change constant in setalert default |
| A2 | Coin symbols normalized to uppercase on input (btc → BTC) | Input validation in /add and /setalert |
| A5 | Price check runs every 60 minutes, no time-of-day restriction | Fine for crypto (24/7 markets) |
| A6 | Prices returned and stored in USD only | Hard-coded USD for MVP |
| A7 | Railway free tier resources sufficient for single-process + Postgres | May need paid tier for reliability |

## SYMBOL_TO_ID Mapping (MVP hardcoded)

Defined in `bot/coingecko.py`. Expand as needed.

```python
SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "DOGE": "dogecoin",
    "ATOM": "cosmos",
    "UNI": "uniswap",
    "TON": "the-open-network",
}
```

Phase 2: replace with dynamic lookup via CoinGecko `/coins/list` endpoint.
