import logging
import uuid
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import config
from bot.database import crud
from bot.database.models import Channel, Creative, SwapDeal, User
from bot.keyboards.channel_kb import VIEW_TIERS

logger = logging.getLogger(__name__)


def build_ad_markup(button_text: str, invite_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button_text, url=invite_link)]
        ]
    )


def format_ad_caption(creative: Creative, owner: User, bot_username: str) -> str:
    caption = creative.ad_text
    if not owner.is_vip_active:
        watermark = f"\n\n⚡ <i>Powered by @{bot_username} (Auto-VP Pool)</i>"
        caption = f"{caption}{watermark}"
    return caption


async def post_creative_to_channel(
    bot: Bot,
    channel_id: int,
    creative: Creative,
    owner: User,
    invite_link: str,
) -> Optional[int]:
    """Posts creative to target channel and returns the message_id."""
    bot_info = await bot.get_me()
    bot_username = bot_info.username or "EduSwapBot"
    caption = format_ad_caption(creative, owner, bot_username)
    markup = build_ad_markup(creative.button_text, invite_link)

    try:
        if creative.media_type == "photo" and creative.media_file_id:
            msg = await bot.send_photo(
                chat_id=channel_id,
                photo=creative.media_file_id,
                caption=caption,
                reply_markup=markup,
            )
        elif creative.media_type == "video" and creative.media_file_id:
            msg = await bot.send_video(
                chat_id=channel_id,
                video=creative.media_file_id,
                caption=caption,
                reply_markup=markup,
            )
        else:
            msg = await bot.send_message(
                chat_id=channel_id,
                text=caption,
                reply_markup=markup,
                disable_web_page_preview=True,
            )
        return msg.message_id
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.error(f"Failed to post ad to channel {channel_id}: {e}")
        return None


async def safe_delete_post(bot: Bot, channel_id: int, message_id: Optional[int]) -> bool:
    if not message_id:
        return True
    try:
        await bot.delete_message(chat_id=channel_id, message_id=message_id)
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.warning(f"Could not delete message {message_id} in channel {channel_id}: {e}")
        return False


