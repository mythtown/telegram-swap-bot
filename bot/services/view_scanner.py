import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError
from bot.config import config
from bot.database import crud
from bot.database.models import SwapDeal
from bot.database.session import async_session_factory
from bot.services import swap_engine

logger = logging.getLogger(__name__)

_scanner_client: Optional[TelegramClient] = None


def make_earned_msg(my_views: int, target_views: int, leads: int, partner_title: str, lang: str):
    if lang == "uz":
        text = (
            f"🎉 <b>Reja bajarildi!</b>\n\n"
            f"🏆 <b>SIZ NIMA OLDINGIZ:</b>\n"
            f"👁 <b>Yetkazilgan ko'rishlar:</b> {my_views}/{target_views} ta ✅\n"
            f"👥 <b>Yangi talabalar (CRM):</b> {leads} ta o'quvchi\n"
            f"📢 <b>Sherik:</b> {partner_title}\n\n"
            f"<i>{partner_title} kanalidagi reklamangiz avtomatik o'chirildi!</i>"
        )
        b_leads = "👥 Yig'ilgan lidlar"
        b_menu = "🏠 Asosiy menyu"
    elif lang == "ru":
        text = (
            f"🎉 <b>Цель по просмотрам достигнута!</b>\n\n"
            f"🏆 <b>ЧТО ВЫ ПОЛУЧИЛИ:</b>\n"
            f"👁 <b>Просмотров получено:</b> {my_views}/{target_views} ✅\n"
            f"👥 <b>Новых учеников в CRM:</b> {leads}\n"
            f"📢 <b>Партнер:</b> {partner_title}\n\n"
            f"<i>Рекламный пост в канале {partner_title} был автоматически удален!</i>"
        )
        b_leads = "👥 База лидов"
        b_menu = "🏠 Главное меню"
    else:
        text = (
            f"🎉 <b>Target Views Reached!</b>\n\n"
            f"🏆 <b>WHAT YOU EARNED:</b>\n"
            f"👁 <b>Post Views Delivered:</b> {my_views}/{target_views} views ✅\n"
            f"👥 <b>New Student Leads in your CRM:</b> {leads} students\n"
            f"📢 <b>Partner:</b> {partner_title}\n\n"
            f"<i>Your promotional post in {partner_title} was automatically deleted!</i>"
        )
        b_leads = "👥 View Captured Leads"
        b_menu = "🏠 Back to Main Menu"

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=b_leads, callback_data="menu:leads")],
            [InlineKeyboardButton(text=b_menu, callback_data="menu:main")],
        ]
    )
    return text, markup


def make_summary_msg(deal_id: str, target: int, views: int, leads: int, partner_title: str, lang: str):
    if lang == "uz":
        text = (
            f"🏆 <b>Auto-VP Bitim #{deal_id[:8]} muvaffaqiyatli yakunlandi!</b>\n\n"
            f"🎯 <b>Reja:</b> {target} ta ko'rish 👀\n\n"
            f"📊 <b>NATIJANGIZ:</b>\n"
            f"• 👁 <b>Qabul qilingan ko'rishlar:</b> {views} ta ✅\n"
            f"• 👥 <b>Yangi talabalar (CRM):</b> {leads} ta\n"
            f"• 📢 <b>Sherik:</b> {partner_title}\n\n"
            f"Barcha reklama postlari toza o'chirildi."
        )
        b_leads = "👥 Talabalar bazasi"
        b_swap = "⚡ Yangi almashinuv"
        b_menu = "🏠 Asosiy menyu"
    elif lang == "ru":
        text = (
            f"🏆 <b>Авто-ВП Сделка #{deal_id[:8]} успешно завершена!</b>\n\n"
            f"🎯 <b>Цель:</b> {target} просмотров 👀\n\n"
            f"📊 <b>ВАШ РЕЗУЛЬТАТ:</b>\n"
            f"• 👁 <b>Получено просмотров:</b> {views} ✅\n"
            f"• 👥 <b>Новых учеников в CRM:</b> {leads}\n"
            f"• 📢 <b>Партнер:</b> {partner_title}\n\n"
            f"Все рекламные посты были чисто удалены."
        )
        b_leads = "👥 База учеников"
        b_swap = "⚡ Новый взаимопиар"
        b_menu = "🏠 Главное меню"
    else:
        text = (
            f"🏆 <b>Auto-VP Swap #{deal_id[:8]} Finished Successfully!</b>\n\n"
            f"🎯 <b>Target Views:</b> {target}\n\n"
            f"📊 <b>WHAT YOU EARNED:</b>\n"
            f"• 👁 <b>Views Received:</b> {views} views ✅\n"
            f"• 👥 <b>New Student Leads in CRM:</b> {leads} students\n"
            f"• 📢 <b>Partner:</b> {partner_title}\n\n"
            f"All promotional posts have been cleanly removed."
        )
        b_leads = "👥 View Captured Leads"
        b_swap = "⚡ Start New Swap"
        b_menu = "🏠 Main Menu"

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=b_leads, callback_data="menu:leads")],
            [InlineKeyboardButton(text=b_swap, callback_data="menu:pool")],
            [InlineKeyboardButton(text=b_menu, callback_data="menu:main")],
        ]
    )
    return text, markup


async def get_scanner_client() -> TelegramClient:
    global _scanner_client
    if _scanner_client is None:
        _scanner_client = TelegramClient(
            "scanner_session",
            config.telegram_api_id,
            config.telegram_api_hash,
        )
    if not _scanner_client.is_connected():
        await _scanner_client.connect()
    return _scanner_client


