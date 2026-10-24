from typing import Optional
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import config
from bot.database import crud
from bot.database.models import User
from bot.keyboards.common import (
    access_request_keyboard,
    admin_approve_user_keyboard,
    initial_language_keyboard,
    language_selector_keyboard,
    main_menu_keyboard,
    main_reply_keyboard,
    mandatory_sub_keyboard,
    settings_keyboard,
)
from bot.locales.texts import LANGUAGES, t
from bot.services import lead_service

router = Router(name="start_router")


def is_start_command(message: Message) -> bool:
    if not message.text:
        return False
    cmd = message.text.split()[0].lower()
    return cmd in ("/start", ".start", "/menu", ".menu")


async def check_mandatory_subscription(
    bot: Bot,
    session: AsyncSession,
    user_id: int,
) -> Optional[str]:
    """Returns mandatory channel if user is not subscribed. Returns None if subscribed or check disabled."""
    if config.is_admin(user_id):
        return None
    channel = await crud.get_system_setting(session, "mandatory_channel", config.mandatory_channel)
    if not channel or not channel.strip():
        return None
    channel = channel.strip()
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status in ("creator", "administrator", "member", "restricted"):
            return None
    except Exception:
        # If check fails or bot lacks permission, don't lock out users
        return None
    return channel


async def show_user_start_dashboard(
    bot: Bot,
    session: AsyncSession,
    current_user: User,
    chat_id: int,
    user_name: str,
    target_message: Optional[Message] = None,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"

    # Mandatory Channel Subscription Check
    unsub_channel = await check_mandatory_subscription(bot, session, chat_id)
    if unsub_channel:
        sub_text = t("mandatory_sub_prompt", lang)
        sub_kb = mandatory_sub_keyboard(unsub_channel, lang=lang)
        if target_message:
            try:
                await target_message.edit_text(sub_text, reply_markup=sub_kb)
                return
            except Exception:
                pass
        await bot.send_message(chat_id=chat_id, text=sub_text, reply_markup=sub_kb)
        return

    is_admin = config.is_admin(chat_id)
    is_vip = current_user.is_vip_active
    plan_name = "💎 VIP" if is_vip else ("Free" if lang == "en" else "Oddiy")
    limit_val = "∞" if is_vip else str(config.free_weekly_swap_limit)

    welcome_text = t(
        "welcome_approved",
        lang,
        name=user_name,
        plan=plan_name,
        swaps=current_user.swaps_this_week,
        limit=limit_val,
    )

    reply_markup = main_reply_keyboard(lang=lang, is_vip=is_vip, is_admin=is_admin)
    inline_markup = main_menu_keyboard(lang=lang, is_vip=is_vip, is_admin=is_admin)

    # Deliver reply keyboard and dashboard
    await bot.send_message(chat_id=chat_id, text="⚡ EduSwap", reply_markup=reply_markup)
    if target_message:
        try:
            await target_message.edit_text(welcome_text, reply_markup=inline_markup)
            return
        except Exception:
            pass
    await bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=inline_markup)


