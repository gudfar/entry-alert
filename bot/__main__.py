"""Entry point: wires the Telegram bot and APScheduler into a single process."""

import asyncio
import logging
import os
import signal

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from bot import db
from bot.handlers.start import start
from bot.handlers.add import add
from bot.handlers.mystats import mystats
from bot.handlers.setalert import setalert
from bot.handlers.help import help_command
from bot.scheduler import build_scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    token = os.environ["TELEGRAM_TOKEN"]

    # Initialise DB pool (runs migrations on first boot)
    await db.init_pool()
    logger.info("Database pool ready")

    # Build PTB application
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("mystats", mystats))
    app.add_handler(CommandHandler("setalert", setalert))
    app.add_handler(CommandHandler("help", help_command))

    # Build and start scheduler
    scheduler = build_scheduler(app.bot)
    scheduler.start()
    logger.info("Scheduler started")

    # Graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _handle_signal():
        logger.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handle_signal)

    logger.info("Starting bot (polling mode)")
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await stop_event.wait()
        logger.info("Stopping...")
        await app.updater.stop()
        await app.stop()

    scheduler.shutdown(wait=False)
    await db.close_pool()
    logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