async def publish_swap_deal(
    bot: Bot,
    session: AsyncSession,
    channel_a: Channel,
    channel_b: Channel,
    target_tier: int,
) -> Optional[SwapDeal]:
    """Sets up synchronized escrow swap between Channel A and Channel B based on target views."""
    deal_id = str(uuid.uuid4())
    logger.info(f"Publishing swap deal {deal_id} between {channel_a.title} and {channel_b.title} (Target: {target_tier} views)")

    # 1. Create unique Request-to-Join invite links
    try:
        link_a = await bot.create_chat_invite_link(
            chat_id=channel_a.telegram_id,
            creates_join_request=True,
            name=f"VP_{deal_id[:8]}_A",
        )
        link_b = await bot.create_chat_invite_link(
            chat_id=channel_b.telegram_id,
            creates_join_request=True,
            name=f"VP_{deal_id[:8]}_B",
        )
    except Exception as e:
        logger.error(f"Failed to create invite links for deal {deal_id}: {e}")
        return None

    # 2. Channel A's ad is published in Channel B
    msg_id_in_b = await post_creative_to_channel(
        bot=bot,
        channel_id=channel_b.telegram_id,
        creative=channel_a.creative,
        owner=channel_a.owner,
        invite_link=link_a.invite_link,
    )

    # 3. Channel B's ad is published in Channel A
    msg_id_in_a = await post_creative_to_channel(
        bot=bot,
        channel_id=channel_a.telegram_id,
        creative=channel_b.creative,
        owner=channel_b.owner,
        invite_link=link_b.invite_link,
    )

    if not msg_id_in_a or not msg_id_in_b:
        if msg_id_in_a:
            await safe_delete_post(bot, channel_a.telegram_id, msg_id_in_a)
        if msg_id_in_b:
            await safe_delete_post(bot, channel_b.telegram_id, msg_id_in_b)
        logger.error(f"Deal {deal_id} failed: could not publish simultaneously in both channels.")
        return None

    # 4. Save to Database
    deal = await crud.create_swap_deal(
        session=session,
        deal_id=deal_id,
        channel_a_id=channel_a.telegram_id,
        channel_b_id=channel_b.telegram_id,
        target_views=target_tier,
        invite_link_a=link_a.invite_link,
        invite_link_b=link_b.invite_link,
        post_msg_id_in_a=msg_id_in_a,
        post_msg_id_in_b=msg_id_in_b,
    )

    # 5. Increment weekly counters
    await crud.increment_user_swaps(session, channel_a.owner_id)
    await crud.increment_user_swaps(session, channel_b.owner_id)

    # 6. Notify both channel owners in DM
    # Notify both channel owners in their chosen language
    owner_a = await crud.get_user(session, channel_a.owner_id)
    lang_a = getattr(owner_a, "language", "uz") or "uz"
    owner_b = await crud.get_user(session, channel_b.owner_id)
    lang_b = getattr(owner_b, "language", "uz") or "uz"

    def make_launch_msg(my_ch_title: str, partner_ch_title: str, lang: str):
        if lang == "uz":
            txt = (
                f"⚡ <b>Auto-VP Reklama almashinuvi boshlandi!</b>\n\n"
                f"🎯 <b>Reja:</b> {target_tier} ta ko'rish 👀\n"
                f"📢 <b>Sherik kanal:</b> {partner_ch_title}\n\n"
                f"🟢 Sizning postingiz <b>{partner_ch_title}</b> kanaliga chiqdi!\n"
                f"🟢 Sherik posti <b>{my_ch_title}</b> kanaliga chiqdi!\n\n"
                f"👁 <i>Avtomatlashtirilgan ko'rishlar skaneri (@{config.scanner_username}) postni har 45 soniyada tekshiradi. {target_tier} ko'rish to'plangach, post avtomatik o'chiriladi.</i>"
            )
            btn_status = "📊 Jonli holat"
            btn_cancel = "🛑 To'xtatish"
        elif lang == "ru":
            txt = (
                f"⚡ <b>Авто-ВП Взаимопиар запущен!</b>\n\n"
                f"🎯 <b>Цель:</b> {target_tier} просмотров 👀\n"
                f"📢 <b>Партнер:</b> {partner_ch_title}\n\n"
                f"🟢 Ваш пост опубликован в канале <b>{partner_ch_title}</b>!\n"
                f"🟢 Пост партнера опубликован в вашем канале <b>{my_ch_title}</b>!\n\n"
                f"👁 <i>Сканнер (@{config.scanner_username}) отслеживает просмотры каждые 45 сек. Пост будет автоматически удален по достижении {target_tier} просмотров.</i>"
            )
            btn_status = "📊 Статус сделки"
            btn_cancel = "🛑 Прервать сделку"
        else:
            txt = (
                f"⚡ <b>Auto-VP Swap Launched!</b>\n\n"
                f"🎯 <b>Target Views:</b> {target_tier} views 👀\n"
                f"📢 <b>Your Partner:</b> {partner_ch_title}\n\n"
                f"🟢 Your ad is LIVE in <b>{partner_ch_title}</b>!\n"
                f"🟢 Partner's ad is LIVE in <b>{my_ch_title}</b>!\n\n"
                f"👁 <i>Our automated eye-scanner (@{config.scanner_username}) tracks views every 45s. Post auto-deletes on {target_tier} views.</i>"
            )
            btn_status = "📊 View Live Status"
            btn_cancel = "🛑 Emergency Cancel"

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=btn_status, callback_data=f"deal:view:{deal_id}")],
                [InlineKeyboardButton(text=btn_cancel, callback_data=f"deal:cancel_confirm:{deal_id}")],
            ]
        )
        return txt, markup

    text_for_a, markup_a = make_launch_msg(channel_a.title, channel_b.title, lang_a)
    text_for_b, markup_b = make_launch_msg(channel_b.title, channel_a.title, lang_b)

    try:
        await bot.send_message(chat_id=channel_a.owner_id, text=text_for_a, reply_markup=markup_a)
    except Exception as e:
        logger.warning(f"Could not notify owner A {channel_a.owner_id}: {e}")

    try:
        await bot.send_message(chat_id=channel_b.owner_id, text=text_for_b, reply_markup=markup_b)
    except Exception as e:
        logger.warning(f"Could not notify owner B {channel_b.owner_id}: {e}")

    return deal


async def cancel_deal(
    bot: Bot,
    session: AsyncSession,
    deal_id: str,
    cancelled_by_user_id: int,
) -> bool:
    deal = await crud.get_deal_by_id(session, deal_id)
    if not deal or deal.status != "ACTIVE":
        return False

    if not deal.post_a_deleted:
        await safe_delete_post(bot, deal.channel_a_id, deal.post_msg_id_in_a)
    if not deal.post_b_deleted:
        await safe_delete_post(bot, deal.channel_b_id, deal.post_msg_id_in_b)

    await crud.complete_or_close_deal(session, deal_id, "CANCELLED")

    for owner_id in [deal.channel_a.owner_id, deal.channel_b.owner_id]:
        user_obj = await crud.get_user(session, owner_id)
        u_lang = getattr(user_obj, "language", "uz") or "uz"
        if u_lang == "uz":
            notification = (
                f"🛑 <b>Auto-VP Bitim #{deal.id[:8]} to'xtatildi</b>\n\n"
                f"Kanal egalaridan biri bitimni bekor qildi.\n"
                f"Barcha reklama postlari kanallardan darhol o'chirildi."
            )
        elif u_lang == "ru":
            notification = (
                f"🛑 <b>Авто-ВП Сделка #{deal.id[:8]} отменена</b>\n\n"
                f"Один из владельцев каналов прервал сделку.\n"
                f"Все рекламные посты были немедленно удалены из каналов."
            )
        else:
            notification = (
                f"🛑 <b>Auto-VP Deal #{deal.id[:8]} Cancelled</b>\n\n"
                f"One of the channel owners cancelled the swap.\n"
                f"All remaining ad posts have been deleted immediately."
            )
        try:
            await bot.send_message(chat_id=owner_id, text=notification)
        except Exception:
            pass
    return True