@router.message(is_start_command)
async def cmd_start(
    message: Message,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    await state.clear()

    # Deep-linking check (e.g. /start gift_DEALID_CHANNELID or /start ref_USERID)
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        param = args[1].strip()
        if param.startswith("gift_"):
            parts = param.split("_")
            if len(parts) >= 3:
                deal_id_str = parts[1]
                try:
                    channel_id = int(parts[2])
                    await lead_service.confirm_and_deliver_gift(
                        bot=bot,
                        session=session,
                        student_id=message.from_user.id,
                        deal_id_str=deal_id_str,
                        channel_id=channel_id,
                        student_name=message.from_user.full_name or "Student",
                        student_username=message.from_user.username,
                    )
                    return
                except Exception:
                    pass
        elif param.startswith("ref_"):
            ref_str = param.replace("ref_", "")
            if ref_str.isdigit() and int(ref_str) != message.from_user.id:
                if not getattr(message.from_user, "is_bot", False):
                    await crud.record_referral_invitation(session, message.from_user.id, int(ref_str))

    # First Start: Ask user to choose their preferred language first!
    if not current_user.language:
        prompt_text = "🌐 <b>Uzb / Rus / Eng:</b>"
        await message.answer(prompt_text, reply_markup=initial_language_keyboard())
        return

    # Language already set -> Show dashboard
    await show_user_start_dashboard(
        bot=bot,
        session=session,
        current_user=current_user,
        chat_id=message.from_user.id,
        user_name=message.from_user.full_name,
    )


@router.callback_query(F.data.startswith("init_lang:"))
async def cb_initial_language(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = callback.data.split(":")[1]
    if lang not in LANGUAGES:
        lang = "uz"

    await crud.update_user_language(session, callback.from_user.id, lang)
    current_user.language = lang
    await callback.answer()

    await show_user_start_dashboard(
        bot=bot,
        session=session,
        current_user=current_user,
        chat_id=callback.from_user.id,
        user_name=callback.from_user.full_name,
        target_message=callback.message,
    )


@router.callback_query(F.data == "sub:check")
async def cb_check_sub(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    unsub_channel = await check_mandatory_subscription(bot, session, callback.from_user.id)
    if unsub_channel:
        await callback.answer(t("sub_not_joined_alert", lang), show_alert=True)
        return

    await callback.answer(t("sub_confirmed_succ", lang))
    await show_user_start_dashboard(
        bot=bot,
        session=session,
        current_user=current_user,
        chat_id=callback.from_user.id,
        user_name=callback.from_user.full_name,
        target_message=callback.message,
    )


@router.message(F.text.in_(["👥 Taklif qilish", "👥 Рефералы", "👥 Invite Friends"]))
@router.message(Command("ref", "referral"))
@router.callback_query(F.data == "menu:referral")
async def show_referral_center(
    event: Message | CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{current_user.telegram_id}"

    target_str = await crud.get_system_setting(session, "referral_target", str(config.referral_target))
    days_str = await crud.get_system_setting(session, "referral_reward_days", str(config.referral_reward_days))
    target = int(target_str) if target_str.isdigit() else config.referral_target
    days = int(days_str) if days_str.isdigit() else config.referral_reward_days

    text = t(
        "referral_dashboard",
        lang,
        link=ref_link,
        total=current_user.referrals_count or 0,
        qualified=current_user.qualified_referrals_count or 0,
        target=target,
        days=days,
    )

    share_text = f"EduSwap - Telegram ta'lim kanallarini avtomatlashtirilgan o'zaro reklama qilish boti: {ref_link}"
    share_url = f"https://t.me/share/url?url={ref_link}&text={share_text}"
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_share_ref", lang), url=share_url)],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
        ]
    )

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=markup)
        except Exception:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup)


