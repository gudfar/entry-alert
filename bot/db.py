"""asyncpg connection pool and all query helpers."""

import asyncpg
import os
from pathlib import Path
from typing import Optional


_pool: Optional[asyncpg.Pool] = None


async def init_pool() -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(dsn=os.environ["DATABASE_URL"], min_size=2, max_size=10)
    await _run_migrations(_pool)
    return _pool


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialised — call init_pool() first")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def _run_migrations(pool: asyncpg.Pool) -> None:
    sql = (Path(__file__).parent.parent / "migrations" / "001_initial.sql").read_text()
    async with pool.acquire() as conn:
        await conn.execute(sql)


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

async def upsert_user(chat_id: int) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO users (chat_id) VALUES ($1) ON CONFLICT DO NOTHING",
        chat_id,
    )


# ---------------------------------------------------------------------------
# Trade helpers
# ---------------------------------------------------------------------------

async def log_trade(chat_id: int, coin: str, amount: float, price: float) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO trades (chat_id, coin, amount, price) VALUES ($1, $2, $3, $4)",
        chat_id, coin, amount, price,
    )


async def get_avg_entry(chat_id: int, coin: str) -> Optional[float]:
    """Weighted average: SUM(amount*price)/SUM(amount). Returns None if no trades."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT SUM(amount * price) / NULLIF(SUM(amount), 0) AS avg_entry
        FROM trades
        WHERE chat_id = $1 AND coin = $2
        """,
        chat_id, coin,
    )
    return float(row["avg_entry"]) if row and row["avg_entry"] is not None else None


async def get_all_user_coins(chat_id: int) -> list[str]:
    """Distinct coins traded by this user."""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT DISTINCT coin FROM trades WHERE chat_id = $1 ORDER BY coin",
        chat_id,
    )
    return [r["coin"] for r in rows]


async def get_mystats(chat_id: int) -> list[dict]:
    """Returns list of {coin, avg_entry, total_amount} for all user coins."""
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT coin,
               SUM(amount * price) / NULLIF(SUM(amount), 0) AS avg_entry,
               SUM(amount) AS total_amount
        FROM trades
        WHERE chat_id = $1
        GROUP BY coin
        ORDER BY coin
        """,
        chat_id,
    )
    return [
        {
            "coin": r["coin"],
            "avg_entry": float(r["avg_entry"]),
            "total_amount": float(r["total_amount"]),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Alert settings helpers
# ---------------------------------------------------------------------------

async def get_threshold(chat_id: int, coin: str) -> float:
    """Returns alert threshold % for (chat_id, coin). Defaults to 20."""
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT threshold_pct FROM alert_settings WHERE chat_id = $1 AND coin = $2",
        chat_id, coin,
    )
    return float(row["threshold_pct"]) if row else 20.0


async def get_silence_hours(chat_id: int, coin: str) -> float:
    """Returns silence window in hours for (chat_id, coin). Defaults to 24."""
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT silence_hours FROM alert_settings WHERE chat_id = $1 AND coin = $2",
        chat_id, coin,
    )
    return float(row["silence_hours"]) if row else 24.0


async def set_threshold(chat_id: int, coin: str, threshold_pct: float, silence_hours: float = 24.0) -> None:
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO alert_settings (chat_id, coin, threshold_pct, silence_hours)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (chat_id, coin) DO UPDATE
            SET threshold_pct = EXCLUDED.threshold_pct,
                silence_hours = EXCLUDED.silence_hours
        """,
        chat_id, coin, threshold_pct, silence_hours,
    )


# ---------------------------------------------------------------------------
# Alert log helpers
# ---------------------------------------------------------------------------

async def was_alerted_recently(chat_id: int, coin: str, direction: str, silence_hours: float) -> bool:
    """True if an alert for this (chat_id, coin, direction) was sent within the silence window."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT 1 FROM alert_log
        WHERE chat_id = $1 AND coin = $2 AND direction = $3
          AND alerted_at > NOW() - ($4 * INTERVAL '1 hour')
        """,
        chat_id, coin, direction, silence_hours,
    )
    return row is not None


async def record_alert(chat_id: int, coin: str, direction: str) -> None:
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO alert_log (chat_id, coin, direction, alerted_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (chat_id, coin, direction) DO UPDATE SET alerted_at = NOW()
        """,
        chat_id, coin, direction,
    )


# ---------------------------------------------------------------------------
# Scheduler helpers
# ---------------------------------------------------------------------------

async def get_all_tracked_coins() -> list[str]:
    """All distinct coins tracked by any user (for batch price fetch)."""
    pool = await get_pool()
    rows = await pool.fetch("SELECT DISTINCT coin FROM trades ORDER BY coin")
    return [r["coin"] for r in rows]


async def get_users_for_coin(coin: str) -> list[int]:
    """All chat_ids that have trades for this coin."""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT DISTINCT chat_id FROM trades WHERE coin = $1",
        coin,
    )
    return [r["chat_id"] for r in rows]
