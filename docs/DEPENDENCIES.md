# DEPENDENCIES

Dependencies for the entry-alert project.

## Python (requirements.txt)

```
python-telegram-bot[job-queue]>=21.0
asyncpg>=0.29
APScheduler>=3.10
httpx>=0.27
python-dotenv>=1.0
```

## Dev Dependencies

```
pytest>=8.0
pytest-asyncio>=0.23
ruff>=0.4
```

## External APIs

| API | Auth | Tier |
|-----|------|------|
| CoinGecko /simple/price | None (free tier) | 30 req/min |
| Telegram Bot API | TELEGRAM_TOKEN env var | Free |

## Infrastructure

| Service | Plan |
|---------|------|
| Railway app | Hobby / free tier |
| Railway Postgres | Managed, shared |
