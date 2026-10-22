import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from bot.config import config
from bot.database.session import async_session_factory
from bot.database import crud
from bot.services import swap_engine
from bot.services import view_scanner

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_matchmaking(bot: Bot) -> None:
    async with async_session_factory() as session:
        try:
            matched = await swap_engine.run_matchmaking_cycle(bot, session)
            if matched > 0:
                logger.info(f"[Scheduler] Matched {matched} new swap deals.")
        except Exception as e:
            logger.error(f"[Scheduler] Error during scheduled matchmaking: {e}")


async def scheduled_view_scanning(bot: Bot) -> None:
    try:
        await view_scanner.scan_active_deals_views(bot)
    except Exception as e:
        logger.error(f"[Scheduler] Error in scheduled view scanning: {e}")


async def scheduled_stale_cleanup(bot: Bot) -> None:
    async with async_session_factory() as session:
        try:
            cleaned = await swap_engine.cleanup_stale_deals(bot, session, max_hours=config.deal_timeout_hours)
            if cleaned > 0:
                logger.info(f"[Scheduler] Cleaned up {cleaned} stale swap deals.")
        except Exception as e:
            logger.error(f"[Scheduler] Error during stale cleanup: {e}")


async def scheduled_weekly_quota_reset() -> None:
    async with async_session_factory() as session:
        try:
            count = await crud.reset_weekly_quotas(session)
            logger.info(f"[Scheduler] Reset weekly swap quotas for {count} users.")
        except Exception as e:
            logger.error(f"[Scheduler] Error resetting weekly quotas: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    # 1. Matchmaking Job (every 60s)
    scheduler.add_job(
        scheduled_matchmaking,
        trigger=IntervalTrigger(seconds=config.matchmaking_interval_seconds),
        args=[bot],
        id="matchmaking_job",
        replace_existing=True,
    )

    # 2. Automated Eye-Icon View Scanner Job (every 45s)
    scheduler.add_job(
        scheduled_view_scanning,
        trigger=IntervalTrigger(seconds=config.scanner_interval_seconds),
        args=[bot],
        id="view_scanner_job",
        replace_existing=True,
    )

    # 3. Stale Deals Cleanup Job (every 300s)
    scheduler.add_job(
        scheduled_stale_cleanup,
        trigger=IntervalTrigger(seconds=config.cleanup_interval_seconds),
        args=[bot],
        id="stale_cleanup_job",
        replace_existing=True,
    )

    # 4. Weekly Quota Reset Job (Every Monday at 00:00 UTC)
    scheduler.add_job(
        scheduled_weekly_quota_reset,
        trigger=CronTrigger(day_of_week="mon", hour=0, minute=0, timezone="UTC"),
        id="weekly_quota_reset_job",
        replace_existing=True,
    )

    return scheduler
