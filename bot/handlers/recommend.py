from telegram import Update
from telegram.ext import ContextTypes
from bot import db
from bot.coingecko import fetch_prices


async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args

    if not args or len(args) != 1:
        await update.message.reply_text(
            "⚠️ Usage: /recommend AMOUNT\nExample: /recommend 200"
        )
        return

    try:
        invest_amount = float(args[0])
    except ValueError:
        await update.message.reply_text("⚠️ AMOUNT must be a number.")
        return

    if invest_amount <= 0:
        await update.message.reply_text("⚠️ AMOUNT must be positive.")
        return

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
        await update.message.reply_text(
            "⚠️ Could not fetch prices right now — try again in a moment."
        )
        return

    candidates = []
    above_avg = []

    for s in stats:
        coin = s["coin"]
        avg = s["avg_entry"]
        total = s["total_amount"]
        current = prices.get(coin)
        if current is None:
            continue

        deviation_pct = (current - avg) / avg * 100
        new_avg = (avg * total + invest_amount) / (total + invest_amount / current)
        avg_change = new_avg - avg

        if deviation_pct < 0:
            position_value = total * current
            score = abs(deviation_pct) / position_value if position_value > 0 else 0
            candidates.append({
                "coin": coin,
                "avg": avg,
                "deviation_pct": deviation_pct,
                "score": score,
                "new_avg": new_avg,
                "avg_change": avg_change,
            })
        else:
            above_avg.append({
                "coin": coin,
                "avg": avg,
                "deviation_pct": deviation_pct,
                "new_avg": new_avg,
                "avg_change": avg_change,
            })

    if not candidates:
        await update.message.reply_text(
            "📈 All coins are above your avg entry — not the best time for DCA right now."
        )
        return

    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]

    lines = [f"💡 *Recommended: invest ${invest_amount:,.2f} in {best['coin']}*"]

    for c in candidates:
        sign = "+" if c["avg_change"] >= 0 else "-"
        lines.append(
            f"*{c['coin']}*  📉 {abs(c['deviation_pct']):.1f}% below avg\n"
            f"Avg entry now:  ${c['avg']:,.2f}\n"
            f"Avg entry after: ${c['new_avg']:,.2f}  ({sign}${abs(c['avg_change']):,.2f})"
        )

    if above_avg:
        lines.append("_Above avg entry (not recommended for DCA):_")
        for c in above_avg:
            sign = "+" if c["avg_change"] >= 0 else "-"
            lines.append(
                f"*{c['coin']}*  📈 {c['deviation_pct']:.1f}% above avg\n"
                f"Avg entry after: ${c['new_avg']:,.2f}  ({sign}${abs(c['avg_change']):,.2f})"
            )

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")
