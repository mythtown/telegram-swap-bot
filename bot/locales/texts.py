"""EduSwap Multi-Language Localization System (Uzbek, Russian, English).
Provides concise, elegant, simple copy with premium symbols and zero mixed-language fallbacks.
"""
from typing import Dict, Any

LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

DEFAULT_LANGUAGE = "uz"

STRINGS: Dict[str, Dict[str, str]] = {
    # ==================== REPLY KEYBOARD LABELS ====================
    "btn_add_channel": {
        "uz": "+ Kanal qo'shish",
        "ru": "+ Добавить канал",
        "en": "+ Add Channel",
    },
    "btn_channels": {
        "uz": "≡ Kanallar",
        "ru": "≡ Мои каналы",
        "en": "≡ Channels",
    },
    "btn_auto_vp": {
        "uz": "⚡ Auto-VP",
        "ru": "⚡ Авто-ВП",
        "en": "⚡ Auto-VP",
    },
    "btn_deals": {
        "uz": "🤝 Bitimlar",
        "ru": "🤝 Сделки",
        "en": "🤝 Active Deals",
    },
    "btn_stats": {
        "uz": "|||| Statistika",
        "ru": "|||| Статистика",
        "en": "|||| Statistics",
    },
    "btn_settings": {
        "uz": "⚙ Sozlamalar",
        "ru": "⚙ Настройки",
        "en": "⚙ Settings",
    },
    "btn_broadcast": {
        "uz": "✉ Xabar tarqatish",
        "ru": "✉ Рассылка",
        "en": "✉ Broadcast",
    },
    "btn_support": {
        "uz": "💬 Aloqa",
        "ru": "💬 Поддержка",
        "en": "💬 Support",
    },
    "btn_vip": {
        "uz": "💎 VIP Tarif",
        "ru": "💎 VIP Тариф",
        "en": "💎 VIP Upgrade",
    },
    "btn_admin": {
        "uz": "⊘ Admin panel",
        "ru": "⊘ Админ-панель",
        "en": "⊘ Admin Panel",
    },
    "btn_back": {
        "uz": "« Orqaga",
        "ru": "« Назад",
        "en": "« Back",
    },
    "btn_cancel": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Отмена",
        "en": "❌ Cancel",
    },
    "btn_main_menu": {
        "uz": "🏠 Asosiy menyu",
        "ru": "🏠 Главное меню",
        "en": "🏠 Main Menu",
    },
    "btn_refresh": {
        "uz": "🔄 Yangilash",
        "ru": "🔄 Обновить",
        "en": "🔄 Refresh",
    },
    "btn_change_lang": {
        "uz": "🌐 Tilni o'zgartirish",
        "ru": "🌐 Сменить язык",
        "en": "🌐 Change Language",
    },
    "btn_referral": {
        "uz": "👥 Taklif qilish",
        "ru": "👥 Рефералы",
        "en": "👥 Invite Friends",
    },
    "btn_join_channel": {
        "uz": "📢 Kanalga a'zo bo'lish",
        "ru": "📢 Подписаться на канал",
        "en": "📢 Join Channel",
    },
    "btn_check_sub": {
        "uz": "🔄 Tekshirish",
        "ru": "🔄 Проверить",
        "en": "🔄 Verify",
    },
    "btn_format_text": {
        "uz": "📝 Klassik Matn (Faylsiz)",
        "ru": "📝 Классический Текст (Без файлов)",
        "en": "📝 Traditional Text (No Files)",
    },
    "btn_format_gift": {
        "uz": "🎁 Sovg'ali / Faylli",
        "ru": "🎁 С подарком / файлом",
        "en": "🎁 Lead Magnet (With Gift)",
    },
    "btn_share_ref": {
        "uz": "↗️ Do'stlarga yuborish",
        "ru": "↗️ Поделиться с коллегами",
        "en": "↗️ Share With Teachers",
    },

    # ==================== WELCOME & START ====================
    "welcome_approved": {
        "uz": (
            "⚡ <b>EduSwap Platformasi</b>\n\n"
            "Assalomu alaykum, <b>{name}</b>!\n"
            "Ta'lim kanallari uchun ko'rishlar (👀) bo'yicha o'zaro reklama va CRM tizimi.\n\n"
            "⭐ <b>Tarif:</b> {plan}\n"
            "🔄 <b>Haftalik almashinuvlar:</b> {swaps}/{limit}\n\n"
            "<i>Pastdagi menyudan kerakli bo'limni tanlang:</i>"
        ),
        "ru": (
            "⚡ <b>Платформа EduSwap</b>\n\n"
            "Здравствуйте, <b>{name}</b>!\n"
            "Взаимопиар по просмотрам (👀) и сбор базы учеников (CRM).\n\n"
            "⭐ <b>Тариф:</b> {plan}\n"
            "🔄 <b>Сделок на этой неделе:</b> {swaps}/{limit}\n\n"
            "<i>Выберите нужный раздел в меню ниже:</i>"
        ),
        "en": (
            "⚡ <b>EduSwap Platform</b>\n\n"
            "Welcome, <b>{name}</b>!\n"
            "Automated cross-promotion by post views (👀) & lead capture CRM.\n\n"
            "⭐ <b>Plan:</b> {plan}\n"
            "🔄 <b>Swaps this week:</b> {swaps}/{limit}\n\n"
            "<i>Select an option from the menu below:</i>"
        ),
    },

    "private_gate_locked": {
        "uz": (
            "🔒 <b>EduSwap — Yopiq tizim</b>\n\n"
            "Salom, <b>{name}</b>!\n"
            "Bot faqat tasdiqlangan o'qituvchilar va kanal egalari uchun ishlaydi.\n\n"
            "👉 <i>Kirish uchun so'rov qoldiring:</i>"
        ),
        "ru": (
            "🔒 <b>EduSwap — Закрытая платформа</b>\n\n"
            "Привет, <b>{name}</b>!\n"
            "Бот доступен только проверенным преподавателям и каналам.\n\n"
            "👉 <i>Подайте заявку на доступ:</i>"
        ),
        "en": (
            "🔒 <b>EduSwap — Private Network</b>\n\n"
            "Hello, <b>{name}</b>!\n"
            "Access is reserved for verified educators and channel owners.\n\n"
            "👉 <i>Tap below to request access:</i>"
        ),
    },

    "private_gate_pending": {
        "uz": (
            "⏳ <b>Arizangiz ko'rib chiqilmoqda</b>\n\n"
            "Administratorlarimiz arizangizni ko'rib chiqib, tez orada tasdiqlashadi.\n\n"
            "Shoshilinch bo'lsa: @{support}"
        ),
        "ru": (
            "⏳ <b>Заявка на рассмотрении</b>\n\n"
            "Администратор проверяет вашу заявку и скоро откроет доступ.\n\n"
            "Срочные вопросы: @{support}"
        ),
        "en": (
            "⏳ <b>Application Under Review</b>\n\n"
            "Our administrators are reviewing your request.\n\n"
            "Urgent inquiries: @{support}"
        ),
    },

    "btn_request_access": {
        "uz": "📝 Kirish uchun so'rov yuborish",
        "ru": "📝 Подать заявку на доступ",
        "en": "📝 Request Teacher Access",
    },
    "btn_check_status": {
        "uz": "🔄 Holatni tekshirish",
        "ru": "🔄 Проверить статус",
        "en": "🔄 Check Status",
    },
    "request_submitted": {
        "uz": "✅ <b>So'rovingiz qabul qilindi!</b>\n\nTez orada tasdiqlanadi. Xabar kutib turing.",
        "ru": "✅ <b>Заявка отправлена!</b>\n\nАдминистратор скоро рассмотрит её. Ожидайте уведомления.",
        "en": "✅ <b>Application Submitted!</b>\n\nAdmins will review and approve your account shortly.",
    },

    # ==================== SETTINGS & LANGUAGE ====================
    "settings_title": {
        "uz": (
            "⚙ <b>Sozlamalar</b>\n\n"
            "👤 <b>Foydalanuvchi:</b> {name}\n"
            "🌐 <b>Joriy til:</b> 🇺🇿 O'zbekcha\n"
            "⭐ <b>Tarif:</b> {plan}\n"
            "🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
            "Tilni o'zgartirish uchun tanlang:"
        ),
        "ru": (
            "⚙ <b>Настройки</b>\n\n"
            "👤 <b>Пользователь:</b> {name}\n"
            "🌐 <b>Текущий язык:</b> 🇷🇺 Русский\n"
            "⭐ <b>Тариф:</b> {plan}\n"
            "🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
            "Выберите язык интерфейса:"
        ),
        "en": (
            "⚙ <b>Settings</b>\n\n"
            "👤 <b>User:</b> {name}\n"
            "🌐 <b>Language:</b> 🇬🇧 English\n"
            "⭐ <b>Plan:</b> {plan}\n"
            "🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
            "Select interface language:"
        ),
    },
    "lang_changed": {
        "uz": "🇺🇿 <b>Til O'zbekchaga o'zgartirildi!</b>",
        "ru": "🇷🇺 <b>Язык успешно изменён на Русский!</b>",
        "en": "🇬🇧 <b>Language updated to English!</b>",
    },
    "settings_saved": {
        "uz": "✅ Saqlandi",
        "ru": "✅ Сохранено",
        "en": "✅ Saved",
    },

    # ==================== SUPPORT & VIP ====================
    "support_text": {
        "uz": (
            "💬 <b>Aloqa va Hamkorlik</b>\n\n"
            "Savollar, takliflar yoki VIP tarifni ulash uchun to'g'ridan-to'g'ri murojaat qiling:\n\n"
            "👤 <b>Administrator:</b> @{support}"
        ),
        "ru": (
            "💬 <b>Поддержка и Сотрудничество</b>\n\n"
            "По вопросам, партнерству или подключению VIP напишите нам напрямую:\n\n"
            "👤 <b>Администратор:</b> @{support}"
        ),
        "en": (
            "💬 <b>Support & Collaboration</b>\n\n"
            "For inquiries, partnerships, or VIP upgrades:\n\n"
            "👤 <b>Administrator:</b> @{support}"
        ),
    },
    "vip_info_text": {
        "uz": (
            "💎 <b>VIP Tarif Imkoniyatlari</b>\n\n"
            "• ✉ <b>Lidlar DMsiga xabar yuborish:</b> 80%+ o'qilish darajasi\n"
            "• 📥 <b>Talabalar bazasini Excel/CSV formatida yuklab olish</b>\n"
            "• ⚡ <b>Cheksiz reklama almashinuvlari (haftalik cheklovsiz)</b>\n"
            "• 👑 <b>Postlarda bot belgisiz (toza ko'rinish)</b>\n"
            "• 🌆 <b>Kechki eng qizg'in vaqtlarda (18:00–22:00) birinchi navbat</b>\n\n"
            "Ulash uchun administrator: @{support}"
        ),
        "ru": (
            "💎 <b>Возможности VIP Тарифа</b>\n\n"
            "• ✉ <b>Рассылка лидам прямо в ЛС:</b> открываемость 80%+\n"
            "• 📥 <b>Выгрузка базы учеников в Excel/CSV</b>\n"
            "• ⚡ <b>Безлимитный взаимопиар (без ограничений в неделю)</b>\n"
            "• 👑 <b>Посты без водяных знаков и рекламы бота</b>\n"
            "• 🌆 <b>Приоритет в вечерний прайм-тайм (18:00–22:00)</b>\n\n"
            "Для подключения напишите: @{support}"
        ),
        "en": (
            "💎 <b>VIP Partner Privileges</b>\n\n"
            "• ✉ <b>Direct DM Broadcast to students:</b> 80%+ open rate\n"
            "• 📥 <b>1-Click Export to Excel/CSV</b>\n"
            "• ⚡ <b>Unlimited Auto-Swaps (no weekly limits)</b>\n"
            "• 👑 <b>100% Whitelabel (no bot marks)</b>\n"
            "• 🌆 <b>Prime-Time priority (18:00–22:00)</b>\n\n"
            "To activate, contact: @{support}"
        ),
    },

    # ==================== CHANNELS ====================
    "channels_list_title": {
        "uz": "≡ <b>Sizning kanallaringiz ({count})</b>\n\nBoshqarish uchun kanalni tanlang:",
        "ru": "≡ <b>Ваши каналы ({count})</b>\n\nВыберите канал для управления:",
        "en": "≡ <b>Your Channels ({count})</b>\n\nSelect a channel to manage:",
    },
    "no_channels": {
        "uz": "≡ <b>Sizda hali kanallar yo'q.</b>\n\nQo'shish uchun pastdagi tugmani bosing:",
        "ru": "≡ <b>У вас пока нет добавленных каналов.</b>\n\nНажмите кнопку ниже для добавления:",
        "en": "≡ <b>You have no channels yet.</b>\n\nTap below to add your first channel:",
    },
    "add_channel_prompt": {
        "uz": (
            "+ <b>Yangi kanal qo'shish</b>\n\n"
            "1. @{bot_name} ni kanalingizga <b>Admin</b> qiling (xabarlar yozish va o'chirish huquqi bilan).\n"
            "2. Ko'rishlarni hisoblovchi yordamchi <b>@{scanner_name}</b> ni kanalga qo'shing.\n"
            "3. Kanalingiz <b>@username</b> yoki <b>ID</b> sini yuboring:"
        ),
        "ru": (
            "+ <b>Добавление канала</b>\n\n"
            "1. Назначьте @{bot_name} <b>Администратором</b> канала (права: посты и удаление).\n"
            "2. Добавьте помощника <b>@{scanner_name}</b> в участники канала (для учёта просмотров 👀).\n"
            "3. Отправьте <b>@username</b> или <b>ID</b> канала:"
        ),
        "en": (
            "+ <b>Add New Channel</b>\n\n"
            "1. Add @{bot_name} as <b>Admin</b> (post & delete messages).\n"
            "2. Add assistant <b>@{scanner_name}</b> as channel member (to scan views 👀).\n"
            "3. Send your channel <b>@username</b> or <b>ID</b>:"
        ),
    },
    "channel_connected_succ": {
        "uz": (
            "✅ <b>Kanal muvaffaqiyatli ulandi!</b>\n\n"
            "📢 <b>Nomi:</b> {title}\n"
            "🎯 <b>Reja:</b> {tier} ta ko'rish 👀\n\n"
            "💡 <i>Ko'rishlar hisoblanishi uchun <b>@{scanner}</b> kanal a'zosi bo'lishi shart!</i>"
        ),
        "ru": (
            "✅ <b>Канал успешно подключен!</b>\n\n"
            "📢 <b>Название:</b> {title}\n"
            "🎯 <b>Цель:</b> {tier} просмотров 👀\n\n"
            "💡 <i>Убедитесь, что помощник <b>@{scanner}</b> добавлен в канал!</i>"
        ),
        "en": (
            "✅ <b>Channel successfully connected!</b>\n\n"
            "📢 <b>Title:</b> {title}\n"
            "🎯 <b>Goal:</b> {tier} views 👀\n\n"
            "💡 <i>Ensure <b>@{scanner}</b> is added to scan post views!</i>"
        ),
    },
    "channel_details_title": {
        "uz": (
            "📢 <b>{title}</b>\n\n"
            "🎯 <b>Reja:</b> {tier} ta ko'rish 👀\n"
            "⚡ <b>Auto-VP holati:</b> {pool_status}\n"
            "🎁 <b>Sovg'a posti:</b> {creative_status}\n"
            "⏰ <b>Vaqt rejasi:</b> {window}\n"
            "⏳ <b>Dam olish vaqti:</b> {cooldown} soat"
        ),
        "ru": (
            "📢 <b>{title}</b>\n\n"
            "🎯 <b>Цель:</b> {tier} просмотров 👀\n"
            "⚡ <b>Авто-ВП:</b> {pool_status}\n"
            "🎁 <b>Рекламный подарок:</b> {creative_status}\n"
            "⏰ <b>Окно публикаций:</b> {window}\n"
            "⏳ <b>Пауза между сделками:</b> {cooldown} ч."
        ),
        "en": (
            "📢 <b>{title}</b>\n\n"
            "🎯 <b>Goal:</b> {tier} views 👀\n"
            "⚡ <b>Auto-VP Pool:</b> {pool_status}\n"
            "🎁 <b>Gift creative:</b> {creative_status}\n"
            "⏰ <b>Window:</b> {window}\n"
            "⏳ <b>Rest period:</b> {cooldown}h"
        ),
    },
    "channel_schedule_title": {
        "uz": (
            "⏰ <b>{title} — Vaqt va Dam olish rejasi</b>\n\n"
            "🕒 <b>Toshkent soati:</b> {clock} (UTC+5)\n"
            "⏳ <b>Dam olish holati:</b> {cooldown_status}\n\n"
            "Obunachilar charchamasligi uchun vaqt va dam olish oralig'ini tanlang:"
        ),
        "ru": (
            "⏰ <b>{title} — Расписание и паузы</b>\n\n"
            "🕒 <b>Текущее время:</b> {clock} (UTC+5)\n"
            "⏳ <b>Статус паузы:</b> {cooldown_status}\n\n"
            "Выберите время выхода и паузу между сделками:"
        ),
        "en": (
            "⏰ <b>{title} — Schedule & Rest Period</b>\n\n"
            "🕒 <b>Current clock:</b> {clock} (UTC+5)\n"
            "⏳ <b>Rest status:</b> {cooldown_status}\n\n"
            "Configure active posting window and rest interval:"
        ),
    },
    "channel_delete_confirm": {
        "uz": "⚠️ <b>Kanalni o'chirmoqchimisiz?</b>\nReklama va sozlamalar o'chiriladi.",
        "ru": "⚠️ <b>Удалить канал?</b>\nНастройки и пост будут удалены.",
        "en": "⚠️ <b>Delete this channel?</b>\nPost creative and settings will be removed.",
    },
    "channel_deleted": {
        "uz": "Kanal o'chirildi.",
        "ru": "Канал удален.",
        "en": "Channel deleted.",
    },
    "channel_not_found": {
        "uz": "⚠️ Kanal topilmadi. Qayta urinib ko'ring.",
        "ru": "⚠️ Канал не найден. Попробуйте снова.",
        "en": "⚠️ Channel not found. Please try again.",
    },
    "perms_insufficient": {
        "uz": "⚠️ <b>Ruxsatlar yetarli emas:</b> {msg}\nBotga to'liq admin huquqlarini bering.",
        "ru": "⚠️ <b>Недостаточно прав:</b> {msg}\nВыдайте боту полные права администратора.",
        "en": "⚠️ <b>Insufficient permissions:</b> {msg}\nGrant full administrator rights to the bot.",
    },
    "btn_edit_creative": {
        "uz": "🎁 Sovg'a va Postni sozlash",
        "ru": "🎁 Настроить подарок и пост",
        "en": "🎁 Setup Gift & Ad Creative",
    },
    "btn_change_tier": {
        "uz": "🎯 Ko'rishlar: {tier} 👀",
        "ru": "🎯 Просмотры: {tier} 👀",
        "en": "🎯 Target: {tier} Views 👀",
    },
    "btn_pool_on": {
        "uz": "🟢 Havzaga qo'shish (Auto-VP)",
        "ru": "🟢 Включить в Пул (Авто-ВП)",
        "en": "🟢 Turn ON Auto-VP",
    },
    "btn_pool_off": {
        "uz": "🔴 Havzadan to'xtatish",
        "ru": "🔴 Выключить из Пула",
        "en": "🔴 Turn OFF Auto-VP",
    },
    "btn_schedule": {
        "uz": "⏰ Vaqt va Dam olish rejasi",
        "ru": "⏰ Расписание и Пауза",
        "en": "⏰ Schedule & Rest Period",
    },
    "btn_reverify": {
        "uz": "🔄 Qayta tekshirish",
        "ru": "🔄 Перепроверить права",
        "en": "🔄 Re-verify Admin",
    },
    "btn_delete_channel": {
        "uz": "🗑 Kanalni o'chirish",
        "ru": "🗑 Удалить канал",
        "en": "🗑 Delete Channel",
    },

    # ==================== CREATIVES & GIFTS ====================
    "step_ad_content": {
        "uz": (
            "🎨 <b>1/4-qadam: Reklama posti</b>\n\n"
            "Hamkoringiz kanalida chiqadigan reklama postini yuboring (matn, rasm yoki video):"
        ),
        "ru": (
            "🎨 <b>Шаг 1 из 4: Рекламный пост</b>\n\n"
            "Отправьте пост для размещения в канале партнера (текст, фото или видео):"
        ),
        "en": (
            "🎨 <b>Step 1 of 4: Ad Creative</b>\n\n"
            "Send your promo post to be shown in partner channels (text, photo, or video):"
        ),
    },
    "step_button_text": {
        "uz": (
            "🔘 <b>2/4-qadam: Tugma matni</b>\n\n"
            "Post ostidagi tugma nomini yuboring (masalan: <i>🎁 Bepul darslikni olish</i>):"
        ),
        "ru": (
            "🔘 <b>Шаг 2 из 4: Текст кнопки</b>\n\n"
            "Отправьте текст для кнопки под постом (например: <i>🎁 Получить полезный файл</i>):"
        ),
        "en": (
            "🔘 <b>Step 2 of 4: Button Text</b>\n\n"
            "Send text for the button under the ad (e.g. <i>🎁 Claim Free Study Material</i>):"
        ),
    },
    "step_gift_title": {
        "uz": (
            "📖 <b>3/4-qadam: Sovg'a nomi</b>\n\n"
            "Talabaga beriladigan material nomini kiriting (masalan: <i>IELTS 8.0 Vocabulary PDF</i>):"
        ),
        "ru": (
            "📖 <b>Шаг 3 из 4: Название подарка</b>\n\n"
            "Введите название учебного материала (например: <i>IELTS 8.0 Сборник PDF</i>):"
        ),
        "en": (
            "📖 <b>Step 3 of 4: Gift Title</b>\n\n"
            "Enter title of the gift material (e.g. <i>IELTS 8.0 Vocabulary Guide</i>):"
        ),
    },
    "step_gift_file": {
        "uz": (
            "📎 <b>4/4-qadam: Sovg'a fayli</b>\n\n"
            "Faylni yuboring (PDF, ZIP, Video, Rasm, Audio) yoki dars havolasini yozing:"
        ),
        "ru": (
            "📎 <b>Шаг 4 из 4: Файл подарка</b>\n\n"
            "Отправьте файл (PDF, ZIP, Видео, Фото, Аудио) или ссылку на материалы:"
        ),
        "en": (
            "📎 <b>Step 4 of 4: Gift File</b>\n\n"
            "Upload file (PDF, ZIP, Video, Photo, Audio) or send resource link:"
        ),
    },
    "creative_saved": {
        "uz": "✅ <b>Post va Bepul sovg'a saqlandi!</b>",
        "ru": "✅ <b>Рекламный пост и подарок сохранены!</b>",
        "en": "✅ <b>Ad creative & free gift saved successfully!</b>",
    },
    "preview_ad_header": {
        "uz": "👇 <b>REKLAMA PREVIEW (Sherik kanalda shunday chiqadi):</b>",
        "ru": "👇 <b>ПРЕДПРОСМОТР (Так пост выйдет в канале партнера):</b>",
        "en": "👇 <b>AD PREVIEW (How partners will see it):</b>",
    },
    "preview_gift_label": {
        "uz": "🎁 <b>Talabaga beriladigan sovg'a:</b> {title}",
        "ru": "🎁 <b>Подарок ученику:</b> {title}",
        "en": "🎁 <b>Student free gift:</b> {title}",
    },

    # ==================== AUTO-VP POOL ====================
    "pool_title": {
        "uz": (
            "⚡ <b>Auto-VP Havzasi</b>\n\n"
            "Haftalik kvota: <b>{swaps}/{limit}</b>\n\n"
            "Kanallarni avtomatik juftlash uchun yoqing yoki o'chiring:"
        ),
        "ru": (
            "⚡ <b>Пул Авто-ВП</b>\n\n"
            "Квота на неделю: <b>{swaps}/{limit}</b>\n\n"
            "Включите или выключите каналы для авто-подбора пар:"
        ),
        "en": (
            "⚡ <b>Auto-VP Pool</b>\n\n"
            "Weekly quota: <b>{swaps}/{limit}</b>\n\n"
            "Toggle channels ON/OFF for automated pairing:"
        ),
    },
    "pool_added": {
        "uz": "🟢 Havzaga qo'shildi!",
        "ru": "🟢 Добавлен в пул!",
        "en": "🟢 Added to pool!",
    },
    "pool_paused": {
        "uz": "🔴 To'xtatildi",
        "ru": "🔴 Приостановлен",
        "en": "🔴 Paused",
    },
    "need_creative_first": {
        "uz": "⚠️ Avval reklama posti va bepul sovg'ani yuklang!",
        "ru": "⚠️ Сначала настройте рекламный пост и подарок!",
        "en": "⚠️ Please setup ad post and free gift first!",
    },

    # ==================== DEALS & CLOCK ====================
    "deals_title": {
        "uz": "🤝 <b>Faol Bitimlar ({count})</b>\n\nJonli ko'rishlar (👀) va avtomatik o'chirish holati:",
        "ru": "🤝 <b>Активные Сделки ({count})</b>\n\nТекущие просмотры (👀) и авто-удаление:",
        "en": "🤝 <b>Active Deals ({count})</b>\n\nLive view counts (👀) and auto-deletion:",
    },
    "no_deals": {
        "uz": "🤝 <b>Hozircha faol bitimlar yo'q.</b>\n\nKanalingizni Auto-VP havzasiga qo'shing va tizim uni avtomatik juftlaydi.",
        "ru": "🤝 <b>Сейчас нет активных сделок.</b>\n\nВключите канал в пул Авто-ВП, и бот автоматически найдет пару.",
        "en": "🤝 <b>No active deals right now.</b>\n\nTurn ON Auto-VP for your channel to be matched automatically.",
    },
    "deal_detail_title": {
        "uz": (
            "🤝 <b>Bitim #{deal_id}</b>\n\n"
            "📢 <b>Sizning kanalingiz:</b> {my_ch}\n"
            "📢 <b>Sherik kanal:</b> {partner_ch}\n"
            "🎯 <b>Reja:</b> {target} ta ko'rish (👀)\n\n"
            "👁 <b>Sizning postingiz:</b> {my_views}/{target} ko'rish 👀\n"
            "👁 <b>Sherik posti:</b> {partner_views}/{target} ko'rish 👀\n"
            "👥 <b>Yig'ilgan talabalar:</b> {my_leads} ta lid\n"
            "⏱ <b>24h Taymer:</b> {timer}\n"
            "⚡ <b>Holat:</b> {status}"
        ),
        "ru": (
            "🤝 <b>Сделка #{deal_id}</b>\n\n"
            "📢 <b>Ваш канал:</b> {my_ch}\n"
            "📢 <b>Канал партнера:</b> {partner_ch}\n"
            "🎯 <b>Цель:</b> {target} просмотров (👀)\n\n"
            "👁 <b>Ваш пост набрал:</b> {my_views}/{target} 👀\n"
            "👁 <b>Пост партнера:</b> {partner_views}/{target} 👀\n"
            "👥 <b>Собрано лидов:</b> {my_leads}\n"
            "⏱ <b>24ч Таймер:</b> {timer}\n"
            "⚡ <b>Статус:</b> {status}"
        ),
        "en": (
            "🤝 <b>Deal #{deal_id}</b>\n\n"
            "📢 <b>Your channel:</b> {my_ch}\n"
            "📢 <b>Partner channel:</b> {partner_ch}\n"
            "🎯 <b>Target:</b> {target} views (👀)\n\n"
            "👁 <b>Your post views:</b> {my_views}/{target} 👀\n"
            "👁 <b>Partner post views:</b> {partner_views}/{target} 👀\n"
            "👥 <b>Captured leads:</b> {my_leads}\n"
            "⏱ <b>24h Timer:</b> {timer}\n"
            "⚡ <b>Status:</b> {status}"
        ),
    },
    "deal_not_found": {
        "uz": "Bitim topilmadi.",
        "ru": "Сделка не найдена.",
        "en": "Deal not found.",
    },
    "deal_already_finished": {
        "uz": "Bitim allaqachon yakunlangan.",
        "ru": "Сделка уже завершена.",
        "en": "Deal is already completed.",
    },
    "deal_cancel_confirm": {
        "uz": "⚠️ <b>Bitimni to'xtatmoqchimisiz?</b>\nPostlar kanallardan darhol o'chiriladi.",
        "ru": "⚠️ <b>Прервать сделку?</b>\nПосты будут немедленно удалены из каналов.",
        "en": "⚠️ <b>Cancel this deal?</b>\nPosts will be deleted from channels immediately.",
    },
    "deal_cancelled": {
        "uz": "Bitim to'xtatildi.",
        "ru": "Сделка отменена.",
        "en": "Deal cancelled.",
    },

    # ==================== LEADS CRM ====================
    "leads_title": {
        "uz": (
            "|||| <b>Talabalar CRM Bazasi</b>\n\n"
            "👥 <b>Jami talabalar:</b> <code>{total}</code> ta\n"
            "⭐ <b>VIP imkoniyatlar:</b> {vip_status}\n\n"
            "<b>Kanallar bo'yicha:</b>\n{breakdown}"
        ),
        "ru": (
            "|||| <b>CRM База Лидов</b>\n\n"
            "👥 <b>Всего учеников:</b> <code>{total}</code>\n"
            "⭐ <b>VIP статус:</b> {vip_status}\n\n"
            "<b>По каналам:</b>\n{breakdown}"
        ),
        "en": (
            "|||| <b>Student Leads CRM</b>\n\n"
            "👥 <b>Total captured students:</b> <code>{total}</code>\n"
            "⭐ <b>VIP status:</b> {vip_status}\n\n"
            "<b>By channel:</b>\n{breakdown}"
        ),
    },
    "btn_export_csv": {
        "uz": "📥 Excel/CSV yuklab olish 💎",
        "ru": "📥 Скачать Excel/CSV 💎",
        "en": "📥 Export CSV/Excel 💎",
    },
    "vip_only_feature": {
        "uz": "💎 Bu imkoniyat faqat VIP foydalanuvchilar uchun!",
        "ru": "💎 Доступно только на тарифе VIP!",
        "en": "💎 Exclusive VIP feature!",
    },
    "no_leads_yet": {
        "uz": "Hali talabalar bazasi mavjud emas.",
        "ru": "База лидов пока пуста.",
        "en": "No student leads yet.",
    },

    # ==================== BROADCAST ====================
    "broadcast_title": {
        "uz": (
            "✉ <b>Lidlarga to'g'ridan-to'g'ri xabar (DM)</b>\n\n"
            "Talabalarning shaxsiy xabarlariga to'g'ridan-to'g'ri kurs taklifini yuborish.\n\n"
            "Auditoriyani tanlang:"
        ),
        "ru": (
            "✉ <b>Прямая рассылка лидам в ЛС</b>\n\n"
            "Отправка ваших предложений прямо в личные сообщения учеников.\n\n"
            "Выберите аудиторию:"
        ),
        "en": (
            "✉ <b>Direct DM Broadcast to Leads</b>\n\n"
            "Deliver course offers straight into students' private messages.\n\n"
            "Select target audience:"
        ),
    },

    # ==================== ADMIN ====================
    "admin_dashboard_title": {
        "uz": (
            "⊘ <b>Boshqaruv Paneli (SuperAdmin)</b>\n\n"
            "🤖 <b>Skaner:</b> @{scanner}\n"
            "👥 <b>Foydalanuvchilar:</b> {users} (Tasdiqlangan: {approved})\n"
            "💎 <b>VIP Foydalanuvchilar:</b> {vip}\n"
            "📢 <b>Kanallar:</b> {channels}\n"
            "⚡ <b>Havzadagi kanallar:</b> {pool}\n"
            "🤝 <b>Faol bitimlar:</b> {active_deals}\n"
            "📥 <b>Jami lidlar:</b> {leads}"
        ),
        "ru": (
            "⊘ <b>Панель Управления (SuperAdmin)</b>\n\n"
            "🤖 <b>Сканнер:</b> @{scanner}\n"
            "👥 <b>Пользователи:</b> {users} (Одобрено: {approved})\n"
            "💎 <b>VIP Пользователи:</b> {vip}\n"
            "📢 <b>Каналы:</b> {channels}\n"
            "⚡ <b>В пуле:</b> {pool}\n"
            "🤝 <b>Активные сделки:</b> {active_deals}\n"
            "📥 <b>Всего лидов:</b> {leads}"
        ),
        "en": (
            "⊘ <b>SuperAdmin Dashboard</b>\n\n"
            "🤖 <b>Scanner:</b> @{scanner}\n"
            "👥 <b>Users:</b> {users} (Approved: {approved})\n"
            "💎 <b>VIP Users:</b> {vip}\n"
            "📢 <b>Channels:</b> {channels}\n"
            "⚡ <b>Pool Channels:</b> {pool}\n"
            "🤝 <b>Active Deals:</b> {active_deals}\n"
            "📥 <b>Total Leads:</b> {leads}"
        ),
    },

    # ==================== MANDATORY SUBSCRIPTION ====================
    "mandatory_sub_prompt": {
        "uz": (
            "📢 <b>Rasmiy kanalimizga a'zo bo'ling!</b>\n\n"
            "EduSwap platformasidan foydalanish uchun rasmiy kanalimizga obuna bo'lishingiz lozim.\n\n"
            "Kanalga a'zo bo'lgach, pastdagi <b>Tekshirish</b> tugmasini bosing:"
        ),
        "ru": (
            "📢 <b>Подпишитесь на наш официальный канал!</b>\n\n"
            "Чтобы использовать платформу EduSwap, необходимо подписаться на наш канал обновлений.\n\n"
            "После подписки нажмите кнопку <b>Проверить</b> ниже:"
        ),
        "en": (
            "📢 <b>Join Our Official Channel!</b>\n\n"
            "To access the EduSwap platform, please subscribe to our official updates channel.\n\n"
            "After joining, tap the <b>Verify</b> button below:"
        ),
    },
    "sub_not_joined_alert": {
        "uz": "⚠️ Siz hali kanalga a'zo bo'lmadingiz! Iltimos, avval kanalga obuna bo'ling.",
        "ru": "⚠️ Вы ещё не подписались на канал! Пожалуйста, подпишитесь на канал.",
        "en": "⚠️ You have not joined the channel yet! Please subscribe first.",
    },
    "sub_confirmed_succ": {
        "uz": "✅ A'zolik tasdiqlandi! Xush kelibsiz.",
        "ru": "✅ Подписка подтверждена! Добро пожаловать.",
        "en": "✅ Subscription confirmed! Welcome.",
    },

    # ==================== CREATIVE FORMATS ====================
    "choose_creative_format": {
        "uz": (
            "📝 <b>Reklama formatini tanlang:</b>\n\n"
            "1️⃣ <b>Klassik Matn:</b> An'anaviy Telegram reklamasi — matn, emojilar va kanalingiz havolalari (faylsiz).\n\n"
            "2️⃣ <b>Sovg'ali / Faylli:</b> Matn + sovg'a fayli (PDF/ZIP/rasm) — talabalar a'zo bo'lgach avtomatik sovg'a beriladi."
        ),
        "ru": (
            "📝 <b>Выберите формат рекламного поста:</b>\n\n"
            "1️⃣ <b>Классический Текст:</b> Традиционная реклама в Telegram — текст, эмодзи и ссылки на ваш канал (без файлов).\n\n"
            "2️⃣ <b>С подарком / файлом:</b> Текст + обучающий файл (PDF/ZIP/фото) — ученики получают файл при подписке."
        ),
        "en": (
            "📝 <b>Select Ad Creative Format:</b>\n\n"
            "1️⃣ <b>Traditional Text Ad:</b> Standard Telegram promo — text, emojis, and your channel links (no files needed).\n\n"
            "2️⃣ <b>Lead Magnet Ad:</b> Text + study material file (PDF/ZIP/photo) — delivered to students upon joining."
        ),
    },
    "step_text_only_prompt": {
        "uz": (
            "📝 <b>Klassik reklama postingizni yuboring:</b>\n\n"
            "Matn ichida kanalingiz havolasi, sarlavhalar va kerakli ma'lumotlarni yozing.\n"
            "<i>(Xohlasangiz, matnga rasm yoki video biriktirib yuborishingiz mumkin)</i>"
        ),
        "ru": (
            "📝 <b>Отправьте ваш классический рекламный пост:</b>\n\n"
            "Добавьте текст, ссылки на ваш канал и любое форматирование.\n"
            "<i>(Вы также можете прикрепить одно фото или видео к тексту)</i>"
        ),
        "en": (
            "📝 <b>Send your traditional promotional post:</b>\n\n"
            "Include your channel link, formatting, and message.\n"
            "<i>(You may also attach a single photo or video to the text)</i>"
        ),
    },

    # ==================== REFERRAL SYSTEM (ANTI-NAKRUTKA) ====================
    "referral_dashboard": {
        "uz": (
            "👥 <b>Do'stlarni taklif qilish (Referal dasturi)</b>\n\n"
            "🔗 <b>Sizning shaxsiy taklif havolangiz:</b>\n"
            "<code>{link}</code>\n\n"
            "📊 <b>Ko'rsatkichlaringiz:</b>\n"
            "• 👤 <b>Jami o'tganlar:</b> {total} ta\n"
            "• 🎓 <b>Kanal qo'shgan ustozlar:</b> {qualified}/{target} ta\n\n"
            "🎁 <b>Mukofot:</b> {target} ta faol kanal egasini taklif qiling va <b>{days} kunlik bepul VIP</b> ga ega bo'ling!\n\n"
            "🛡 <i>Anti-Nakrutka: Soxta botlar yoki bo'sh akkauntlar hisoblanmaydi. Ball faqat taklif qilingan do'stingiz haqiqiy kanal qo'shganda beriladi!</i>"
        ),
        "ru": (
            "👥 <b>Пригласить коллег (Реферальная программа)</b>\n\n"
            "🔗 <b>Ваша личная ссылка:</b>\n"
            "<code>{link}</code>\n\n"
            "📊 <b>Ваш прогресс:</b>\n"
            "• 👤 <b>Всего переходов:</b> {total}\n"
            "• 🎓 <b>Учителей с каналом:</b> {qualified}/{target}\n\n"
            "🎁 <b>Награда:</b> Пригласите {target} владельцев каналов и получите <b>{days} дней VIP бесплатно</b>!\n\n"
            "🛡 <i>Анти-Накрутка: Фейковые боты не засчитываются. Балл начисляется только когда приглашенный добавляет реальный канал!</i>"
        ),
        "en": (
            "👥 <b>Invite Fellow Teachers (Referral Program)</b>\n\n"
            "🔗 <b>Your Personal Referral Link:</b>\n"
            "<code>{link}</code>\n\n"
            "📊 <b>Your Progress:</b>\n"
            "• 👤 <b>Total Clicks:</b> {total}\n"
            "• 🎓 <b>Verified Channel Owners:</b> {qualified}/{target}\n\n"
            "🎁 <b>Reward:</b> Invite {target} active channel owners to unlock <b>{days} Days of Free VIP</b>!\n\n"
            "🛡 <i>Anti-Nakrutka Shield: Spam bots and dummy accounts do not count. Only users who bind a real channel qualify!</i>"
        ),
    },
    "referral_reward_congrats": {
        "uz": (
            "👑 <b>Tabriklaymiz! Bepul VIP tarif faollashtirildi!</b>\n\n"
            "Siz {target} ta faol kanal egasini taklif qildingiz va <b>{days} kunlik VIP</b> ga ega bo'ldingiz!\n\n"
            "• ⚡ Cheksiz o'zaro reklamalar\n"
            "• ✉ Talabalarga shaxsiy xabar (DM Rassilka)\n"
            "• 📥 Lidlar bazasini Excel formatida yuklash\n"
            "• 👑 100% belgisiz toza postlar"
        ),
        "ru": (
            "👑 <b>Поздравляем! Бесплатный VIP активирован!</b>\n\n"
            "Вы пригласили {target} активных владельцев каналов и получили <b>{days} дней VIP</b>!\n\n"
            "• ⚡ Безлимитный взаимопиар\n"
            "• ✉ Рассылка в личные сообщения учеников\n"
            "• 📥 Выгрузка базы лидов в Excel\n"
            "• 👑 Чистые посты без водяных знаков"
        ),
        "en": (
            "👑 <b>Congratulations! Free VIP Status Activated!</b>\n\n"
            "You invited {target} active channel owners and earned <b>{days} Days of VIP</b>!\n\n"
            "• ⚡ Unlimited Auto-VP swaps\n"
            "• ✉ Direct DM Broadcast to students\n"
            "• 📥 1-Click Excel lead export\n"
            "• 👑 100% clean whitelabel posts"
        ),
    },

    # ==================== ANTI-CHEATING ALERTS ====================
    "anti_cheat_victim_alert": {
        "uz": (
            "🚨 <b>Diqqat! Sherik kanal qoidani buzdi!</b>\n\n"
            "Sherik kanal <b>{partner}</b> sizning reklama postingizni kelishilgan {target} ko'rishga yetmasdan oldin o'chirib yubordi!\n\n"
            "🛡 <i>Sizni himoya qilish maqsadida, sizning kanalingizdagi sherik posti ham avtomatik o'chirildi va bitim bekor qilindi.</i>"
        ),
        "ru": (
            "🚨 <b>Внимание! Нарушение со стороны партнера!</b>\n\n"
            "Канал-партнер <b>{partner}</b> удалил ваш рекламный пост до достижения {target} просмотров!\n\n"
            "🛡 <i>В целях вашей защиты рекламный пост партнера в вашем канале был также немедленно удален.</i>"
        ),
        "en": (
            "🚨 <b>Warning! Partner Policy Violation!</b>\n\n"
            "Partner channel <b>{partner}</b> deleted your promotional post before reaching the target {target} views!\n\n"
            "🛡 <i>To protect your channel, their post has been immediately deleted from your channel as well.</i>"
        ),
    },
    "anti_cheat_violator_alert": {
        "uz": (
            "⚠️ <b>Qoidabuzarlik qayd etildi!</b>\n\n"
            "Siz <b>{partner}</b> kanali reklama postini kelishilgan {target} ko'rishga yetmasdan oldin o'chirib yubordingiz!\n\n"
            "O'zaro kelishuv buzilganligi sababli bitim to'xtatildi va sherik kanaldan sizning postingiz ham olib tashlandi."
        ),
        "ru": (
            "⚠️ <b>Зафиксировано нарушение правил!</b>\n\n"
            "Вы удалили рекламный пост канала <b>{partner}</b> до достижения целевых {target} просмотров!\n\n"
            "Сделка аннулирована, ваш пост в партнерском канале также был удален."
        ),
        "en": (
            "⚠️ <b>Policy Violation Recorded!</b>\n\n"
            "You deleted the promotional post of <b>{partner}</b> before reaching {target} views!\n\n"
            "Due to this breach, the deal was cancelled and your post was also removed from the partner channel."
        ),
    },
}


def t(key: str, lang: str = "uz", **kwargs: Any) -> str:
    """Retrieve localized string with formatted kwargs."""
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    
    table = STRINGS.get(key, {})
    text = table.get(lang) or table.get("uz") or table.get("en") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
