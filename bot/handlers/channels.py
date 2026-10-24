from datetime import datetime, timedelta, timezone
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatMemberAdministrator, ChatMemberOwner, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import config
from bot.database import crud
from bot.database.models import User
from bot.keyboards.channel_kb import (
    channel_details_keyboard,
    channels_list_keyboard,
    confirm_channel_delete_keyboard,
    schedule_settings_keyboard,
    tier_selector_keyboard,
)
from bot.keyboards.common import cancel_action_keyboard
from bot.locales.texts import t
from bot.services.time_utils import format_clock, format_remaining_timer, tashkent_now
from bot.states.states import AddChannelState

router = Router(name="channels_router")


async def verify_bot_permissions(bot: Bot, channel_id: int) -> tuple[bool, str]:
    """Verifies that the bot is an admin with post, delete, and invite permissions."""
    try:
        bot_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        return False, f"Bot is not in channel: {e}"

    if not isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner)):
        return False, "Bot is not an Administrator."

    if isinstance(bot_member, ChatMemberOwner):
        return True, "Bot is owner."

    missing = []
    if not bot_member.can_post_messages:
        missing.append("Post Messages")
    if not bot_member.can_delete_messages:
        missing.append("Delete Messages")
    if not bot_member.can_invite_users:
        missing.append("Invite Users")

    if missing:
        return False, f"Missing permissions: {', '.join(missing)}"

    return True, "OK"


# ==================== LIST CHANNELS ====================

