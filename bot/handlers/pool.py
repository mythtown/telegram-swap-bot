from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import config
from bot.database import crud
from bot.database.models import User
from bot.locales.texts import t

router = Router(name="pool_router")


async def render_pool_dashboard(session: AsyncSession, current_user: User, lang: str):
    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)
    limit_val = "∞" if current_user.is_vip_active else str(config.free_weekly_swap_limit)

    if not channels:
        text = t("no_channels", lang)
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_add_channel", lang), callback_data="channel:add")],
                [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
            ]
        )
        return text, markup

    buttons = []
    text = t("pool_title", lang, swaps=current_user.swaps_this_week, limit=limit_val)

    for ch in channels:
        toggle_prefix = "🔴 " if ch.is_in_pool else "🟢 "
        action_word = ("To'xtatish" if ch.is_in_pool else "Qo'shish") if lang == "uz" else (
            ("Стоп" if ch.is_in_pool else "Старт") if lang == "ru" else (
                ("Pause" if ch.is_in_pool else "Start")
            )
        )
        btn_label = f"{toggle_prefix}{action_word}: {ch.title[:15]}"
        buttons.append([
            InlineKeyboardButton(
                text=btn_label,
                callback_data=f"pool:toggle:{ch.telegram_id}",
            )
        ])

    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return text, markup


@router.callback_query(F.data == "menu:pool")
async def cb_pool_dashboard(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_pool_dashboard(session, current_user, lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.message(F.text.in_(["⚡ Auto-VP", "⚡ Авто-ВП"]))
async def msg_pool_dashboard(
    message: Message,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_pool_dashboard(session, current_user, lang)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("pool:toggle:"))
async def cb_toggle_pool(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channel_id = int(callback.data.split(":")[2])
    channel = await crud.get_channel(session, channel_id)
    if not channel:
        await callback.answer(t("channel_not_found", lang), show_alert=True)
        return

    # Check creative upload requirement before joining pool
    if not channel.is_in_pool:
        creative = channel.creative
        has_creative = creative is not None and bool(creative.ad_text and (creative.gift_file_id or creative.gift_text_content))
        if not has_creative:
            await callback.answer(t("need_creative_first", lang), show_alert=True)
            return

    new_status = not channel.is_in_pool
    await crud.set_channel_pool_status(session, channel_id, new_status)

    alert_txt = t("pool_added", lang) if new_status else t("pool_paused", lang)
    await callback.answer(alert_txt)

    text, markup = await render_pool_dashboard(session, current_user, lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        pass
