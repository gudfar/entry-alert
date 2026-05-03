"""Alert evaluation and dispatch.

Called by the scheduler every hour. For each tracked coin:
1. Fetch current price from CoinGecko (batched).
2. For each user holding that coin, compute deviation from avg entry.
3. If abs(deviation) >= threshold AND no recent alert for that direction, send alert.
"""

import logging
from telegram import Bot
from bot import db
from bot.coingecko import fetch_prices

logger = logging.getLogger(__name__)


def _format_alert(coin: str, current_price: float, avg_entry: float, deviation_pct: float, direction: str) -> str:
    sign = f"{deviation_pct:.1f}"
    if direction == "below":
        return (
            f"📉 *{coin}* is {abs(deviation_pct):.1f}% below your avg entry of "
            f"${avg_entry:,.2f} (now ${current_price:,.2f}) — potential DCA zone."
        )
    else:
        return (
            f"📈 *{coin}* is {deviation_pct:.1f}% above your avg entry of "
            f"${avg_entry:,.2f} (now ${current_price:,.2f}) — potential take-profit zone."
        )


async def run_price_check(bot: Bot) -> None:
    """Main hourly job: evaluate alerts for all tracked coins and users."""
    coins = await db.get_all_tracked_coins()
    if not coins:
        logger.debug("No tracked coins — skipping price check")
        return

    logger.info("Price check for %d coin(s): %s", len(coins), coins)

    try:
        prices = await fetch_prices(coins)
    except Exception as exc:
        logger.error("CoinGecko fetch failed: %s", exc)
        return

    for coin in coins:
        current_price = prices.get(coin)
        if current_price is None:
            logger.warning("No price returned for %s — skipping", coin)
            continue

        users = await db.get_users_for_coin(coin)
        for chat_id in users:
            avg_entry = await db.get_avg_entry(chat_id, coin)
            if avg_entry is None or avg_entry == 0:
                continue

            deviation_pct = (current_price - avg_entry) / avg_entry * 100
            direction = "below" if deviation_pct < 0 else "above"
            threshold = await db.get_threshold(chat_id, coin)

            if abs(deviation_pct) < threshold:
                continue

            silence_hours = await db.get_silence_hours(chat_id, coin)
            if await db.was_alerted_recently(chat_id, coin, direction, silence_hours):
                logger.debug(
                    "Suppressed %s %s alert for chat_id=%d (24h dedup)", coin, direction, chat_id
                )
                continue

            text = _format_alert(coin, current_price, avg_entry, deviation_pct, direction)
            try:
                await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
                await db.record_alert(chat_id, coin, direction)
                logger.info("Alert sent: chat_id=%d coin=%s direction=%s dev=%.1f%%",
                            chat_id, coin, direction, deviation_pct)
            except Exception as exc:
                logger.error("Failed to send alert to chat_id=%d: %s", chat_id, exc)
