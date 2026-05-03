from telegram import Update
from telegram.ext import ContextTypes


HELP_TEXT = (
    "📖 *entry-alert commands:*\n\n"
    "👋 /start — Register and show welcome\n"
    "📝 /add COIN AMOUNT PRICE — Log a trade\n"
    "  e.g. `/add BTC 0.5 45000`\n\n"
    "📊 /mystats — Show avg entry + live deviation per coin\n\n"
    "🔔 /setalert — Set alert threshold\n"
    "  `/setalert BTC 20` — alert at 20% deviation, silence 24h\n"
    "  `/setalert BTC 20 12` — same, re-alert after 12h\n\n"
    "❓ /help — Show this message\n\n"
    "_⏱ Alerts fire at most once per direction (below/above) per coin per silence window._"
)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
