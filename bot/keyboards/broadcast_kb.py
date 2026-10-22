from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database.models import Channel
from bot.locales.texts import t


def broadcast_channel_picker_keyboard(channels: List[Channel], all_leads_count: int, lang: str = "uz") -> InlineKeyboardMarkup:
    all_label = (
        f"🌐 Barcha talabalar ({all_leads_count})"
        if lang == "uz"
        else (f"🌐 Все ученики ({all_leads_count})" if lang == "ru" else f"🌐 All Captured Students ({all_leads_count})")
    )
    buttons = [
        [
            InlineKeyboardButton(
                text=all_label,
                callback_data="broadcast:target:all",
            )
        ]
    ]
    for ch in channels:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"📢 {ch.title}",
                    callback_data=f"broadcast:target:{ch.telegram_id}",
                )
            ]
        )
    buttons.append([InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="menu:leads")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def broadcast_confirm_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    send_txt = "🚀 Yuborishni boshlash" if lang == "uz" else ("🚀 Запустить рассылку" if lang == "ru" else "🚀 Send Broadcast Now")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=send_txt, callback_data="broadcast:confirm_send"),
                InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="menu:leads"),
            ]
        ]
    )
