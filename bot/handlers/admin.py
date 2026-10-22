from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import config
from bot.database import crud
from bot.keyboards.admin_kb import admin_panel_keyboard
from bot.keyboards.common import cancel_action_keyboard
from bot.services import swap_engine, view_scanner
from bot.states.states import AdminState

router = Router(name="admin_router")


from bot.locales.texts import t


def is_admin_filter(user_id: int) -> bool:
    return config.is_admin(user_id)


async def render_admin_dashboard(session: AsyncSession, lang: str = "uz"):
    stats = await crud.get_global_stats(session)
    text = t(
        "admin_dashboard_title",
        lang,
        scanner=config.scanner_username,
        users=stats["users"],
        approved=stats["approved_users"],
        vip=stats["vip_users"],
        channels=stats["channels"],
        pool=stats["pool_channels"],
        active_deals=stats["active_deals"],
        leads=stats["total_leads"],
    )
    markup = admin_panel_keyboard(lang=lang)
    return text, markup


@router.message(Command("admin"))
async def cmd_admin_panel(
    message: Message,
    session: AsyncSession,
    current_user: User,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return

    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_admin_dashboard(session, lang=lang)
    await message.answer(text, reply_markup=markup)


@router.message(F.text.in_(["⊘ Admin panel", "⊘ Админ-панель", "⊘ Admin Panel"]))
async def msg_admin_panel(
    message: Message,
    session: AsyncSession,
    current_user: User,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return

    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_admin_dashboard(session, lang=lang)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "admin:menu")
async def cb_admin_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Unauthorized.", show_alert=True)
        return

    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_admin_dashboard(session, lang=lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:approve:"))
async def cb_approve_teacher(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    user_id = int(callback.data.split(":")[2])
    user = await crud.set_user_approval(session, user_id, is_approved=True)

    await callback.message.edit_text(f"✅ <b>Teacher Approved!</b> (User ID: <code>{user_id}</code>)")
    await callback.answer("Teacher access granted!")

    # Notify Teacher
    try:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Enter Teacher Dashboard", callback_data="menu:main")]
            ]
        )
        await bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 <b>Congratulations! Teacher Access Approved!</b>\n\n"
                "Your application has been accepted by the administrator.\n"
                "You now have full access to connect your channels and start view swaps!\n\n"
                "👉 <i>Tap the button below to get started:</i>"
            ),
            reply_markup=markup,
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin:reject:"))
async def cb_reject_teacher(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    user_id = int(callback.data.split(":")[2])
    await crud.set_user_approval(session, user_id, is_approved=False)
    await callback.message.edit_text(f"❌ <b>Teacher Access Rejected.</b> (User ID: <code>{user_id}</code>)")
    await callback.answer("Application rejected.")


@router.message(Command("whitelist"))
async def cmd_quick_whitelist(
    message: Message,
    bot: Bot,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Usage: <code>/whitelist &lt;user_id&gt;</code>")
        return

    target_id = int(args[1])
    user = await crud.set_user_approval(session, target_id, is_approved=True)
    if user:
        await message.answer(f"✅ User <code>{target_id}</code> has been whitelisted for teacher access.")
        try:
            await bot.send_message(
                chat_id=target_id,
                text="🎉 <b>You have been approved for EduSwap access!</b> Send /start to begin.",
            )
        except Exception:
            pass
    else:
        await message.answer(f"User <code>{target_id}</code> not found in database.")


@router.callback_query(F.data == "admin:force_match")
async def cb_admin_force_match(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    await callback.answer("Running matchmaking cycle... ⏳")
    matched = await swap_engine.run_matchmaking_cycle(bot, session)
    await callback.message.answer(f"⚡ Matchmaking cycle completed! Matched <b>{matched}</b> new swap deals.")


@router.callback_query(F.data == "admin:force_scan")
async def cb_admin_force_scan(
    callback: CallbackQuery,
    bot: Bot,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    await callback.answer("Scanning eye-icon views on active deals... ⏳")
    scanned = await view_scanner.scan_active_deals_views(bot)
    await callback.message.answer(f"👁 View scan finished! Checked <b>{scanned}</b> active deals.")


@router.callback_query(F.data == "admin:force_cleanup")
async def cb_admin_force_cleanup(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    await callback.answer("Running 24h stale deal cleanup... ⏳")
    cleaned = await swap_engine.cleanup_stale_deals(bot, session, max_hours=config.deal_timeout_hours)
    await callback.message.answer(f"🧹 Stale cleanup completed! Cleaned up <b>{cleaned}</b> expired deals.")


@router.callback_query(F.data == "admin:reset_quotas")
async def cb_admin_reset_quotas(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    count = await crud.reset_weekly_quotas(session)
    await callback.answer("Weekly quotas reset!", show_alert=True)
    await callback.message.answer(f"🔄 Reset weekly swap quotas for <b>{count}</b> users.")


@router.callback_query(F.data == "admin:grant_vip")
async def cb_admin_prompt_grant_vip(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    await state.set_state(AdminState.waiting_for_vip_user)
    await callback.message.edit_text(
        "👑 <b>Grant VIP Status</b>\n\nPlease send the Telegram User ID (e.g. <code>123456789</code>):",
        reply_markup=cancel_action_keyboard("admin:menu"),
    )
    await callback.answer()


@router.message(AdminState.waiting_for_vip_user)
async def process_vip_target_user(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Please enter a numeric Telegram User ID.", reply_markup=cancel_action_keyboard("admin:menu"))
        return

    target_id = int(message.text.strip())
    await state.update_data(target_vip_user_id=target_id)
    await state.set_state(AdminState.waiting_for_vip_days)

    await message.answer(
        f"Enter duration in days for User ID <code>{target_id}</code> (e.g. <code>30</code>, <code>365</code>, or <code>0</code> for permanent):",
        reply_markup=cancel_action_keyboard("admin:menu"),
    )


@router.message(AdminState.waiting_for_vip_days)
async def process_vip_duration(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Please enter a number of days (e.g. 30).", reply_markup=cancel_action_keyboard("admin:menu"))
        return

    days = int(message.text.strip())
    duration = days if days > 0 else None
    data = await state.get_data()
    target_id = data["target_vip_user_id"]

    user = await crud.set_user_vip(session, target_id, is_vip=True, days=duration)
    await state.clear()

    if user:
        await message.answer(
            f"✅ <b>VIP Granted!</b>\nUser: <code>{target_id}</code>\nDuration: {f'{days} days' if days > 0 else 'Permanent'}",
            reply_markup=admin_panel_keyboard(),
        )
        # Notify the user
        u_lang = getattr(user, "language", "uz") or "uz"
        if u_lang == "uz":
            congrats = (
                "💎 <b>Tabriklaymiz! Sizga VIP tarif faollashtirildi!</b>\n\n"
                "• ✉ Lidlarga to'g'ridan-to'g'ri xabar (DM Rassilka)\n"
                "• 📥 Talabalar bazasini Excel/CSV formatida yuklash\n"
                "• ⚡ Cheksiz reklama almashinuvlari\n"
                "• 👑 Toza (belgisiz) postlar\n\n"
                "Barcha VIP imkoniyatlaridan foydalanishingiz mumkin!"
            )
        elif u_lang == "ru":
            congrats = (
                "💎 <b>Поздравляем! Вам активирован VIP статус!</b>\n\n"
                "• ✉ Рассылка прямо в личные сообщения учеников\n"
                "• 📥 Выгрузка базы лидов в Excel/CSV\n"
                "• ⚡ Безлимитный взаимопиар\n"
                "• 👑 Посты без водяных знаков\n\n"
                "Все функции VIP теперь доступны!"
            )
        else:
            congrats = (
                "💎 <b>Congratulations! VIP Status Activated!</b>\n\n"
                "• ✉ Direct DM Broadcasts to captured student leads\n"
                "• 📥 1-Click Excel/CSV student list export\n"
                "• ⚡ Unlimited Auto-VP swaps\n"
                "• 👑 100% Whitelabel clean promotional posts\n\n"
                "All VIP superpowers are now unlocked!"
            )
        try:
            from bot.keyboards.common import main_reply_keyboard
            reply_kb = main_reply_keyboard(lang=u_lang, is_vip=True, is_admin=config.is_admin(target_id))
            await message.bot.send_message(chat_id=target_id, text=congrats, reply_markup=reply_kb)
        except Exception:
            pass
    else:
        await message.answer(
            f"⚠️ User <code>{target_id}</code> has not started the bot yet, so they could not be updated in the database.",
            reply_markup=admin_panel_keyboard(),
        )


@router.callback_query(F.data == "admin:revoke_vip")
async def cb_admin_prompt_revoke_vip(
    callback: CallbackQuery,
) -> None:
    if not is_admin_filter(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🚫 Send <code>/revoke_vip &lt;user_id&gt;</code> to revoke VIP status from any user.",
        reply_markup=cancel_action_keyboard("admin:menu"),
    )
    await callback.answer()


@router.message(Command("grant_vip"))
async def cmd_quick_grant_vip(
    message: Message,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Usage: <code>/grant_vip &lt;user_id&gt; [days]</code>")
        return

    target_id = int(args[1])
    days = int(args[2]) if len(args) >= 3 and args[2].isdigit() else 30
    duration = days if days > 0 else None

    user = await crud.set_user_vip(session, target_id, is_vip=True, days=duration)
    if user:
        await message.answer(f"✅ VIP granted to <code>{target_id}</code> for {days} days.")
        u_lang = getattr(user, "language", "uz") or "uz"
        if u_lang == "uz":
            congrats = (
                "💎 <b>Tabriklaymiz! Sizga VIP tarif faollashtirildi!</b>\n\n"
                "• ✉ Lidlarga to'g'ridan-to'g'ri xabar (DM Rassilka)\n"
                "• 📥 Talabalar bazasini Excel/CSV formatida yuklash\n"
                "• ⚡ Cheksiz reklama almashinuvlari\n"
                "• 👑 Toza (belgisiz) postlar\n\n"
                "Barcha VIP imkoniyatlaridan foydalanishingiz mumkin!"
            )
        elif u_lang == "ru":
            congrats = (
                "💎 <b>Поздравляем! Вам активирован VIP статус!</b>\n\n"
                "• ✉ Рассылка прямо в личные сообщения учеников\n"
                "• 📥 Выгрузка базы лидов в Excel/CSV\n"
                "• ⚡ Безлимитный взаимопиар\n"
                "• 👑 Посты без водяных знаков\n\n"
                "Все функции VIP теперь доступны!"
            )
        else:
            congrats = (
                "💎 <b>Congratulations! VIP Status Activated!</b>\n\n"
                "• ✉ Direct DM Broadcasts to captured student leads\n"
                "• 📥 1-Click Excel/CSV student list export\n"
                "• ⚡ Unlimited Auto-VP swaps\n"
                "• 👑 100% Whitelabel clean promotional posts\n\n"
                "All VIP superpowers are now unlocked!"
            )
        try:
            from bot.keyboards.common import main_reply_keyboard
            reply_kb = main_reply_keyboard(lang=u_lang, is_vip=True, is_admin=config.is_admin(target_id))
            await message.bot.send_message(chat_id=target_id, text=congrats, reply_markup=reply_kb)
        except Exception:
            pass
    else:
        await message.answer(f"User <code>{target_id}</code> not found in database.")


@router.message(Command("revoke_vip"))
async def cmd_quick_revoke_vip(
    message: Message,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Usage: <code>/revoke_vip &lt;user_id&gt;</code>")
        return

    target_id = int(args[1])
    user = await crud.set_user_vip(session, target_id, is_vip=False)
    if user:
        await message.answer(f"🚫 VIP revoked from <code>{target_id}</code>.")
    else:
        await message.answer(f"User <code>{target_id}</code> not found in database.")


@router.message(Command("force_match"))
async def cmd_quick_force_match(
    message: Message,
    bot: Bot,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return
    matched = await swap_engine.run_matchmaking_cycle(bot, session)
    await message.answer(f"⚡ Matched {matched} swap deals.")


@router.message(Command("force_scan"))
async def cmd_quick_force_scan(
    message: Message,
    bot: Bot,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return
    scanned = await view_scanner.scan_active_deals_views(bot)
    await message.answer(f"👁 Scanned {scanned} active deals.")


@router.message(Command("force_cleanup"))
async def cmd_quick_force_cleanup(
    message: Message,
    bot: Bot,
    session: AsyncSession,
) -> None:
    if not is_admin_filter(message.from_user.id):
        return
    cleaned = await swap_engine.cleanup_stale_deals(bot, session, max_hours=config.deal_timeout_hours)
    await message.answer(f"🧹 Cleaned up {cleaned} stale deals.")
