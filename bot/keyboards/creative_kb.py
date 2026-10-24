from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.locales.texts import t


def skip_step_keyboard(skip_callback: str, cancel_callback: str, lang: str = "uz") -> InlineKeyboardMarkup:
    skip_text = "⏭ Standart / O'tkazib yuborish" if lang == "uz" else ("⏭ По умолчанию / Пропустить" if lang == "ru" else "⏭ Use Default / Skip")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=skip_text, callback_data=skip_callback)],
            [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=cancel_callback)],
        ]
    )


def creative_format_choice_keyboard(channel_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn_format_text", lang), callback_data=f"creative:format:text:{channel_id}"),
            ],
            [
                InlineKeyboardButton(text=t("btn_format_gift", lang), callback_data=f"creative:format:gift:{channel_id}"),
            ],
            [
                InlineKeyboardButton(text=t("btn_back", lang), callback_data=f"channel:view:{channel_id}"),
            ],
        ]
    )


def creative_actions_keyboard(channel_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    preview_txt = "👁 Postni ko'rish (Test)" if lang == "uz" else ("👁 Предпросмотр поста" if lang == "ru" else "👁 Preview Full Ad")
    reupload_txt = "🔄 Yangitdan yuklash" if lang == "uz" else ("🔄 Загрузить заново" if lang == "ru" else "🔄 Re-upload Creative")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=preview_txt, callback_data=f"creative:preview:{channel_id}")],
            [InlineKeyboardButton(text=reupload_txt, callback_data=f"creative:edit:{channel_id}")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data=f"channel:view:{channel_id}")],
        ]
    )
