"""APScheduler setup — hourly price check job."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot

logger = logging.getLogger(__name__)


def build_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Create and return an AsyncIOScheduler with the price check job registered."""
    from bot.alerts import run_price_check

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_price_check,
        trigger="interval",
        minutes=60,
        args=[bot],
        id="price_check",
        name="Hourly price check",
        max_instances=1,
        misfire_grace_time=300,
    )
    logger.info("Scheduler configured: price check every 60 minutes")
    return scheduler
