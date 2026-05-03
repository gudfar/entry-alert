# TECHSTACK

Tech stack for the entry-alert project.

## Language

- Python 3.11+

## Core Libraries

| Library | Role |
|---------|------|
| python-telegram-bot | Telegram Bot API client (async) |
| asyncpg | PostgreSQL async driver |
| APScheduler | Hourly price check scheduler (AsyncIOScheduler) |
| httpx or aiohttp | HTTP client for CoinGecko API |

## External Services

| Service | Role |
|---------|------|
| Telegram Bot API | User interface |
| CoinGecko API (free tier) | Crypto price data |
| PostgreSQL (Railway managed) | Persistence |

## Infrastructure

- Deployment: Railway
- Process: single Python process (polling mode)
- Database: Railway managed Postgres

## Dev / Tooling

- python-dotenv — local env var loading
- pytest + pytest-asyncio — testing
- ruff — linting and formatting
