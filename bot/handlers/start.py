from telegram import Update
from telegram.ext import ContextTypes
from bot import db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await db.upsert_user(chat_id)
    await update.message.reply_text(
        "👋 Welcome to *entry-alert*!\n\n"
        "📊 I notify you when the market moves significantly relative to your personal average entry price.\n\n"
        "Get started:\n"
        "  📝 /add BTC 0.5 45000 — log a trade\n"
        "  📈 /mystats — see your avg entries\n"
        "  🔔 /setalert BTC 20 — alert when price is 20% off your avg\n"
        "  ❓ /help — full command reference",
        parse_mode="Markdown",
    )
