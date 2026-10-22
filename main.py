import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import config
from bot.database.session import engine, init_db
from bot.handlers import (
    admin_router,
    broadcast_router,
    channels_router,
    creatives_router,
    deals_router,
    join_requests_router,
    leads_router,
    pool_router,
    start_router,
)
from bot.middlewares import DbSessionMiddleware, UserSyncMiddleware
from bot.services.scheduler import setup_scheduler
from bot.services.view_scanner import get_scanner_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("EduSwapBot")


async def main() -> None:
    if not config.bot_token:
        logger.error("BOT_TOKEN is not configured! Please provide a valid token in .env or environment.")
        return

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully.")

    # Initialize Telethon Eye-Icon View Scanner
    try:
        scanner = await get_scanner_client()
        if await scanner.is_user_authorized():
            scanner_me = await scanner.get_me()
            logger.info(f"View Scanner authenticated as @{scanner_me.username} ({scanner_me.id})")
        else:
            logger.warning("View Scanner session not authorized yet.")
    except Exception as e:
        logger.error(f"Failed to start View Scanner: {e}")

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register Middlewares
    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.middleware(UserSyncMiddleware())

    # Register Handlers
    dp.include_router(start_router)
    dp.include_router(channels_router)
    dp.include_router(creatives_router)
    dp.include_router(pool_router)
    dp.include_router(deals_router)
    dp.include_router(join_requests_router)
    dp.include_router(leads_router)
    dp.include_router(broadcast_router)
    dp.include_router(admin_router)

    # Setup APScheduler
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("APScheduler background tasks started.")

    # Drop any pending updates before polling to start fresh
    await bot.delete_webhook(drop_pending_updates=True)

    allowed_updates = dp.resolve_used_update_types()
    logger.info(f"Starting bot polling with allowed_updates: {allowed_updates}")

    try:
        await dp.start_polling(bot, allowed_updates=allowed_updates)
    finally:
        logger.info("Shutting down bot...")
        scheduler.shutdown(wait=False)
        try:
            scanner = await get_scanner_client()
            if scanner.is_connected():
                await scanner.disconnect()
        except Exception:
            pass
        await engine.dispose()
        await bot.session.close()
        logger.info("Shutdown completed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