@router.callback_query(F.data == "menu:channels")
async def cb_list_channels(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)
    if not channels:
        text = t("no_channels", lang)
    else:
        text = t("channels_list_title", lang, count=len(channels))
    markup = channels_list_keyboard(channels, lang=lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.message(F.text.in_(["≡ Kanallar", "≡ Мои каналы", "≡ Channels"]))
async def msg_list_channels(
    message: Message,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)
    if not channels:
        text = t("no_channels", lang)
    else:
        text = t("channels_list_title", lang, count=len(channels))
    markup = channels_list_keyboard(channels, lang=lang)
    await message.answer(text, reply_markup=markup)


# ==================== ADD CHANNEL ====================

@router.callback_query(F.data == "channel:add")
async def cb_add_channel_prompt(
    callback: CallbackQuery,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    bot_info = await callback.bot.get_me()
    text = t("add_channel_prompt", lang, bot_name=bot_info.username, scanner_name=config.scanner_username)
    await state.set_state(AddChannelState.waiting_for_forward_or_id)
    try:
        await callback.message.edit_text(text, reply_markup=cancel_action_keyboard(lang=lang, return_to="menu:channels"))
    except Exception:
        await callback.message.answer(text, reply_markup=cancel_action_keyboard(lang=lang, return_to="menu:channels"))
    await callback.answer()


@router.message(F.text.in_(["+ Kanal qo'shish", "+ Добавить канал", "+ Add Channel"]))
async def msg_add_channel(
    message: Message,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    bot_info = await message.bot.get_me()
    text = t("add_channel_prompt", lang, bot_name=bot_info.username, scanner_name=config.scanner_username)
    await state.set_state(AddChannelState.waiting_for_forward_or_id)
    await message.answer(text, reply_markup=cancel_action_keyboard(lang=lang, return_to="menu:channels"))


@router.message(AddChannelState.waiting_for_forward_or_id)
async def process_channel_input(
    message: Message,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channel_id = None
    if message.forward_from_chat:
        channel_id = message.forward_from_chat.id
    elif message.text:
        text_val = message.text.strip()
        if text_val.startswith("-100") and text_val[1:].isdigit():
            channel_id = int(text_val)
        elif text_val.startswith("@") or not text_val.startswith("/"):
            channel_id = text_val

    if not channel_id:
        await message.answer(t("channel_not_found", lang), reply_markup=cancel_action_keyboard(lang=lang, return_to="menu:channels"))
        return

    try:
        chat = await bot.get_chat(chat_id=channel_id)
    except Exception:
        await message.answer(t("channel_not_found", lang), reply_markup=cancel_action_keyboard(lang=lang, return_to="menu:channels"))
        return

    is_valid, msg = await verify_bot_permissions(bot, chat.id)
    if not is_valid:
        await message.answer(t("perms_insufficient", lang, msg=msg), reply_markup=cancel_action_keyboard(lang=lang, return_to="menu:channels"))
        return

    channel = await crud.create_or_update_channel(
        session=session,
        telegram_id=chat.id,
        owner_id=current_user.telegram_id,
        title=chat.title or "Channel",
        username=chat.username,
        is_verified=True,
    )
    await state.clear()

    # Anti-Nakrutka Referral Qualification:
    try:
        subs_count = await bot.get_chat_member_count(chat.id)
    except Exception:
        subs_count = 100

    ref_res = await crud.check_and_qualify_referral(
        session=session,
        user_id=current_user.telegram_id,
        channel_subscribers=subs_count,
        min_subs=config.referral_min_subs,
    )
    if ref_res:
        ref_id = ref_res["referrer_id"]
        ref_lang = ref_res["referrer_lang"]
        if ref_res.get("vip_awarded"):
            congrats_text = t(
                "referral_reward_congrats",
                ref_lang,
                target=ref_res["target"],
                days=ref_res["days"],
            )
            try:
                from bot.keyboards.common import main_reply_keyboard
                ref_kb = main_reply_keyboard(lang=ref_lang, is_vip=True, is_admin=config.is_admin(ref_id))
                await bot.send_message(chat_id=ref_id, text=congrats_text, reply_markup=ref_kb)
            except Exception:
                pass
        else:
            notice = (
                f"🎉 Siz taklif qilgan ustoz ({current_user.full_name}) haqiqiy kanal qo'shdi! "
                f"Sizga +1 ball berildi ({ref_res['qualified_count']}/{ref_res['target']})."
                if ref_lang == "uz" else
                (
                    f"🎉 Приглашенный вами учитель ({current_user.full_name}) добавил активный канал! "
                    f"Вам начислен +1 балл ({ref_res['qualified_count']}/{ref_res['target']})."
                    if ref_lang == "ru" else
                    f"🎉 Your invited teacher ({current_user.full_name}) added an active channel! "
                    f"+1 point awarded ({ref_res['qualified_count']}/{ref_res['target']})."
                )
            )
            try:
                await bot.send_message(chat_id=ref_id, text=notice)
            except Exception:
                pass

    succ = t("channel_connected_succ", lang, title=channel.title, tier=channel.target_tier, scanner=config.scanner_username)
    markup = channel_details_keyboard(channel, has_creative=False, lang=lang)
    await message.answer(succ, reply_markup=markup)


# ==================== VIEW & MANAGE CHANNEL ====================

@router.callback_query(F.data.startswith("channel:view:"))
async def cb_view_channel(
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

    creative = channel.creative
    has_creative = creative is not None and bool(creative.ad_text and (creative.gift_file_id or creative.gift_text_content))

    if lang == "uz":
        status_pool = "🟢 Faol (Havzada)" if channel.is_in_pool else "⚪️ To'xtatilgan"
        status_creative = "✅ Tayyor" if has_creative else "❌ Yuklanmagan"
    elif lang == "ru":
        status_pool = "🟢 Активен (В пуле)" if channel.is_in_pool else "⚪️ На паузе"
        status_creative = "✅ Готов" if has_creative else "❌ Не настроен"
    else:
        status_pool = "🟢 Active (In Pool)" if channel.is_in_pool else "⚪️ Paused"
        status_creative = "✅ Ready" if has_creative else "❌ Not set"

    win_map = {
        "evening": "🌆 Kechki (18-22)" if lang == "uz" else ("🌆 Вечер (18-22)" if lang == "ru" else "🌆 Evening (18-22)"),
        "morning": "☀️ Ertalabki (09-13)" if lang == "uz" else ("☀️ Утро (09-13)" if lang == "ru" else "☀️ Morning (09-13)"),
        "anytime": "24/7 Har doim" if lang == "uz" else ("24/7 Всегда" if lang == "ru" else "24/7 Anytime"),
    }
    win_name = win_map.get(channel.posting_window, "24/7")

    text = t(
        "channel_details_title",
        lang,
        title=channel.title,
        tier=channel.target_tier,
        pool_status=status_pool,
        creative_status=status_creative,
        window=win_name,
        cooldown=channel.swap_cooldown_hours,
    )
    markup = channel_details_keyboard(channel, has_creative=has_creative, lang=lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("channel:schedule:"))
async def cb_channel_schedule(
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

    # Timer & Clock status check
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    cooldown_sec = 0.0
    if channel.last_swap_finished_at and channel.swap_cooldown_hours > 0:
        expiry = channel.last_swap_finished_at + timedelta(hours=channel.swap_cooldown_hours)
        cooldown_sec = max(0.0, (expiry - now_utc).total_seconds())

    cooldown_status = format_remaining_timer(cooldown_sec, lang=lang)
    clock_str = format_clock()

    text = t(
        "channel_schedule_title",
        lang,
        title=channel.title,
        clock=clock_str,
        cooldown_status=cooldown_status,
    )
    markup = schedule_settings_keyboard(channel, lang=lang)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("channel:set_win:"))
async def cb_set_window(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    parts = callback.data.split(":")
    channel_id = int(parts[2])
    window = parts[3]

    channel = await crud.get_channel(session, channel_id)
    if not channel:
        return

    await crud.set_channel_schedule(session, channel_id, posting_window=window, cooldown_hours=channel.swap_cooldown_hours)
    channel.posting_window = window
    await callback.answer(t("settings_saved", lang))
    await callback.message.edit_reply_markup(reply_markup=schedule_settings_keyboard(channel, lang=lang))


@router.callback_query(F.data.startswith("channel:set_cd:"))
async def cb_set_cooldown(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    parts = callback.data.split(":")
    channel_id = int(parts[2])
    hours = int(parts[3])

    channel = await crud.get_channel(session, channel_id)
    if not channel:
        return

    await crud.set_channel_schedule(session, channel_id, posting_window=channel.posting_window, cooldown_hours=hours)
    channel.swap_cooldown_hours = hours
    await callback.answer(f"✅ {hours}h")
    await callback.message.edit_reply_markup(reply_markup=schedule_settings_keyboard(channel, lang=lang))


@router.callback_query(F.data.startswith("channel:tier:"))
async def cb_tier_menu(
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

    choose_tier_txt = (
        f"🎯 <b>{channel.title} — Ko'rishlar rejasini tanlang (👀)</b>\n\n"
        "Sherik kanalda reklama aynan necha ko'rish to'planganda avtomatik o'chirilishini xohlaysiz?"
    ) if lang == "uz" else (
        f"🎯 <b>{channel.title} — Цель по просмотрам (👀)</b>\n\n"
        "Сколько просмотров должен набрать пост в канале партнера до авто-удаления?"
    ) if lang == "ru" else (
        f"🎯 <b>{channel.title} — Select View Target (👀)</b>\n\n"
        "How many post views should your ad reach before automated deletion?"
    )
    markup = tier_selector_keyboard(channel_id, channel.target_tier, lang=lang)
    await callback.message.edit_text(choose_tier_txt, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("channel:set_tier:"))
async def cb_set_tier(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    parts = callback.data.split(":")
    channel_id = int(parts[2])
    tier = int(parts[3])

    channel = await crud.set_channel_tier(session, channel_id, tier)
    if not channel:
        await callback.answer(t("channel_not_found", lang), show_alert=True)
        return

    await callback.answer(f"✅ {tier} 👀", show_alert=False)
    creative = channel.creative
    has_creative = creative is not None and bool(creative.ad_text and (creative.gift_file_id or creative.gift_text_content))
    markup = channel_details_keyboard(channel, has_creative=has_creative, lang=lang)

    if lang == "uz":
        status_pool = "🟢 Faol (Havzada)" if channel.is_in_pool else "⚪️ To'xtatilgan"
        status_creative = "✅ Tayyor" if has_creative else "❌ Yuklanmagan"
    elif lang == "ru":
        status_pool = "🟢 Активен (В пуле)" if channel.is_in_pool else "⚪️ На паузе"
        status_creative = "✅ Готов" if has_creative else "❌ Не настроен"
    else:
        status_pool = "🟢 Active (In Pool)" if channel.is_in_pool else "⚪️ Paused"
        status_creative = "✅ Ready" if has_creative else "❌ Not set"

    text = t(
        "channel_details_title",
        lang,
        title=channel.title,
        tier=channel.target_tier,
        pool_status=status_pool,
        creative_status=status_creative,
        window=channel.posting_window,
        cooldown=channel.swap_cooldown_hours,
    )
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.startswith("channel:verify:"))
async def cb_reverify_channel(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channel_id = int(callback.data.split(":")[2])
    channel = await crud.get_channel(session, channel_id)
    if not channel:
        await callback.answer(t("channel_not_found", lang), show_alert=True)
        return

    is_valid, msg = await verify_bot_permissions(bot, channel_id)
    await crud.create_or_update_channel(
        session=session,
        telegram_id=channel.telegram_id,
        owner_id=channel.owner_id,
        title=channel.title,
        username=channel.username,
        is_verified=is_valid,
    )
    if is_valid:
        ok_txt = "✅ Ruxsatlar tasdiqlandi!" if lang == "uz" else ("✅ Права подтверждены!" if lang == "ru" else "✅ Permissions verified!")
        await callback.answer(ok_txt, show_alert=True)
    else:
        await callback.answer(f"⚠️ {msg}", show_alert=True)

    creative = channel.creative
    has_creative = creative is not None and bool(creative.ad_text and (creative.gift_file_id or creative.gift_text_content))
    markup = channel_details_keyboard(channel, has_creative=has_creative, lang=lang)
    await callback.message.edit_reply_markup(reply_markup=markup)


@router.callback_query(F.data.startswith("channel:delete_confirm:"))
async def cb_delete_confirm(
    callback: CallbackQuery,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channel_id = int(callback.data.split(":")[2])
    text = t("channel_delete_confirm", lang)
    await callback.message.edit_text(text, reply_markup=confirm_channel_delete_keyboard(channel_id, lang=lang))
    await callback.answer()


@router.callback_query(F.data.startswith("channel:delete:"))
async def cb_delete_channel(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channel_id = int(callback.data.split(":")[2])
    await crud.delete_channel(session, channel_id)
    await callback.answer(t("channel_deleted", lang), show_alert=True)

    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)
    if not channels:
        text = t("no_channels", lang)
    else:
        text = t("channels_list_title", lang, count=len(channels))
    markup = channels_list_keyboard(channels, lang=lang)
    await callback.message.edit_text(text, reply_markup=markup)
