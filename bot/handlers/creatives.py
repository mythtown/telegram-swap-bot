from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud
from bot.database.models import User
from bot.keyboards.common import cancel_action_keyboard
from bot.keyboards.creative_kb import skip_step_keyboard
from bot.locales.texts import t
from bot.services import swap_engine
from bot.states.states import CreativeState

router = Router(name="creatives_router")


@router.callback_query(F.data.startswith("creative:edit:"))
async def cb_start_creative_edit(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channel_id = int(callback.data.split(":")[2])
    channel = await crud.get_channel(session, channel_id)
    if not channel:
        await callback.answer(t("channel_not_found", lang), show_alert=True)
        return

    await state.clear()
    await state.update_data(channel_id=channel_id)
    await state.set_state(CreativeState.waiting_for_ad_content)

    text = t("step_ad_content", lang)
    await callback.message.edit_text(text, reply_markup=cancel_action_keyboard(lang=lang, return_to=f"channel:view:{channel_id}"))
    await callback.answer()


@router.message(CreativeState.waiting_for_ad_content)
async def process_ad_content(
    message: Message,
    state: FSMContext,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    data = await state.get_data()
    channel_id = data["channel_id"]

    media_type = "text"
    media_file_id = None
    ad_text = ""

    if message.photo:
        media_type = "photo"
        media_file_id = message.photo[-1].file_id
        ad_text = message.html_text or ""
    elif message.video:
        media_type = "video"
        media_file_id = message.video.file_id
        ad_text = message.html_text or ""
    elif message.text:
        media_type = "text"
        ad_text = message.html_text or message.text
    else:
        err = "⚠️ Iltimos, matn, rasm yoki video yuboring." if lang == "uz" else (
            "⚠️ Пожалуйста, отправьте текст, фото или видео." if lang == "ru" else "⚠️ Please send text, photo, or video."
        )
        await message.answer(err, reply_markup=cancel_action_keyboard(lang=lang, return_to=f"channel:view:{channel_id}"))
        return

    if not ad_text.strip():
        err = "⚠️ Post matni bo'sh bo'lishi mumkin emas!" if lang == "uz" else (
            "⚠️ Текст рекламного поста не может быть пустым!" if lang == "ru" else "⚠️ Ad text cannot be empty!"
        )
        await message.answer(err, reply_markup=cancel_action_keyboard(lang=lang, return_to=f"channel:view:{channel_id}"))
        return

    await state.update_data(
        media_type=media_type,
        media_file_id=media_file_id,
        ad_text=ad_text,
    )
    await state.set_state(CreativeState.waiting_for_button_text)

    prompt = t("step_button_text", lang)
    markup = skip_step_keyboard(
        skip_callback="creative:skip_button_text",
        cancel_callback=f"channel:view:{channel_id}",
        lang=lang,
    )
    await message.answer(prompt, reply_markup=markup)


@router.callback_query(F.data == "creative:skip_button_text", CreativeState.waiting_for_button_text)
async def cb_skip_button_text(
    callback: CallbackQuery,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    default_btn = "🎁 Bepul sovg'ani olish" if lang == "uz" else ("🎁 Забрать подарок" if lang == "ru" else "🎁 Claim Free Gift & Join")
    await state.update_data(button_text=default_btn)
    await prompt_gift_upload(callback.message, state, lang=lang, is_edit=True)
    await callback.answer()


@router.message(CreativeState.waiting_for_button_text)
async def process_button_text(
    message: Message,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    default_btn = "🎁 Bepul sovg'ani olish" if lang == "uz" else ("🎁 Забрать подарок" if lang == "ru" else "🎁 Claim Free Gift & Join")
    btn_text = message.text.strip() if message.text else default_btn
    if len(btn_text) > 40:
        btn_text = btn_text[:40]

    await state.update_data(button_text=btn_text)
    await prompt_gift_upload(message, state, lang=lang, is_edit=False)


async def prompt_gift_upload(message: Message, state: FSMContext, lang: str = "uz", is_edit: bool = False) -> None:
    data = await state.get_data()
    channel_id = data["channel_id"]
    await state.set_state(CreativeState.waiting_for_gift_content)

    prompt = t("step_gift_file", lang)
    markup = cancel_action_keyboard(lang=lang, return_to=f"channel:view:{channel_id}")
    if is_edit:
        try:
            await message.edit_text(prompt, reply_markup=markup)
            return
        except Exception:
            pass
    await message.answer(prompt, reply_markup=markup)


@router.message(CreativeState.waiting_for_gift_content)
async def process_gift_content(
    message: Message,
    state: FSMContext,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    gift_type = "document"
    gift_file_id = None
    gift_name = "Study Materials"
    gift_text_content = None

    if message.document:
        gift_type = "document"
        gift_file_id = message.document.file_id
        gift_name = message.document.file_name or "materials.pdf"
    elif message.video:
        gift_type = "video"
        gift_file_id = message.video.file_id
        gift_name = "Video Lesson"
    elif message.audio:
        gift_type = "audio"
        gift_file_id = message.audio.file_id
        gift_name = message.audio.file_name or "Audio Lesson"
    elif message.photo:
        gift_type = "photo"
        gift_file_id = message.photo[-1].file_id
        gift_name = "CheatSheet Image"
    elif message.text:
        gift_type = "text"
        gift_text_content = message.text
        gift_name = "Study Resource Link"
    else:
        err = "⚠️ Iltimos, fayl, rasm, video yoki havola yuboring." if lang == "uz" else (
            "⚠️ Отправьте файл, фото, видео или ссылку." if lang == "ru" else "⚠️ Please send file, photo, video, or link."
        )
        await message.answer(err)
        return

    await state.update_data(
        gift_type=gift_type,
        gift_file_id=gift_file_id,
        gift_name=gift_name,
        gift_text_content=gift_text_content,
    )
    await state.set_state(CreativeState.waiting_for_gift_title)

    data = await state.get_data()
    channel_id = data["channel_id"]

    prompt = t("step_gift_title", lang)
    markup = skip_step_keyboard(
        skip_callback="creative:skip_gift_title",
        cancel_callback=f"channel:view:{channel_id}",
        lang=lang,
    )
    await message.answer(prompt, reply_markup=markup)


@router.callback_query(F.data == "creative:skip_gift_title", CreativeState.waiting_for_gift_title)
async def cb_skip_gift_title(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    data = await state.get_data()
    default_title = "Maxsus o'quv qo'llanma" if lang == "uz" else ("Полезные материалы" if lang == "ru" else "Exclusive Study Pack")
    gift_title = data.get("gift_name") or default_title
    await finish_creative_setup(
        session=session,
        state=state,
        target_message=callback.message,
        gift_title=gift_title,
        lang=lang,
    )
    await callback.answer()


@router.message(CreativeState.waiting_for_gift_title)
async def process_gift_title(
    message: Message,
    session: AsyncSession,
    current_user: User,
    state: FSMContext,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    default_title = "Maxsus o'quv qo'llanma" if lang == "uz" else ("Полезные материалы" if lang == "ru" else "Exclusive Study Pack")
    gift_title = message.text.strip() if message.text else default_title
    await finish_creative_setup(
        session=session,
        state=state,
        target_message=message,
        gift_title=gift_title,
        lang=lang,
    )


async def finish_creative_setup(
    session: AsyncSession,
    state: FSMContext,
    target_message: Message,
    gift_title: str,
    lang: str = "uz",
) -> None:
    data = await state.get_data()
    channel_id = data["channel_id"]
    default_btn = "🎁 Bepul sovg'ani olish" if lang == "uz" else ("🎁 Забрать подарок" if lang == "ru" else "🎁 Claim Free Gift & Join")

    await crud.save_or_update_creative(
        session=session,
        channel_id=channel_id,
        ad_text=data["ad_text"],
        media_type=data["media_type"],
        media_file_id=data.get("media_file_id"),
        button_text=data.get("button_text", default_btn),
        gift_type=data.get("gift_type", "document"),
        gift_file_id=data.get("gift_file_id"),
        gift_name=data.get("gift_name"),
        gift_text_content=data.get("gift_text_content"),
        gift_title=gift_title,
    )
    await state.clear()

    channel = await crud.get_channel(session, channel_id)
    if lang == "uz":
        success_text = f"✅ <b>Post va Bepul sovg'a saqlandi!</b>\n\n📢 <b>Kanal:</b> {channel.title}\n🔘 <b>Tugma:</b> {data.get('button_text')}\n🎁 <b>Sovg'a:</b> {gift_title}\n\n<i>Kanal o'zaro reklama (Auto-VP) uchun tayyor!</i>"
        btn_preview = "👁 Postni ko'rish (Test)"
        btn_channel = "📢 Kanal sozlamalari"
    elif lang == "ru":
        success_text = f"✅ <b>Пост и подарок успешно сохранены!</b>\n\n📢 <b>Канал:</b> {channel.title}\n🔘 <b>Кнопка:</b> {data.get('button_text')}\n🎁 <b>Подарок:</b> {gift_title}\n\n<i>Канал готов к взаимопиару в пуле!</i>"
        btn_preview = "👁 Предпросмотр поста"
        btn_channel = "📢 Настройки канала"
    else:
        success_text = f"✅ <b>Ad post & free gift saved!</b>\n\n📢 <b>Channel:</b> {channel.title}\n🔘 <b>Button:</b> {data.get('button_text')}\n🎁 <b>Gift:</b> {gift_title}\n\n<i>Channel is ready for Auto-VP matchmaking!</i>"
        btn_preview = "👁 Preview Ad Post"
        btn_channel = "📢 Channel Settings"

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_preview, callback_data=f"creative:preview:{channel_id}")],
            [InlineKeyboardButton(text=btn_channel, callback_data=f"channel:view:{channel_id}")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
        ]
    )
    if hasattr(target_message, "edit_text"):
        try:
            await target_message.edit_text(success_text, reply_markup=markup)
            return
        except Exception:
            pass
    await target_message.answer(success_text, reply_markup=markup)


@router.callback_query(F.data.startswith("creative:preview:"))
async def cb_preview_creative(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    channel_id = int(callback.data.split(":")[2])
    channel = await crud.get_channel(session, channel_id)
    if not channel or not channel.creative:
        await callback.answer(t("channel_not_found", lang), show_alert=True)
        return

    creative = channel.creative
    bot_info = await bot.get_me()
    bot_username = bot_info.username or "EduSwapBot"
    caption = swap_engine.format_ad_caption(creative, current_user, bot_username)
    markup = swap_engine.build_ad_markup(creative.button_text, f"https://t.me/{bot_username}")

    header = t("preview_ad_header", lang)
    await callback.message.answer(header)

    if creative.media_type == "photo" and creative.media_file_id:
        await callback.message.answer_photo(
            photo=creative.media_file_id,
            caption=caption,
            reply_markup=markup,
        )
    elif creative.media_type == "video" and creative.media_file_id:
        await callback.message.answer_video(
            video=creative.media_file_id,
            caption=caption,
            reply_markup=markup,
        )
    else:
        await callback.message.answer(
            text=caption,
            reply_markup=markup,
            disable_web_page_preview=True,
        )

    gift_preview_txt = t("preview_gift_label", lang, title=creative.gift_title)
    btn_edit = "✏️ " + ("Tahrirlash" if lang == "uz" else ("Изменить" if lang == "ru" else "Edit"))
    btn_back_ch = "📢 " + ("Kanalga qaytish" if lang == "uz" else ("Назад в канал" if lang == "ru" else "Back to Channel"))

    await callback.message.answer(
        gift_preview_txt,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=btn_edit, callback_data=f"creative:edit:{channel_id}")],
                [InlineKeyboardButton(text=btn_back_ch, callback_data=f"channel:view:{channel_id}")],
                [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
            ]
        ),
    )
    await callback.answer()
