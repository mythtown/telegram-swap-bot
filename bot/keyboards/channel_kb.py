from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database.models import Channel
from bot.locales.texts import t

VIEW_TIERS = [
    50, 100, 150, 200,
    250, 300, 350, 400,
    500, 600, 700, 800,
    900, 1000, 1500, 2000,
]


def channels_list_keyboard(channels: List[Channel], lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        pool_icon = "🟢" if ch.is_in_pool else "⚪️"
        verified_icon = "✅" if ch.is_verified else "⚠️"
        views_suffix = "ta" if lang == "uz" else ("просм." if lang == "ru" else "views")
        btn_text = f"{pool_icon} {ch.title} ({ch.target_tier} {views_suffix}) {verified_icon}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"channel:view:{ch.telegram_id}")])

    buttons.append([InlineKeyboardButton(text=t("btn_add_channel", lang), callback_data="channel:add")])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def channel_details_keyboard(channel: Channel, has_creative: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    pool_btn_text = t("btn_pool_off", lang) if channel.is_in_pool else t("btn_pool_on", lang)
    creative_btn_text = t("btn_edit_creative", lang)

    buttons = [
        [InlineKeyboardButton(text=creative_btn_text, callback_data=f"creative:edit:{channel.telegram_id}")],
        [
            InlineKeyboardButton(text=t("btn_change_tier", lang, tier=channel.target_tier), callback_data=f"channel:tier:{channel.telegram_id}"),
            InlineKeyboardButton(text=pool_btn_text, callback_data=f"pool:toggle:{channel.telegram_id}"),
        ],
        [
            InlineKeyboardButton(text=t("btn_schedule", lang), callback_data=f"channel:schedule:{channel.telegram_id}"),
        ],
        [
            InlineKeyboardButton(text=t("btn_reverify", lang), callback_data=f"channel:verify:{channel.telegram_id}"),
            InlineKeyboardButton(text=t("btn_delete_channel", lang), callback_data=f"channel:delete_confirm:{channel.telegram_id}"),
        ],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:channels")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def schedule_settings_keyboard(channel: Channel, lang: str = "uz") -> InlineKeyboardMarkup:
    w = channel.posting_window
    any_label = "24/7 Har doim" if lang == "uz" else ("24/7 В любое время" if lang == "ru" else "24/7 Anytime")
    eve_label = "🌆 Kechki (18-22)" if lang == "uz" else ("🌆 Вечер (18-22)" if lang == "ru" else "🌆 Evening (18-22)")
    mor_label = "☀️ Ertalabki (09-13)" if lang == "uz" else ("☀️ Утро (09-13)" if lang == "ru" else "☀️ Morning (09-13)")

    w_any = f"🔹 {any_label}" if w == "anytime" else any_label
    w_eve = f"🔹 {eve_label}" if w == "evening" else eve_label
    w_mor = f"🔹 {mor_label}" if w == "morning" else mor_label

    cd = channel.swap_cooldown_hours
    cd_label = "Dam" if lang == "uz" else ("Пауза" if lang == "ru" else "Rest")
    cd_3 = f"🔹 {cd_label}: 3h" if cd == 3 else f"{cd_label}: 3h"
    cd_6 = f"🔹 {cd_label}: 6h" if cd == 6 else f"{cd_label}: 6h"
    cd_12 = f"🔹 {cd_label}: 12h" if cd == 12 else f"{cd_label}: 12h"
    cd_24 = f"🔹 {cd_label}: 24h" if cd == 24 else f"{cd_label}: 24h"

    buttons = [
        [
            InlineKeyboardButton(text=w_eve, callback_data=f"channel:set_win:{channel.telegram_id}:evening"),
            InlineKeyboardButton(text=w_mor, callback_data=f"channel:set_win:{channel.telegram_id}:morning"),
        ],
        [
            InlineKeyboardButton(text=w_any, callback_data=f"channel:set_win:{channel.telegram_id}:anytime"),
        ],
        [
            InlineKeyboardButton(text=cd_3, callback_data=f"channel:set_cd:{channel.telegram_id}:3"),
            InlineKeyboardButton(text=cd_6, callback_data=f"channel:set_cd:{channel.telegram_id}:6"),
            InlineKeyboardButton(text=cd_12, callback_data=f"channel:set_cd:{channel.telegram_id}:12"),
            InlineKeyboardButton(text=cd_24, callback_data=f"channel:set_cd:{channel.telegram_id}:24"),
        ],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data=f"channel:view:{channel.telegram_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def tier_selector_keyboard(channel_id: int, current_tier: int, lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    tiers = VIEW_TIERS
    chunk_size = 4
    for i in range(0, len(tiers), chunk_size):
        row = []
        for tier in tiers[i:i + chunk_size]:
            mark = "🔹 " if tier == current_tier else ""
            label = f"{mark}{tier} 👀"
            row.append(InlineKeyboardButton(text=label, callback_data=f"channel:set_tier:{channel_id}:{tier}"))
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data=f"channel:view:{channel_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_channel_delete_keyboard(channel_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    yes_text = "⚠️ Ha, o'chirish" if lang == "uz" else ("⚠️ Да, удалить" if lang == "ru" else "⚠️ Yes, Delete")
    cancel_text = t("btn_cancel", lang)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data=f"channel:delete:{channel_id}"),
                InlineKeyboardButton(text=cancel_text, callback_data=f"channel:view:{channel_id}"),
            ]
        ]
    )
