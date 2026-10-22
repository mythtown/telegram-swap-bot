import logging
from aiogram import Bot, Router
from aiogram.types import ChatJoinRequest
from sqlalchemy.ext.asyncio import AsyncSession
from bot.services import lead_service

logger = logging.getLogger(__name__)

router = Router(name="join_requests_router")


@router.chat_join_request()
async def on_chat_join_request(
    event: ChatJoinRequest,
    bot: Bot,
    session: AsyncSession,
) -> None:
    """Triggered by Telegram whenever a student taps 'Request to Join' on a private channel."""
    logger.info(
        f"[Event: chat_join_request] Student {event.from_user.id} requested to join {event.chat.id} via {event.invite_link.invite_link if event.invite_link else 'unknown'}"
    )
    await lead_service.handle_student_join_request(
        bot=bot,
        event=event,
        session=session,
    )
