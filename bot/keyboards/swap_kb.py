from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database.models import SwapDeal
from bot.locales.texts import t


def deals_list_keyboard(deals: List[SwapDeal], user_channel_ids: List[int], lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    for d in deals:
        is_a = d.channel_a_id in user_channel_ids
        views = d.views_a_received if is_a else d.views_b_received
        status_icon = "🟢" if d.status == "ACTIVE" else "✅"
        views_word = "ko'rish" if lang == "uz" else ("просмотров" if lang == "ru" else "views")
        btn_text = f"{status_icon} #{d.id[:6]} ({views}/{d.target_views} {views_word} 👀)"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"deal:view:{d.id}")])

    buttons.append([InlineKeyboardButton(text=t("btn_refresh", lang), callback_data="menu:deals")])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def deal_detail_keyboard(deal_id: str, is_active: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    if is_active:
        cancel_deal_txt = "🛑 Bitimni to'xtatish" if lang == "uz" else ("🛑 Прервать сделку" if lang == "ru" else "🛑 Cancel Deal")
        buttons.append([InlineKeyboardButton(text=cancel_deal_txt, callback_data=f"deal:cancel_confirm:{deal_id}")])
    buttons.append([InlineKeyboardButton(text=t("btn_refresh", lang), callback_data=f"deal:view:{deal_id}")])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:deals")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_deal_cancel_keyboard(deal_id: str, lang: str = "uz") -> InlineKeyboardMarkup:
    yes_txt = "⚠️ Ha, to'xtatilsin" if lang == "uz" else ("⚠️ Да, отменить" if lang == "ru" else "⚠️ Yes, Cancel")
    keep_txt = "Davom etsin" if lang == "uz" else ("Оставить активным" if lang == "ru" else "Keep Running")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_txt, callback_data=f"deal:cancel:{deal_id}"),
                InlineKeyboardButton(text=keep_txt, callback_data=f"deal:view:{deal_id}"),
            ]
        ]
    )
