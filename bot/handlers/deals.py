from datetime import datetime, timedelta, timezone
from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud
from bot.database.models import User
from bot.keyboards.swap_kb import (
    confirm_deal_cancel_keyboard,
    deal_detail_keyboard,
    deals_list_keyboard,
)
from bot.locales.texts import t
from bot.services import swap_engine
from bot.services.time_utils import format_remaining_timer

router = Router(name="deals_router")


async def render_deals_list(session: AsyncSession, current_user: User, lang: str):
    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)
    user_channel_ids = [ch.telegram_id for ch in channels]
    deals = await crud.get_active_deals_for_owner(session, current_user.telegram_id)

    if not deals:
        text = t("no_deals", lang)
        markup = deals_list_keyboard([], user_channel_ids, lang=lang)
    else:
        text = t("deals_title", lang, count=len(deals))
        markup = deals_list_keyboard(deals, user_channel_ids, lang=lang)
    return text, markup


@router.callback_query(F.data == "menu:deals")
async def cb_list_deals(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_deals_list(session, current_user, lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.message(F.text.in_(["🤝 Bitimlar", "🤝 Сделки", "🤝 Active Deals"]))
async def msg_list_deals(
    message: Message,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_deals_list(session, current_user, lang)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("deal:view:"))
async def cb_view_deal(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    deal_id = callback.data.split(":")[2]
    deal = await crud.get_deal_by_id(session, deal_id)
    if not deal:
        await callback.answer(t("deal_not_found", lang), show_alert=True)
        return

    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)
    user_channel_ids = [ch.telegram_id for ch in channels]

    is_ch_a = deal.channel_a_id in user_channel_ids
    my_ch = deal.channel_a if is_ch_a else deal.channel_b
    partner_ch = deal.channel_b if is_ch_a else deal.channel_a

    my_views = deal.views_a_received if is_ch_a else deal.views_b_received
    partner_views = deal.views_b_received if is_ch_a else deal.views_a_received
    my_leads = deal.joins_a_received if is_ch_a else deal.joins_b_received

    # 24h Deal Timeout Timer calculation
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    started = deal.started_at
    if started and started.tzinfo is not None:
        started = started.replace(tzinfo=None)
    
    timer_str = "—"
    if deal.status == "ACTIVE" and started:
        time_elapsed = (now_utc - started).total_seconds()
        remaining_sec = max(0.0, (24 * 3600) - time_elapsed)
        timer_str = format_remaining_timer(remaining_sec, lang=lang)

    if lang == "uz":
        status_str = "🟢 Faol" if deal.status == "ACTIVE" else "✅ Yakunlangan"
    elif lang == "ru":
        status_str = "🟢 Активна" if deal.status == "ACTIVE" else "✅ Завершена"
    else:
        status_str = "🟢 Active" if deal.status == "ACTIVE" else "✅ Completed"

    text = t(
        "deal_detail_title",
        lang,
        deal_id=deal.id[:8],
        my_ch=my_ch.title,
        partner_ch=partner_ch.title,
        target=deal.target_views,
        my_views=my_views,
        partner_views=partner_views,
        my_leads=my_leads,
        timer=timer_str,
        status=status_str,
    )

    markup = deal_detail_keyboard(deal.id, is_active=(deal.status == "ACTIVE"), lang=lang)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("deal:cancel_confirm:"))
async def cb_cancel_confirm(
    callback: CallbackQuery,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    deal_id = callback.data.split(":")[2]
    await callback.message.edit_text(t("deal_cancel_confirm", lang), reply_markup=confirm_deal_cancel_keyboard(deal_id, lang=lang))
    await callback.answer()


@router.callback_query(F.data.startswith("deal:cancel:"))
async def cb_cancel_deal(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    deal_id = callback.data.split(":")[2]
    deal = await crud.get_deal_by_id(session, deal_id)
    if not deal or deal.status != "ACTIVE":
        await callback.answer(t("deal_already_finished", lang), show_alert=True)
        return

    await swap_engine.cancel_deal_and_cleanup(bot=bot, session=session, deal_id=deal_id)
    await callback.answer(t("deal_cancelled", lang), show_alert=True)

    text, markup = await render_deals_list(session, current_user, lang)
    await callback.message.edit_text(text, reply_markup=markup)
