from aiogram import Bot, F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud
from bot.database.models import User
from bot.keyboards.lead_kb import leads_menu_keyboard
from bot.locales.texts import t

router = Router(name="leads_router")


async def render_leads_dashboard(session: AsyncSession, current_user: User, lang: str):
    total_leads = await crud.get_student_leads_count(session, current_user.telegram_id)
    channels = await crud.get_channels_by_owner(session, current_user.telegram_id)

    vip_str = "Faol 🚀" if current_user.is_vip_active else t("btn_vip", lang)
    if lang == "ru":
        vip_str = "Активен 🚀" if current_user.is_vip_active else t("btn_vip", lang)
    elif lang == "en":
        vip_str = "Active 🚀" if current_user.is_vip_active else t("btn_vip", lang)

    breakdown_lines = []
    for ch in channels:
        ch_leads = await crud.get_student_leads_count(session, current_user.telegram_id, channel_id=ch.telegram_id)
        unit = "ta" if lang == "uz" else ("лидов" if lang == "ru" else "leads")
        breakdown_lines.append(f"• <b>{ch.title}:</b> {ch_leads} {unit}")

    empty_lbl = "Hozircha kanallar yo'q" if lang == "uz" else ("Каналы отсутствуют" if lang == "ru" else "No channels yet")
    breakdown_str = "\n".join(breakdown_lines) if breakdown_lines else empty_lbl

    text = t(
        "leads_title",
        lang,
        total=total_leads,
        vip_status=vip_str,
        breakdown=breakdown_str,
    )
    markup = leads_menu_keyboard(total_leads, current_user.is_vip_active, lang=lang)
    return text, markup


@router.callback_query(F.data == "menu:leads")
async def cb_leads_crm(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_leads_dashboard(session, current_user, lang)
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.message(F.text.in_(["|||| Statistika", "|||| Статистика", "|||| Statistics"]))
async def msg_leads_crm(
    message: Message,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    text, markup = await render_leads_dashboard(session, current_user, lang)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "leads:export_csv")
async def cb_export_leads_csv(
    callback: CallbackQuery,
    session: AsyncSession,
    current_user: User,
) -> None:
    lang = getattr(current_user, "language", "uz") or "uz"
    if not current_user.is_vip_active:
        await callback.answer(t("vip_only_feature", lang), show_alert=True)
        return

    csv_data = await crud.export_leads_csv(session, current_user.telegram_id)
    if not csv_data.strip():
        await callback.answer(t("no_leads_yet", lang), show_alert=True)
        return

    csv_bytes = csv_data.encode("utf-8-sig")
    file = BufferedInputFile(csv_bytes, filename=f"leads_{current_user.telegram_id}.csv")

    caption = "📥 <b>Talabalar CRM bazasi (Excel/CSV)</b>" if lang == "uz" else (
        "📥 <b>База лидов CRM (Excel/CSV)</b>" if lang == "ru" else "📥 <b>Student Leads CRM (Excel/CSV)</b>"
    )
    await callback.message.answer_document(
        document=file,
        caption=caption,
    )
    await callback.answer()