@router.message(Command("lang", "language"))
async def cmd_language(
    message: Message,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    choose_text = "🌐 <b>Uzb / Rus / Eng:</b>"
    markup = language_selector_keyboard(current_lang=lang)
    await message.answer(choose_text, reply_markup=markup)


@router.callback_query(F.data == "access:request")
async def cb_request_access(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    await crud.set_user_pending(session, callback.from_user.id, pending=True)

    text = t("request_submitted", lang)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_support", lang), url=f"https://t.me/{config.support_username}")],
            [InlineKeyboardButton(text=t("btn_check_status", lang), callback_data="access:check")],
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

    # SuperAdmin notification
    admin_alert = (
        "🔔 <b>Yangi o'qituvchi arizasi! / New Teacher Request!</b>\n\n"
        f"👤 <b>Ism:</b> {callback.from_user.full_name}\n"
        f"🔗 <b>Username:</b> @{callback.from_user.username or 'None'}\n"
        f"🆔 <b>User ID:</b> <code>{callback.from_user.id}</code>\n\n"
        "<i>Ruxsat berasizmi?</i>"
    )
    admin_markup = admin_approve_user_keyboard(callback.from_user.id)
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id, text=admin_alert, reply_markup=admin_markup)
        except Exception:
            pass


@router.callback_query(F.data == "access:check")
async def cb_check_access_status(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    if current_user.is_approved:
        approved_msg = "✅ Ruxsat berilgan!" if lang == "uz" else ("✅ Доступ одобрен!" if lang == "ru" else "✅ Access approved!")
        await callback.answer(approved_msg, show_alert=True)
        await show_user_start_dashboard(
            bot=bot,
            session=session,
            current_user=current_user,
            chat_id=callback.from_user.id,
            user_name=callback.from_user.full_name,
            target_message=callback.message,
        )
    else:
        wait_msg = "⏳ Arizangiz ko'rib chiqilmoqda..." if lang == "uz" else ("⏳ Заявка на рассмотрении..." if lang == "ru" else "⏳ Application under review...")
        await callback.answer(wait_msg, show_alert=True)


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(
    callback: CallbackQuery,
    current_user: User,
    state: FSMContext,
) -> None:
    await state.clear()
    lang = getattr(current_user, "language", "uz") or "uz"
    is_admin = config.is_admin(callback.from_user.id)
    is_vip = current_user.is_vip_active
    plan_name = "💎 VIP" if is_vip else ("Free" if lang == "en" else "Oddiy")
    limit_val = "∞" if is_vip else str(config.free_weekly_swap_limit)

    menu_text = t(
        "welcome_approved",
        lang,
        name=callback.from_user.full_name,
        plan=plan_name,
        swaps=current_user.swaps_this_week,
        limit=limit_val,
    )
    markup = main_menu_keyboard(lang=lang, is_vip=is_vip, is_admin=is_admin)
    try:
        await callback.message.edit_text(menu_text, reply_markup=markup)
    except Exception:
        await callback.message.answer(menu_text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data == "menu:settings")
async def cb_settings_menu(
    callback: CallbackQuery,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    plan_name = "💎 VIP" if current_user.is_vip_active else ("Free" if lang == "en" else "Oddiy")
    text = t(
        "settings_title",
        lang,
        name=callback.from_user.full_name,
        plan=plan_name,
        user_id=callback.from_user.id,
    )
    markup = settings_keyboard(lang=lang, is_vip=current_user.is_vip_active)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data == "menu:language")
async def cb_language_picker(
    callback: CallbackQuery,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    choose_text = "🌐 <b>Uzb / Rus / Eng:</b>"
    markup = language_selector_keyboard(current_lang=lang)
    await callback.message.edit_text(choose_text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_language(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    new_lang = callback.data.split(":")[1]
    if new_lang in LANGUAGES:
        await crud.update_user_language(session, callback.from_user.id, new_lang)
        current_user.language = new_lang

    confirm_msg = t("lang_changed", new_lang)
    await callback.answer(confirm_msg, show_alert=False)

    is_admin = config.is_admin(callback.from_user.id)
    is_vip = current_user.is_vip_active

    # Update Reply Keyboard in new language
    reply_kb = main_reply_keyboard(lang=new_lang, is_vip=is_vip, is_admin=is_admin)
    await callback.message.answer(confirm_msg, reply_markup=reply_kb)

    # Refresh settings view
    plan_name = "💎 VIP" if is_vip else ("Free" if new_lang == "en" else "Oddiy")
    text = t(
        "settings_title",
        new_lang,
        name=callback.from_user.full_name,
        plan=plan_name,
        user_id=callback.from_user.id,
    )
    markup = settings_keyboard(lang=new_lang, is_vip=is_vip)
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "menu:support")
async def cb_support_menu(
    callback: CallbackQuery,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text = t("support_text", lang, support=config.support_username)
    chat_btn_txt = "✉ Bog'lanish" if lang == "uz" else ("✉ Написать" if lang == "ru" else "✉ Message Admin")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=chat_btn_txt, url=f"https://t.me/{config.support_username}")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data == "menu:vip_info")
async def cb_vip_info(
    callback: CallbackQuery,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text = t("vip_info_text", lang, support=config.support_username)
    upgrade_btn_txt = "💎 VIP ga o'tish" if lang == "uz" else ("💎 Подключить VIP" if lang == "ru" else "💎 Upgrade to VIP")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=upgrade_btn_txt, url=f"https://t.me/{config.support_username}")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


# ==================== REPLY KEYBOARD TEXT ROUTERS ====================

@router.message(F.text.in_([
    "⚙ Sozlamalar", "⚙ Настройки", "⚙ Settings"
]))
async def msg_settings_router(message: Message, current_user: User) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    plan_name = "💎 VIP" if current_user.is_vip_active else ("Free" if lang == "en" else "Oddiy")
    text = t(
        "settings_title",
        lang,
        name=message.from_user.full_name,
        plan=plan_name,
        user_id=message.from_user.id,
    )
    markup = settings_keyboard(lang=lang, is_vip=current_user.is_vip_active)
    await message.answer(text, reply_markup=markup)


@router.message(F.text.in_([
    "💬 Aloqa", "💬 Поддержка", "💬 Support"
]))
async def msg_support_router(message: Message, current_user: User) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text = t("support_text", lang, support=config.support_username)
    chat_btn_txt = "✉ Bog'lanish" if lang == "uz" else ("✉ Написать" if lang == "ru" else "✉ Message Admin")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=chat_btn_txt, url=f"https://t.me/{config.support_username}")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
        ]
    )
    await message.answer(text, reply_markup=markup)


@router.message(F.text.in_([
    "💎 VIP Tarif", "💎 VIP Тариф", "💎 VIP Upgrade"
]))
async def msg_vip_router(message: Message, current_user: User) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text = t("vip_info_text", lang, support=config.support_username)
    upgrade_btn_txt = "💎 VIP ga o'tish" if lang == "uz" else ("💎 Подключить VIP" if lang == "ru" else "💎 Upgrade to VIP")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=upgrade_btn_txt, url=f"https://t.me/{config.support_username}")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
        ]
    )
    await message.answer(text, reply_markup=markup)
