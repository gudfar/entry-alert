from decimal import Decimal, InvalidOperation
from telegram import Update
from telegram.ext import ContextTypes
from bot import db
from bot.coingecko import SYMBOL_TO_ID


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args

    if not args or len(args) != 3:
        await update.message.reply_text(
            "⚠️ Usage: /add COIN AMOUNT PRICE\nExample: /add BTC 0.5 45000"
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
        amount = Decimal(args[1])
        price = Decimal(args[2])
    except InvalidOperation:
        await update.message.reply_text("⚠️ AMOUNT and PRICE must be numbers.")
        return

    if amount <= 0 or price <= 0:
        await update.message.reply_text("⚠️ AMOUNT and PRICE must be positive.")
        return

    await db.upsert_user(chat_id)
    await db.log_trade(chat_id, coin, amount, price)

    avg = await db.get_avg_entry(chat_id, coin)
    await update.message.reply_text(
        f"✅ Trade logged: {amount} {coin} at ${price:,.2f}\n"
        f"📊 Your new avg entry for {coin}: ${avg:,.2f}"
    )
