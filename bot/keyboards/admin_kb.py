from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.locales.texts import t


def admin_panel_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    match_txt = "⚡ Juftlash (Match)" if lang == "uz" else ("⚡ Подбор пар" if lang == "ru" else "⚡ Force Matchmaking")
    scan_txt = "👁 Ko'rishlarni skanerlash" if lang == "uz" else ("👁 Сканировать глазок" if lang == "ru" else "👁 Force View Scan")
    clean_txt = "🧹 Tozalash (24h)" if lang == "uz" else ("🧹 Очистка (24ч)" if lang == "ru" else "🧹 Force Cleanup")
    quota_txt = "🔄 Kvotalarni yangilash" if lang == "uz" else ("🔄 Сброс квот" if lang == "ru" else "🔄 Reset Quotas")
    grant_txt = "👑 VIP Berish" if lang == "uz" else ("👑 Выдать VIP" if lang == "ru" else "👑 Grant VIP")
    revoke_txt = "🚫 VIP Bekor qilish" if lang == "uz" else ("🚫 Забрать VIP" if lang == "ru" else "🚫 Revoke VIP")

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=match_txt, callback_data="admin:force_match"),
                InlineKeyboardButton(text=scan_txt, callback_data="admin:force_scan"),
            ],
            [
                InlineKeyboardButton(text=clean_txt, callback_data="admin:force_cleanup"),
                InlineKeyboardButton(text=quota_txt, callback_data="admin:reset_quotas"),
            ],
            [
                InlineKeyboardButton(text=grant_txt, callback_data="admin:grant_vip"),
                InlineKeyboardButton(text=revoke_txt, callback_data="admin:revoke_vip"),
            ],
            [
                InlineKeyboardButton(text=t("btn_refresh", lang), callback_data="admin:menu"),
                InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main"),
            ],
        ]
    )
