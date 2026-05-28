from telegram import Update
from telegram.ext import ContextTypes
from bot import db
from bot.coingecko import fetch_prices


async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    stats = await db.get_mystats(chat_id)

    if not stats:
        await update.message.reply_text(
            "📭 No trades logged yet. Use /add COIN AMOUNT PRICE to get started."
        )
        return

    coins = [s["coin"] for s in stats]
    try:
        prices = await fetch_prices(coins)
    except Exception:
        prices = {}

    lines = ["📊 *Your portfolio stats:*"]
    total_pnl = 0.0
    has_prices = False

    for s in stats:
        coin = s["coin"]
        avg = s["avg_entry"]
        total = s["total_amount"]
        line = f"*{coin}*: avg entry ${avg:,.2f} ({total:g} held)"

        current = prices.get(coin)
        if current:
            deviation = (current - avg) / avg * 100
            sign = "+" if deviation >= 0 else ""
            arrow = "📈" if deviation >= 0 else "📉"
            line += f"\n{arrow} Current: ${current:,.2f} ({sign}{deviation:.1f}% from avg)"
            total_pnl += (current - avg) * total
            has_prices = True

        lines.append(line)

    if has_prices:
        pnl_sign = "+" if total_pnl >= 0 else "-"
        lines.append(f"💰 *Total unrealized PnL: {pnl_sign}${abs(total_pnl):,.2f}*")

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")