async def cleanup_stale_deals(
    bot: Bot,
    session: AsyncSession,
    max_hours: int = 24,
) -> int:
    """Finds deals older than max_hours, deletes remaining posts, and marks them EXPIRED."""
    stale_deals = await crud.get_stale_active_deals(session, max_hours=max_hours)
    cleaned_count = 0

    for deal in stale_deals:
        logger.info(f"Cleaning up stale deal {deal.id} (> {max_hours}h old)")
        if not deal.post_a_deleted:
            await safe_delete_post(bot, deal.channel_a_id, deal.post_msg_id_in_a)
        if not deal.post_b_deleted:
            await safe_delete_post(bot, deal.channel_b_id, deal.post_msg_id_in_b)

        await crud.complete_or_close_deal(session, deal.id, "EXPIRED")
        cleaned_count += 1

        for owner_id in [deal.channel_a.owner_id, deal.channel_b.owner_id]:
            user_obj = await crud.get_user(session, owner_id)
            u_lang = getattr(user_obj, "language", "uz") or "uz"
            if u_lang == "uz":
                expired_msg = (
                    f"⏱ <b>Auto-VP Bitim #{deal.id[:8]} yakunlandi (24 soatlik muddat)</b>\n\n"
                    f"24 soatlik muddat tugadi. Postlar kanallardan toza o'chirildi.\n"
                    f"• <b>{deal.channel_a.title}:</b> {deal.views_a_received}/{deal.target_views} ko'rish 👀\n"
                    f"• <b>{deal.channel_b.title}:</b> {deal.views_b_received}/{deal.target_views} ko'rish 👀"
                )
            elif u_lang == "ru":
                expired_msg = (
                    f"⏱ <b>Авто-ВП Сделка #{deal.id[:8]} завершена (24ч истекли)</b>\n\n"
                    f"24-часовой период обмена подошел к концу. Посты автоматически удалены.\n"
                    f"• <b>{deal.channel_a.title}:</b> {deal.views_a_received}/{deal.target_views} просмотров 👀\n"
                    f"• <b>{deal.channel_b.title}:</b> {deal.views_b_received}/{deal.target_views} просмотров 👀"
                )
            else:
                expired_msg = (
                    f"⏱ <b>Auto-VP Deal #{deal.id[:8]} Concluded (24h Window Reached)</b>\n\n"
                    f"The 24-hour exchange window has ended.\n"
                    f"• <b>{deal.channel_a.title}:</b> {deal.views_a_received}/{deal.target_views} views 👀\n"
                    f"• <b>{deal.channel_b.title}:</b> {deal.views_b_received}/{deal.target_views} views 👀"
                )
            try:
                await bot.send_message(chat_id=owner_id, text=expired_msg)
            except Exception:
                pass

    return cleaned_count


async def run_matchmaking_cycle(bot: Bot, session: AsyncSession) -> int:
    """Iterates through all view tiers and matches eligible channels."""
    matched_pairs = 0

    for tier in VIEW_TIERS:
        channels = await crud.get_eligible_pool_channels(session, tier)
        eligible = []
        for ch in channels:
            if not ch.owner.is_vip_active and ch.owner.swaps_this_week >= config.free_weekly_swap_limit:
                continue
            eligible.append(ch)

        used_ids = set()
        for i in range(len(eligible)):
            ch_a = eligible[i]
            if ch_a.telegram_id in used_ids:
                continue

            for j in range(i + 1, len(eligible)):
                ch_b = eligible[j]
                if ch_b.telegram_id in used_ids:
                    continue

                if ch_a.owner_id == ch_b.owner_id:
                    continue

                has_swapped = await crud.has_recent_deal_between_channels(
                    session=session,
                    channel_a_id=ch_a.telegram_id,
                    channel_b_id=ch_b.telegram_id,
                    days=config.swap_cooldown_days,
                )
                if has_swapped:
                    continue

                deal = await publish_swap_deal(
                    bot=bot,
                    session=session,
                    channel_a=ch_a,
                    channel_b=ch_b,
                    target_tier=tier,
                )
                if deal:
                    used_ids.add(ch_a.telegram_id)
                    used_ids.add(ch_b.telegram_id)
                    matched_pairs += 1
                    break

    return matched_pairs
