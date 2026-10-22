from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud
from bot.database.models import User
from bot.keyboards.broadcast_kb import (
    broadcast_channel_picker_keyboard,
    broadcast_confirm_keyboard,
)
from bot.keyboards.common import back_to_main_keyboard, cancel_action_keyboard
from bot.locales.texts import t
from bot.services import broadcast_engine
from bot.states.states import BroadcastState

router = Router(name="broadcast_router")


async def render_broadcast_prompt(session: AsyncSession, current_user: User, lang: str):
    if not current_user.is_vip_active:
        if lang == "uz":
            text = (
                "💎 <b>VIP Imkoniyat: Lidlarga xabar (DM Rassilka)</b>\n\n"
                "Talabalarning shaxsiy xabarlariga to'g'ridan-to'g'ri o'quv kursi yoki takliflaringizni yuborish.\n\n"
                "• 80%+ o'qilish darajasi\n"
                "• Anti-flood xavfsiz tezlik\n\n"
                "<i>VIP tarifga ulanish uchun administratorga yozing.</i>"
            )
        elif lang == "ru":
            text = (
                "💎 <b>VIP Возможность: Рассылка в ЛС лидам</b>\n\n"
                "Отправка предложений прямо в личные сообщения учеников из вашей CRM.\n\n"
                "• Открываемость 80%+\n"
                "• Защита от спам-блокировок\n\n"
                "<i>Для подключения обратитесь к администратору.</i>"
            )
        else:
            text = (
                "💎 <b>VIP Feature: Direct DM Broadcast to Leads</b>\n\n"
                "Deliver course offers and promotions directly into students' private messages.\n\n"
                "• 80%+ open rate\n"
                "• Built-in anti-flood rate limits\n\n"
                "<i>Upgrade to VIP to unlock unlimited DM broadcasts.</i>"
            )
        return text, back_to_main_keyboard(lang=lang), False

    all_leads_count = await crud.get_student_leads_count(session, current_user.telegram_id)
    if all_leads_count == 0:
        return t("no_leads_yet", lang), back_to_main_keyboard(lang=lang), False

    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)
    text = t("broadcast_title", lang)
    markup = broadcast_channel_picker_keyboard(channels, all_leads_count, lang=lang)
    return text, markup, True


@router.callback_query(F.data == "menu:broadcast")
async def cb_start_broadcast(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    await state.clear()
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup, _ = await render_broadcast_prompt(session, current_user, lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.message(F.text.in_(["✉ Xabar tarqatish", "✉ Рассылка", "✉ Broadcast"]))
async def msg_start_broadcast(
    message: Message,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    await state.clear()
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup, _ = await render_broadcast_prompt(session, current_user, lang)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("broadcast:target:"))
async def cb_select_target(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    target_str = callback.data.split(":")[2]
    channel_id = None if target_str == "all" else int(target_str)

    leads_count = await crud.get_student_leads_count(
        session, current_user.telegram_id, channel_id=channel_id
    )

    await state.update_data(target_channel_id=channel_id, target_count=leads_count)
    await state.set_state(BroadcastState.waiting_for_message)

    if lang == "uz":
        text = f"📝 <b>Xabarni yuboring</b>\n\n🎯 Auditoriya: <b>{leads_count}</b> ta o'quvchi\n\nYubormoqchi bo'lgan xabaringizni yozing (matn, rasm yoki video):"
    elif lang == "ru":
        text = f"📝 <b>Создание рассылки</b>\n\n🎯 Получателей: <b>{leads_count}</b> учеников\n\nОтправьте сообщение (текст, фото или видео):"
    else:
        text = f"📝 <b>Compose Broadcast</b>\n\n🎯 Audience: <b>{leads_count}</b> students\n\nSend your message now (text, photo, or video):"

    await callback.message.edit_text(text, reply_markup=cancel_action_keyboard(lang=lang, return_to="menu:broadcast"))
    await callback.answer()


@router.message(BroadcastState.waiting_for_message)
async def process_broadcast_message(
    message: Message,
    state: FSMContext,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    data = await state.get_data()
    target_count = data.get("target_count", 0)

    await state.update_data(broadcast_message_id=message.message_id, broadcast_chat_id=message.chat.id)
    await state.set_state(BroadcastState.confirming)

    if lang == "uz":
        prompt = f"⚠️ <b>Yuborishni tasdiqlang</b>\n\n🎯 Qabul qiluvchilar: <b>{target_count}</b> ta talaba\n\nXabar xavfsiz oraliq bilan yuboriladi. Boshlaysizmi?"
    elif lang == "ru":
        prompt = f"⚠️ <b>Подтверждение отправки</b>\n\n🎯 Получателей: <b>{target_count}</b> учеников\n\nСообщения отправляются с защитой от спама. Начать?"
    else:
        prompt = f"⚠️ <b>Confirm Broadcast Launch</b>\n\n🎯 Target Audience: <b>{target_count}</b> students\n\nMessages will be paced safely to prevent flooding. Ready to send?"

    await message.answer(prompt, reply_markup=broadcast_confirm_keyboard(lang=lang))


@router.callback_query(F.data == "broadcast:confirm_send", BroadcastState.confirming)
async def cb_execute_broadcast(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    data = await state.get_data()
    channel_id = data.get("target_channel_id")
    msg_id = data.get("broadcast_message_id")

    in_progress_txt = (
        "🚀 <b>Xabarlar yuborilmoqda...</b>\nIltimos, kuting." if lang == "uz" else (
            "🚀 <b>Рассылка запущена...</b>\nПожалуйста, подождите." if lang == "ru" else (
                "🚀 <b>Broadcasting in progress...</b>\nPlease wait."
            )
        )
    )
    await callback.message.edit_text(in_progress_txt)

    class MessageStub:
        async def copy_to(self, chat_id: int):
            return await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=callback.message.chat.id,
                message_id=msg_id,
            )

    source_stub = MessageStub()

    report = await broadcast_engine.send_dm_broadcast(
        bot=bot,
        session=session,
        owner_id=current_user.telegram_id,
        channel_id=channel_id,
        source_message=source_stub,
    )
    await state.clear()

    if lang == "uz":
        report_text = f"📊 <b>Xabarlar yetkazildi!</b>\n\n🎯 Jami: {report['total']}\n✅ Yetkazildi: {report['sent']}\n❌ Yetib bormadi (bloklangan): {report['failed']}"
    elif lang == "ru":
        report_text = f"📊 <b>Рассылка завершена!</b>\n\n🎯 Всего: {report['total']}\n✅ Доставлено: {report['sent']}\n❌ Ошибок (бот заблокирован): {report['failed']}"
    else:
        report_text = f"📊 <b>Broadcast Completed!</b>\n\n🎯 Total: {report['total']}\n✅ Delivered: {report['sent']}\n❌ Failed/Blocked: {report['failed']}"

    await callback.message.answer(report_text, reply_markup=back_to_main_keyboard(lang=lang))
    await callback.answer()
