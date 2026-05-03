from telegram import Update
from telegram.ext import ContextTypes
from bot import db
from bot.coingecko import SYMBOL_TO_ID


async def setalert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args

    if not args or len(args) not in (2, 3):
        await update.message.reply_text(
            "⚠️ Usage: /setalert COIN THRESHOLD_% [SILENCE_HOURS]\n"
            "Example: /setalert BTC 20\n"
            "Example: /setalert BTC 20 12"
        )
        return

    coin = args[0].upper()
    if coin not in SYMBOL_TO_ID:
        known = ", ".join(sorted(SYMBOL_TO_ID.keys()))
        await update.message.reply_text(
            f"❌ Unknown coin: {coin}\nSupported coins: {known}"
        )
        return

    try:
        threshold = float(args[1])
    except ValueError:
        await update.message.reply_text("⚠️ THRESHOLD_% must be a number.")
        return

    if threshold <= 0 or threshold > 100:
        await update.message.reply_text("⚠️ Threshold must be between 0 and 100.")
        return

    silence_hours = 24.0
    if len(args) == 3:
        try:
            silence_hours = float(args[2])
        except ValueError:
            await update.message.reply_text("⚠️ SILENCE_HOURS must be a number.")
            return
        if silence_hours <= 0:
            await update.message.reply_text("⚠️ SILENCE_HOURS must be positive.")
            return

    await db.upsert_user(chat_id)
    await db.set_threshold(chat_id, coin, threshold, silence_hours)
    await update.message.reply_text(
        f"🔔 Alert set: I'll notify you when {coin} moves {threshold:g}% from your avg entry "
        f"(silence window: {silence_hours:g}h)."
    )
