from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.locales.texts import t


def student_claim_gift_keyboard(deal_id: str, channel_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    claim_text = (
        "🎁 Sovg'ani olish va A'zo bo'lish"
        if lang == "uz"
        else ("🎁 Забрать подарок и вступить" if lang == "ru" else "🎁 Claim Free Study Gift & Join")
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=claim_text,
                    callback_data=f"student:claim:{deal_id}:{channel_id}",
                )
            ]
        ]
    )


def leads_menu_keyboard(total_leads: int, is_vip: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    broadcast_txt = (
        t("btn_broadcast", lang)
        if is_vip
        else ("💎 " + ("VIP DM Xabar (Rassilka)" if lang == "uz" else ("Рассылка в ЛС (VIP)" if lang == "ru" else "Unlock DM Broadcast (VIP)")))
    )
    broadcast_btn = (
        InlineKeyboardButton(text=broadcast_txt, callback_data="menu:broadcast")
        if is_vip
        else InlineKeyboardButton(text=broadcast_txt, callback_data="menu:vip_info")
    )

    export_txt = (
        t("btn_export_csv", lang)
        if is_vip
        else ("🔒 " + ("Excel/CSV yuklash (VIP)" if lang == "uz" else ("Экспорт в Excel (VIP)" if lang == "ru" else "Export CSV (VIP Only)")))
    )
    export_btn = (
        InlineKeyboardButton(text=export_txt, callback_data="leads:export_csv")
        if is_vip
        else InlineKeyboardButton(text=export_txt, callback_data="menu:vip_info")
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [broadcast_btn],
            [export_btn],
            [InlineKeyboardButton(text=t("btn_refresh", lang), callback_data="menu:leads")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")],
        ]
    )
