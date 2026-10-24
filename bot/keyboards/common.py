from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from bot.config import config
from bot.locales.texts import LANGUAGES, t


def main_reply_keyboard(
    lang: str = "uz",
    is_vip: bool = False,
    is_admin: bool = False,
) -> ReplyKeyboardMarkup:
    """Bottom Reply Keyboard designed identically to the user's sleek reference UI:
    2-column grid with premium unicode symbols (+, ≡, ||||, ⚙, ✉, ⊘, ⚡, 🤝).
    """
    keyboard = [
        [
            KeyboardButton(text=t("btn_add_channel", lang)),
            KeyboardButton(text=t("btn_channels", lang)),
        ],
        [
            KeyboardButton(text=t("btn_auto_vp", lang)),
            KeyboardButton(text=t("btn_deals", lang)),
        ],
        [
            KeyboardButton(text=t("btn_stats", lang)),
            KeyboardButton(text=t("btn_referral", lang)),
        ],
        [
            KeyboardButton(text=t("btn_settings", lang)),
            KeyboardButton(text=t("btn_support", lang)),
        ],
    ]

    extra_row = []
    if is_vip:
        extra_row.append(KeyboardButton(text=t("btn_broadcast", lang)))
    else:
        extra_row.append(KeyboardButton(text=t("btn_vip", lang)))
    if is_admin:
        extra_row.append(KeyboardButton(text=t("btn_admin", lang)))

    if extra_row:
        keyboard.append(extra_row)

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def mandatory_sub_keyboard(channel: str, lang: str = "uz") -> InlineKeyboardMarkup:
    clean_username = channel.lstrip("@").strip()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_join_channel", lang), url=f"https://t.me/{clean_username}")],
            [InlineKeyboardButton(text=t("btn_check_sub", lang), callback_data="sub:check")],
        ]
    )


def main_menu_keyboard(
    lang: str = "uz",
    is_vip: bool = False,
    is_admin: bool = False,
) -> InlineKeyboardMarkup:
    """Inline menu keyboard with navigation and clean symbols."""
    buttons = [
        [
            InlineKeyboardButton(text=t("btn_channels", lang), callback_data="menu:channels"),
            InlineKeyboardButton(text=t("btn_auto_vp", lang), callback_data="menu:pool"),
        ],
        [
            InlineKeyboardButton(text=t("btn_deals", lang), callback_data="menu:deals"),
            InlineKeyboardButton(text=t("btn_stats", lang), callback_data="menu:leads"),
        ],
        [
            InlineKeyboardButton(text=t("btn_referral", lang), callback_data="menu:referral"),
            InlineKeyboardButton(
                text="💎 VIP" if is_vip else t("btn_vip", lang),
                callback_data="menu:vip_info",
            ),
        ],
        [
            InlineKeyboardButton(text=t("btn_settings", lang), callback_data="menu:settings"),
            InlineKeyboardButton(text=t("btn_support", lang), callback_data="menu:support"),
        ],
    ]
    if is_vip:
        buttons.insert(3, [InlineKeyboardButton(text=t("btn_broadcast", lang), callback_data="menu:broadcast")])
    if is_admin:
        buttons.append([InlineKeyboardButton(text=t("btn_admin", lang), callback_data="admin:menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def initial_language_keyboard() -> InlineKeyboardMarkup:
    """Prompt keyboard shown when a new user joins for the first time."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="init_lang:uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="init_lang:ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="init_lang:en")],
        ]
    )


def language_selector_keyboard(current_lang: str = "uz") -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{'🔹 ' if current_lang == 'uz' else ''}🇺🇿 O'zbekcha",
                callback_data="set_lang:uz",
            ),
            InlineKeyboardButton(
                text=f"{'🔹 ' if current_lang == 'ru' else ''}🇷🇺 Русский",
                callback_data="set_lang:ru",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{'🔹 ' if current_lang == 'en' else ''}🇬🇧 English",
                callback_data="set_lang:en",
            ),
        ],
        [
            InlineKeyboardButton(text=t("btn_back", current_lang), callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_keyboard(lang: str = "uz", is_vip: bool = False) -> InlineKeyboardMarkup:
    """Settings menu inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🌐 {LANGUAGES.get(lang, 'Language')}",
                    callback_data="menu:language",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_vip", lang),
                    callback_data="menu:vip_info",
                ),
                InlineKeyboardButton(
                    text=t("btn_support", lang),
                    callback_data="menu:support",
                ),
            ],
            [
                InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main"),
            ],
        ]
    )


def back_to_main_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main")]
        ]
    )


def cancel_action_keyboard(lang: str = "uz", return_to: str = "menu:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=return_to)]
        ]
    )


def access_request_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_request_access", lang), callback_data="access:request")],
            [InlineKeyboardButton(text=t("btn_support", lang), url=f"https://t.me/{config.support_username}")],
        ]
    )


def admin_approve_user_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ruxsat berish (Approve)", callback_data=f"admin:approve:{user_id}"),
                InlineKeyboardButton(text="❌ Rad etish (Reject)", callback_data=f"admin:reject:{user_id}"),
            ]
        ]
    )
