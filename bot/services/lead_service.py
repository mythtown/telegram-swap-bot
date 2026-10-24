import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud
from bot.database.models import Channel, SwapDeal
from bot.keyboards.lead_kb import student_claim_gift_keyboard

logger = logging.getLogger(__name__)


async def handle_student_join_request(
    bot: Bot,
    event: ChatJoinRequest,
    session: AsyncSession,
) -> None:
    student = event.from_user
    target_channel_id = event.chat.id
    invite_link = event.invite_link

    logger.info(
        f"Incoming join request: Student {student.id} (@{student.username}) for channel {target_channel_id}"
    )

    deal_match = None
    side = None
    if invite_link and invite_link.invite_link:
        deal_match = await crud.get_active_deal_by_invite_link(
            session=session,
            invite_link_url=invite_link.invite_link,
        )

    channel: Optional[Channel] = None
    deal: Optional[SwapDeal] = None

    if deal_match:
        deal, side = deal_match
        channel = deal.channel_a if side == "A" else deal.channel_b

        is_first_time = await crud.record_swap_lead_if_new(
            session=session,
            swap_id=deal.id,
            channel_id=channel.telegram_id,
            student_telegram_id=student.id,
        )

        if is_first_time:
            logger.info(f"Anti-Cheat passed! Recording student lead for Deal {deal.id}, side {side}")
            if side == "A":
                deal.joins_a_received += 1
            else:
                deal.joins_b_received += 1
            await session.commit()
    else:
        channel = await crud.get_channel(session, target_channel_id)

    if not channel:
        logger.info(f"Channel {target_channel_id} is not registered in our system. Leaving request pending.")
        return

    creative = channel.creative
    gift_title = creative.gift_title if creative else "Exclusive Study Materials"
    deal_id_str = deal.id if deal else "direct"

    # Save initial student lead record in CRM
    await crud.save_student_lead(
        session=session,
        owner_id=channel.owner_id,
        channel_id=channel.telegram_id,
        student_telegram_id=student.id,
        student_username=student.username,
        student_name=student.full_name or "Student",
        pdf_sent=False,
    )

    code = getattr(student, "language_code", "uz") or "uz"
    if code.startswith("ru"):
        s_lang = "ru"
    elif code.startswith("en"):
        s_lang = "en"
    else:
        s_lang = "uz"

    # Attempt to DM student their gift
    if s_lang == "uz":
        dm_text = (
            f"👋 <b>{channel.title}</b>\n\n"
            f"Kanalga a'zo bo'lish so'rovingiz qabul qilindi.\n"
            f"🎁 <b>Bepul sovg'angiz:</b> {gift_title}\n\n"
            f"Sovg'ani olish va kanalga kirish uchun tugmani bosing:"
        )
    elif s_lang == "ru":
        dm_text = (
            f"👋 <b>{channel.title}</b>\n\n"
            f"Ваша заявка на вступление принята.\n"
            f"🎁 <b>Бесплатный подарок:</b> {gift_title}\n\n"
            f"Нажмите кнопку ниже, чтобы забрать подарок и войти в канал:"
        )
    else:
        dm_text = (
            f"👋 <b>{channel.title}</b>\n\n"
            f"Your request to join has been accepted.\n"
            f"🎁 <b>Free Gift:</b> {gift_title}\n\n"
            f"Tap the button below to claim your gift and enter the channel:"
        )
    markup = student_claim_gift_keyboard(deal_id=deal_id_str, channel_id=channel.telegram_id, lang=s_lang)

    try:
        await bot.send_message(
            chat_id=student.id,
            text=dm_text,
            reply_markup=markup,
        )
        logger.info(f"Sent DM lead magnet prompt to student {student.id}")
    except (TelegramForbiddenError, TelegramBadRequest) as e:
        logger.warning(
            f"Cannot DM student {student.id} (user has not started bot: {e}). Request remains pending for admin review."
        )


