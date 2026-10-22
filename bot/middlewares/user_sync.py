from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud


class UserSyncMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        tg_user: TgUser = data.get("event_from_user")

        if session and tg_user and not tg_user.is_bot:
            user = await crud.get_or_create_user(
                session=session,
                telegram_id=tg_user.id,
                username=tg_user.username,
                full_name=tg_user.full_name or "",
            )
            data["current_user"] = user

        return await handler(event, data)