async def scan_active_deals_views(bot: Bot) -> int:
    """Scans all active swap deals, checks message.views with the scanner account, and deletes completed ads."""
    client = await get_scanner_client()
    if not await client.is_user_authorized():
        logger.warning("[ViewScanner] Scanner client is not authorized. Skipping view check.")
        return 0

    checked_deals = 0

    async with async_session_factory() as session:
        active_deals = await crud.get_active_deals(session)
        if not active_deals:
            return 0

        for deal in active_deals:
            checked_deals += 1
            changed = False

            # 1. Check views for Channel A's ad in Channel B (post_msg_id_in_b)
            if not deal.post_b_deleted and deal.post_msg_id_in_b:
                try:
                    msg_b = await client.get_messages(deal.channel_b_id, ids=deal.post_msg_id_in_b)
                    if msg_b and msg_b.views is not None:
                        deal.views_a_received = msg_b.views
                        changed = True
                        logger.info(
                            f"[ViewScanner] Deal {deal.id[:8]} - Channel A ad in {deal.channel_b.title}: "
                            f"{deal.views_a_received}/{deal.target_views} views"
                        )

                        if deal.views_a_received >= deal.target_views:
                            logger.info(
                                f"[ViewScanner] Goal Reached! Deleting A's ad from {deal.channel_b.title} "
                                f"({deal.views_a_received} views)"
                            )
                            await swap_engine.safe_delete_post(bot, deal.channel_b_id, deal.post_msg_id_in_b)
                            deal.post_b_deleted = True
                            await crud.update_deal_post_deletion(session, deal.id, deleted_post_in_b=True)

                            # Notify Owner A with Earnings Summary in Owner A's language
                            owner_a = await crud.get_user(session, deal.channel_a.owner_id)
                            lang_a = getattr(owner_a, "language", "uz") or "uz"
                            earned_a, markup_a = make_earned_msg(
                                deal.views_a_received, deal.target_views, deal.joins_a_received, deal.channel_b.title, lang_a
                            )
                            try:
                                await bot.send_message(
                                    chat_id=deal.channel_a.owner_id,
                                    text=earned_a,
                                    reply_markup=markup_a,
                                )
                            except Exception as e:
                                logger.warning(f"Could not notify owner A: {e}")
                except (ChannelPrivateError, ChatAdminRequiredError):
                    logger.warning(
                        f"[ViewScanner] Scanner @{config.scanner_username} is not in channel {deal.channel_b_id}!"
                    )
                except Exception as e:
                    logger.error(f"[ViewScanner] Error reading post in channel B {deal.channel_b_id}: {e}")

            # 2. Check views for Channel B's ad in Channel A (post_msg_id_in_a)
            if not deal.post_a_deleted and deal.post_msg_id_in_a:
                try:
                    msg_a = await client.get_messages(deal.channel_a_id, ids=deal.post_msg_id_in_a)
                    if msg_a and msg_a.views is not None:
                        deal.views_b_received = msg_a.views
                        changed = True
                        logger.info(
                            f"[ViewScanner] Deal {deal.id[:8]} - Channel B ad in {deal.channel_a.title}: "
                            f"{deal.views_b_received}/{deal.target_views} views"
                        )

                        if deal.views_b_received >= deal.target_views:
                            logger.info(
                                f"[ViewScanner] Goal Reached! Deleting B's ad from {deal.channel_a.title} "
                                f"({deal.views_b_received} views)"
                            )
                            await swap_engine.safe_delete_post(bot, deal.channel_a_id, deal.post_msg_id_in_a)
                            deal.post_a_deleted = True
                            await crud.update_deal_post_deletion(session, deal.id, deleted_post_in_a=True)

                            # Notify Owner B with Earnings Summary
                            owner_b = await crud.get_user(session, deal.channel_b.owner_id)
                            lang_b = getattr(owner_b, "language", "uz") or "uz"
                            earned_b, markup_b = make_earned_msg(
                                deal.views_b_received, deal.target_views, deal.joins_b_received, deal.channel_a.title, lang_b
                            )
                            try:
                                await bot.send_message(
                                    chat_id=deal.channel_b.owner_id,
                                    text=earned_b,
                                    reply_markup=markup_b,
                                )
                            except Exception as e:
                                logger.warning(f"Could not notify owner B: {e}")
                except (ChannelPrivateError, ChatAdminRequiredError):
                    logger.warning(
                        f"[ViewScanner] Scanner @{config.scanner_username} is not in channel {deal.channel_a_id}!"
                    )
                except Exception as e:
                    logger.error(f"[ViewScanner] Error reading post in channel A {deal.channel_a_id}: {e}")

            # 3. Check if both sides completed
            if deal.post_a_deleted and deal.post_b_deleted:
                logger.info(f"[ViewScanner] Deal {deal.id[:8]} completed 100%! Closing deal.")
                await crud.complete_or_close_deal(session, deal.id, "COMPLETED")

                owner_a = await crud.get_user(session, deal.channel_a.owner_id)
                lang_a = getattr(owner_a, "language", "uz") or "uz"
                owner_b = await crud.get_user(session, deal.channel_b.owner_id)
                lang_b = getattr(owner_b, "language", "uz") or "uz"

                summary_a, markup_sum_a = make_summary_msg(
                    deal.id, deal.target_views, deal.views_a_received, deal.joins_a_received, deal.channel_b.title, lang_a
                )
                summary_b, markup_sum_b = make_summary_msg(
                    deal.id, deal.target_views, deal.views_b_received, deal.joins_b_received, deal.channel_a.title, lang_b
                )

                try:
                    await bot.send_message(chat_id=deal.channel_a.owner_id, text=summary_a, reply_markup=markup_sum_a)
                except Exception:
                    pass
                try:
                    await bot.send_message(chat_id=deal.channel_b.owner_id, text=summary_b, reply_markup=markup_sum_b)
                except Exception:
                    pass

            if changed:
                await session.commit()

    return checked_deals