async def confirm_and_deliver_gift(
    bot: Bot,
    session: AsyncSession,
    student_id: int,
    deal_id_str: str,
    channel_id: int,
    student_name: str = "Student",
    student_username: Optional[str] = None,
) -> bool:
    """Delivers the gift (PDF, ZIP, DOCX, Video, Photo, or Text/Link), approves access, and updates CRM."""
    channel = await crud.get_channel(session, channel_id)
    if not channel:
        return False

    creative = channel.creative
    gift_title = creative.gift_title if creative else "Exclusive Study Materials"

    # 1. Note: Join request is intentionally left PENDING for channel admin to approve manually!
    logger.info(f"Student {student_id} claimed gift. Join request kept pending in channel {channel_id}.")

    # Build channel button
    channel_btn = None
    if channel.username:
        channel_btn = InlineKeyboardButton(text=f"📢 Open {channel.title}", url=f"https://t.me/{channel.username}")
    elif channel.invite_link:
        channel_btn = InlineKeyboardButton(text=f"📢 Open {channel.title}", url=channel.invite_link)

    lead_markup = InlineKeyboardMarkup(inline_keyboard=[[channel_btn]]) if channel_btn else None

    # 2. Deliver the Free Gift based on its format
    gift_delivered = False
    db_user = await crud.get_user(session, student_id)
    s_lang = db_user.language if (db_user and db_user.language) else "uz"
    if s_lang == "uz":
        caption = f"🎁 <b>{gift_title}</b>\n\n✅ Sovg'angiz yetkazildi! <b>{channel.title}</b> kanaliga a'zolik so'rovingiz admin tomonidan ko'rib chiqiladi."
    elif s_lang == "ru":
        caption = f"🎁 <b>{gift_title}</b>\n\n✅ Подарок доставлен! Ваша заявка в канал <b>{channel.title}</b> будет рассмотрена администратором."
    else:
        caption = f"🎁 <b>{gift_title}</b>\n\n✅ Gift delivered! Your request to join <b>{channel.title}</b> will be reviewed by the admin."

    if creative:
        g_type = creative.gift_type
        f_id = creative.gift_file_id
        t_content = creative.gift_text_content

        try:
            if g_type == "document" and f_id:
                await bot.send_document(chat_id=student_id, document=f_id, caption=caption, reply_markup=lead_markup)
                gift_delivered = True
            elif g_type == "video" and f_id:
                await bot.send_video(chat_id=student_id, video=f_id, caption=caption, reply_markup=lead_markup)
                gift_delivered = True
            elif g_type == "photo" and f_id:
                await bot.send_photo(chat_id=student_id, photo=f_id, caption=caption, reply_markup=lead_markup)
                gift_delivered = True
            elif g_type == "audio" and f_id:
                await bot.send_audio(chat_id=student_id, audio=f_id, caption=caption, reply_markup=lead_markup)
                gift_delivered = True
            elif g_type == "text" and t_content:
                text_msg = f"{caption}\n\n🔗 <b>Access Details / Link:</b>\n{t_content}"
                await bot.send_message(chat_id=student_id, text=text_msg, reply_markup=lead_markup)
                gift_delivered = True
            elif f_id:
                await bot.send_document(chat_id=student_id, document=f_id, caption=caption, reply_markup=lead_markup)
                gift_delivered = True
        except Exception as e:
            logger.error(f"Failed to deliver gift to student {student_id}: {e}")

    if not gift_delivered:
        try:
            await bot.send_message(
                chat_id=student_id,
                text=(
                    f"✅ <b>Request Approved!</b>\n\n"
                    f"Welcome to <b>{channel.title}</b>. Your join request is confirmed!"
                ),
                reply_markup=lead_markup,
            )
        except Exception:
            pass

    # 3. Update database lead record
    await crud.save_student_lead(
        session=session,
        owner_id=channel.owner_id,
        channel_id=channel.telegram_id,
        student_telegram_id=student_id,
        student_username=student_username,
        student_name=student_name,
        pdf_sent=gift_delivered,
    )

    # 4. Notify teacher of new lead capture
    try:
        user_mention = f"@{student_username}" if student_username else student_name
        teacher_msg = (
            f"🎯 <b>New Student Lead Captured!</b>\n\n"
            f"👤 <b>Student:</b> {user_mention} (ID: <code>{student_id}</code>)\n"
            f"📢 <b>Channel:</b> {channel.title}\n"
            f"🎁 <b>Gift Delivered:</b> {'Yes ✅' if gift_delivered else 'None'}\n\n"
            f"<i>This student is now permanently saved in your Student Leads CRM for future DM broadcasts.</i>"
        )
        await bot.send_message(chat_id=channel.owner_id, text=teacher_msg)
    except Exception as e:
        logger.warning(f"Could not send lead alert to teacher {channel.owner_id}: {e}")

    return True
