import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud

logger = logging.getLogger(__name__)


async def send_dm_broadcast(
    bot: Bot,
    session: AsyncSession,
    owner_id: int,
    channel_id: Optional[int],
    source_message: Message,
) -> dict:
    """Delivers teacher's broadcast message to all captured active students with flood-safe pacing."""
    leads = await crud.get_student_leads_by_owner(
        session=session,
        owner_id=owner_id,
        channel_id=channel_id,
    )
    total_targets = len(leads)
    sent_count = 0
    failed_count = 0

    logger.info(f"Starting broadcast for owner {owner_id} to {total_targets} student leads.")

    for lead in leads:
        try:
            await source_message.copy_to(chat_id=lead.student_telegram_id)
            sent_count += 1
            # Flood prevention sleep: ~25 messages/sec
            await asyncio.sleep(0.04)

        except TelegramRetryAfter as e:
            logger.warning(f"Flood limit encountered. Sleeping for {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after + 0.5)
            try:
                await source_message.copy_to(chat_id=lead.student_telegram_id)
                sent_count += 1
            except Exception:
                failed_count += 1

        except TelegramForbiddenError:
            # Student blocked the bot
            logger.info(f"Student {lead.student_telegram_id} blocked bot. Marking inactive.")
            await crud.mark_lead_inactive(session, lead.student_telegram_id)
            failed_count += 1

        except TelegramBadRequest as e:
            logger.warning(f"Failed to deliver broadcast to {lead.student_telegram_id}: {e}")
            failed_count += 1

        except Exception as e:
            logger.error(f"Unexpected error broadcasting to {lead.student_telegram_id}: {e}")
            failed_count += 1

    # Log to database
    await crud.log_broadcast(
        session=session,
        owner_id=owner_id,
        channel_id=channel_id,
        total=total_targets,
        sent=sent_count,
        failed=failed_count,
    )

    return {
        "total": total_targets,
        "sent": sent_count,
        "failed": failed_count,
    }
