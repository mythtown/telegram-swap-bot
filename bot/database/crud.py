import io
import csv
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from bot.config import config
from bot.database.models import (
    BroadcastLog,
    Channel,
    Creative,
    StudentLead,
    SwapDeal,
    SwapLead,
    SystemSetting,
    User,
    utc_now,
)


# ===================== USER CRUD =====================

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    full_name: str = "",
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    is_admin_user = config.is_admin(telegram_id)
    default_approval = is_admin_user or (not config.private_mode)

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            is_approved=default_approval,
            quota_reset_date=utc_now() + timedelta(days=7),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        if is_admin_user and not user.is_approved:
            user.is_approved = True

        if user.quota_reset_date and utc_now() >= user.quota_reset_date:
            user.swaps_this_week = 0
            user.quota_reset_date = utc_now() + timedelta(days=7)

        if user.username != username or user.full_name != full_name:
            user.username = username
            user.full_name = full_name
        await session.commit()
    return user


async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> Optional[User]:
    user = await get_user(session, telegram_id)
    if user:
        user.language = language
        await session.commit()
        await session.refresh(user)
    return user


async def set_user_approval(
    session: AsyncSession, telegram_id: int, is_approved: bool
) -> Optional[User]:
    user = await get_user(session, telegram_id)
    if user:
        user.is_approved = is_approved
        user.request_pending = False
        await session.commit()
        await session.refresh(user)
    return user


async def set_user_pending(
    session: AsyncSession, telegram_id: int, pending: bool
) -> Optional[User]:
    user = await get_user(session, telegram_id)
    if user:
        user.request_pending = pending
        await session.commit()
        await session.refresh(user)
    return user


async def set_user_vip(
    session: AsyncSession,
    telegram_id: int,
    is_vip: bool,
    days: Optional[int] = None,
) -> Optional[User]:
    user = await get_user(session, telegram_id)
    if not user:
        return None

    user.is_vip = is_vip
    if is_vip and days:
        user.vip_until = utc_now() + timedelta(days=days)
    elif not is_vip:
        user.vip_until = None
    await session.commit()
    await session.refresh(user)
    return user


async def increment_user_swaps(session: AsyncSession, telegram_id: int) -> None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if user:
        user.swaps_this_week += 1
        await session.commit()


async def reset_weekly_quotas(session: AsyncSession) -> int:
    stmt = update(User).values(
        swaps_this_week=0,
        quota_reset_date=utc_now() + timedelta(days=7),
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount


# ===================== CHANNEL CRUD =====================

async def get_channel(session: AsyncSession, channel_id: int) -> Optional[Channel]:
    stmt = (
        select(Channel)
        .options(selectinload(Channel.creative), selectinload(Channel.owner))
        .where(Channel.telegram_id == channel_id)
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def get_channels_by_owner(
    session: AsyncSession, owner_id: int
) -> List[Channel]:
    stmt = (
        select(Channel)
        .options(selectinload(Channel.creative))
        .where(Channel.owner_id == owner_id)
        .order_by(Channel.created_at.desc())
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def create_or_update_channel(
    session: AsyncSession,
    telegram_id: int,
    owner_id: int,
    title: str,
    username: Optional[str] = None,
    invite_link: Optional[str] = None,
    is_verified: bool = True,
) -> Channel:
    channel = await get_channel(session, telegram_id)
    if not channel:
        channel = Channel(
            telegram_id=telegram_id,
            owner_id=owner_id,
            title=title,
            username=username,
            invite_link=invite_link,
            is_verified=is_verified,
        )
        session.add(channel)
    else:
        channel.owner_id = owner_id
        channel.title = title
        channel.username = username
        if invite_link:
            channel.invite_link = invite_link
        channel.is_verified = is_verified
    await session.commit()
    await session.refresh(channel)
    return channel


async def set_channel_schedule(
    session: AsyncSession,
    channel_id: int,
    posting_window: str,
    cooldown_hours: int,
) -> Optional[Channel]:
    channel = await get_channel(session, channel_id)
    if channel:
        channel.posting_window = posting_window
        channel.swap_cooldown_hours = cooldown_hours
        await session.commit()
        await session.refresh(channel)
    return channel


async def set_channel_pool_status(
    session: AsyncSession, channel_id: int, is_in_pool: bool
) -> Optional[Channel]:
    channel = await get_channel(session, channel_id)
    if channel:
        channel.is_in_pool = is_in_pool
        await session.commit()
        await session.refresh(channel)
    return channel


async def set_channel_tier(
    session: AsyncSession, channel_id: int, tier: int
) -> Optional[Channel]:
    channel = await get_channel(session, channel_id)
    if channel:
        channel.target_tier = tier
        await session.commit()
        await session.refresh(channel)
    return channel


async def delete_channel(session: AsyncSession, channel_id: int) -> bool:
    channel = await get_channel(session, channel_id)
    if channel:
        await session.delete(channel)
        await session.commit()
        return True
    return False


# ===================== CREATIVE CRUD =====================

async def get_creative_by_channel(
    session: AsyncSession, channel_id: int
) -> Optional[Creative]:
    stmt = select(Creative).where(Creative.channel_id == channel_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def save_or_update_creative(
    session: AsyncSession,
    channel_id: int,
    ad_text: str,
    media_type: str = "text",
    media_file_id: Optional[str] = None,
    button_text: str = "🎁 Claim Free Gift & Join",
    gift_type: str = "document",
    gift_file_id: Optional[str] = None,
    gift_name: Optional[str] = None,
    gift_text_content: Optional[str] = None,
    gift_title: str = "Exclusive Study Materials",
    creative_type: str = "text",
) -> Creative:
    creative = await get_creative_by_channel(session, channel_id)
    if not creative:
        creative = Creative(
            channel_id=channel_id,
            creative_type=creative_type,
            ad_text=ad_text,
            media_type=media_type,
            media_file_id=media_file_id,
            button_text=button_text,
            gift_type=gift_type,
            gift_file_id=gift_file_id,
            gift_name=gift_name,
            gift_text_content=gift_text_content,
            gift_title=gift_title,
        )
        session.add(creative)
    else:
        creative.creative_type = creative_type
        creative.ad_text = ad_text
        creative.media_type = media_type
        creative.media_file_id = media_file_id
        creative.button_text = button_text
        creative.gift_type = gift_type
        if gift_file_id is not None:
            creative.gift_file_id = gift_file_id
        if gift_name is not None:
            creative.gift_name = gift_name
        if gift_text_content is not None:
            creative.gift_text_content = gift_text_content
        if gift_title:
            creative.gift_title = gift_title
    await session.commit()
    await session.refresh(creative)
    return creative


# ===================== SWAP DEAL CRUD =====================

async def create_swap_deal(
    session: AsyncSession,
    deal_id: str,
    channel_a_id: int,
    channel_b_id: int,
    target_views: int,
    invite_link_a: str,
    invite_link_b: str,
    post_msg_id_in_a: Optional[int] = None,
    post_msg_id_in_b: Optional[int] = None,
) -> SwapDeal:
    deal = SwapDeal(
        id=deal_id,
        channel_a_id=channel_a_id,
        channel_b_id=channel_b_id,
        target_views=target_views,
        target_joins=0,
        invite_link_a=invite_link_a,
        invite_link_b=invite_link_b,
        post_msg_id_in_a=post_msg_id_in_a,
        post_msg_id_in_b=post_msg_id_in_b,
        status="ACTIVE",
    )
    session.add(deal)
    await session.commit()
    await session.refresh(deal)
    return deal


async def get_deal_by_id(
    session: AsyncSession, deal_id: str
) -> Optional[SwapDeal]:
    stmt = (
        select(SwapDeal)
        .options(
            selectinload(SwapDeal.channel_a).selectinload(Channel.owner),
            selectinload(SwapDeal.channel_a).selectinload(Channel.creative),
            selectinload(SwapDeal.channel_b).selectinload(Channel.owner),
            selectinload(SwapDeal.channel_b).selectinload(Channel.creative),
        )
        .where(SwapDeal.id == deal_id)
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def get_active_deals(session: AsyncSession) -> List[SwapDeal]:
    stmt = (
        select(SwapDeal)
        .options(
            selectinload(SwapDeal.channel_a).selectinload(Channel.owner),
            selectinload(SwapDeal.channel_b).selectinload(Channel.owner),
        )
        .where(SwapDeal.status == "ACTIVE")
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_active_deal_by_invite_link(
    session: AsyncSession, invite_link_url: str
) -> Optional[Tuple[SwapDeal, str]]:
    clean_url = invite_link_url.strip()
    stmt = (
        select(SwapDeal)
        .options(
            selectinload(SwapDeal.channel_a).selectinload(Channel.owner),
            selectinload(SwapDeal.channel_a).selectinload(Channel.creative),
            selectinload(SwapDeal.channel_b).selectinload(Channel.owner),
            selectinload(SwapDeal.channel_b).selectinload(Channel.creative),
        )
        .where(
            and_(
                SwapDeal.status == "ACTIVE",
                or_(
                    SwapDeal.invite_link_a == clean_url,
                    SwapDeal.invite_link_b == clean_url,
                ),
            )
        )
    )
    res = await session.execute(stmt)
    deal = res.scalar_one_or_none()
    if not deal:
        return None

    side = "A" if deal.invite_link_a == clean_url else "B"
    return deal, side


async def get_active_deal_for_channel(
    session: AsyncSession, channel_id: int
) -> Optional[SwapDeal]:
    stmt = (
        select(SwapDeal)
        .where(
            and_(
                SwapDeal.status == "ACTIVE",
                or_(
                    SwapDeal.channel_a_id == channel_id,
                    SwapDeal.channel_b_id == channel_id,
                ),
            )
        )
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def get_active_deals_for_owner(
    session: AsyncSession, owner_id: int
) -> List[SwapDeal]:
    stmt = (
        select(SwapDeal)
        .options(
            selectinload(SwapDeal.channel_a),
            selectinload(SwapDeal.channel_b),
        )
        .join(Channel, or_(SwapDeal.channel_a_id == Channel.telegram_id, SwapDeal.channel_b_id == Channel.telegram_id))
        .where(
            and_(
                SwapDeal.status == "ACTIVE",
                Channel.owner_id == owner_id,
            )
        )
        .distinct()
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_stale_active_deals(
    session: AsyncSession, max_hours: int = 24
) -> List[SwapDeal]:
    threshold = utc_now() - timedelta(hours=max_hours)
    stmt = (
        select(SwapDeal)
        .options(
            selectinload(SwapDeal.channel_a).selectinload(Channel.owner),
            selectinload(SwapDeal.channel_b).selectinload(Channel.owner),
        )
        .where(
            and_(
                SwapDeal.status == "ACTIVE",
                SwapDeal.started_at <= threshold,
            )
        )
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def update_deal_post_deletion(
    session: AsyncSession,
    deal_id: str,
    deleted_post_in_a: Optional[bool] = None,
    deleted_post_in_b: Optional[bool] = None,
) -> Optional[SwapDeal]:
    deal = await get_deal_by_id(session, deal_id)
    if not deal:
        return None
    if deleted_post_in_a is not None:
        deal.post_a_deleted = deleted_post_in_a
    if deleted_post_in_b is not None:
        deal.post_b_deleted = deleted_post_in_b
    await session.commit()
    await session.refresh(deal)
    return deal


async def complete_or_close_deal(
    session: AsyncSession, deal_id: str, status: str
) -> Optional[SwapDeal]:
    deal = await get_deal_by_id(session, deal_id)
    if not deal:
        return None
    deal.status = status
    deal.finished_at = utc_now()

    # Set last_swap_finished_at on both channels to enforce anti-spam cooldown!
    if deal.channel_a:
        deal.channel_a.last_swap_finished_at = utc_now()
    if deal.channel_b:
        deal.channel_b.last_swap_finished_at = utc_now()

    await session.commit()
    await session.refresh(deal)
    return deal


async def has_recent_deal_between_channels(
    session: AsyncSession, channel_a_id: int, channel_b_id: int, days: int = 14
) -> bool:
    threshold = utc_now() - timedelta(days=days)
    stmt = (
        select(SwapDeal.id)
        .where(
            and_(
                SwapDeal.started_at >= threshold,
                or_(
                    and_(SwapDeal.channel_a_id == channel_a_id, SwapDeal.channel_b_id == channel_b_id),
                    and_(SwapDeal.channel_a_id == channel_b_id, SwapDeal.channel_b_id == channel_a_id),
                ),
            )
        )
        .limit(1)
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none() is not None


async def get_eligible_pool_channels(
    session: AsyncSession, tier: int
) -> List[Channel]:
    """Returns channels that are in pool, verified, have valid creative, and respect anti-spam cooldowns."""
    active_deals_subquery = (
        select(SwapDeal.channel_a_id)
        .where(SwapDeal.status == "ACTIVE")
        .union(select(SwapDeal.channel_b_id).where(SwapDeal.status == "ACTIVE"))
    )

    current_hour_utc = datetime.now(timezone.utc).hour

    stmt = (
        select(Channel)
        .options(selectinload(Channel.creative), selectinload(Channel.owner))
        .join(Channel.creative)
        .join(Channel.owner)
        .where(
            and_(
                Channel.is_in_pool.is_(True),
                Channel.is_verified.is_(True),
                Channel.target_tier == tier,
                Creative.ad_text.isnot(None),
                or_(
                    Creative.gift_file_id.isnot(None),
                    Creative.gift_text_content.isnot(None),
                ),
                Channel.telegram_id.not_in(active_deals_subquery),
            )
        )
    )
    res = await session.execute(stmt)
    channels = list(res.scalars().all())

    eligible = []
    for ch in channels:
        # 1. Anti-Spam Channel Cooldown Check
        if ch.last_swap_finished_at and ch.swap_cooldown_hours > 0:
            cooldown_expiry = ch.last_swap_finished_at + timedelta(hours=ch.swap_cooldown_hours)
            if utc_now() < cooldown_expiry:
                continue  # Channel is resting to avoid spamming subscribers

        # 2. Posting Window Check (e.g. Evening: 18-22 Tashkent time, Morning: 09-13, or Anytime)
        from bot.services.time_utils import is_within_posting_window
        if not is_within_posting_window(ch.posting_window):
            continue

        eligible.append(ch)

    return eligible


# ===================== LEAD & ANTI-CHEAT CRUD =====================

async def record_swap_lead_if_new(
    session: AsyncSession,
    swap_id: str,
    channel_id: int,
    student_telegram_id: int,
) -> bool:
    stmt = select(SwapLead).where(
        and_(
            SwapLead.swap_id == swap_id,
            SwapLead.channel_id == channel_id,
            SwapLead.student_telegram_id == student_telegram_id,
        )
    )
    res = await session.execute(stmt)
    if res.scalar_one_or_none():
        return False

    lead = SwapLead(
        swap_id=swap_id,
        channel_id=channel_id,
        student_telegram_id=student_telegram_id,
    )
    session.add(lead)
    await session.commit()
    return True


async def save_student_lead(
    session: AsyncSession,
    owner_id: int,
    channel_id: int,
    student_telegram_id: int,
    student_username: Optional[str] = None,
    student_name: Optional[str] = None,
    pdf_sent: bool = False,
) -> StudentLead:
    stmt = select(StudentLead).where(
        and_(
            StudentLead.channel_id == channel_id,
            StudentLead.student_telegram_id == student_telegram_id,
        )
    )
    res = await session.execute(stmt)
    lead = res.scalar_one_or_none()

    if not lead:
        lead = StudentLead(
            owner_id=owner_id,
            channel_id=channel_id,
            student_telegram_id=student_telegram_id,
            student_username=student_username,
            student_name=student_name,
            pdf_sent=pdf_sent,
            is_active=True,
        )
        session.add(lead)
    else:
        if student_username:
            lead.student_username = student_username
        if student_name:
            lead.student_name = student_name
        if pdf_sent:
            lead.pdf_sent = True
        lead.is_active = True

    await session.commit()
    await session.refresh(lead)
    return lead


async def mark_lead_pdf_sent(
    session: AsyncSession, channel_id: int, student_telegram_id: int
) -> None:
    stmt = (
        update(StudentLead)
        .where(
            and_(
                StudentLead.channel_id == channel_id,
                StudentLead.student_telegram_id == student_telegram_id,
            )
        )
        .values(pdf_sent=True)
    )
    await session.execute(stmt)
    await session.commit()


async def mark_lead_inactive(
    session: AsyncSession, student_telegram_id: int
) -> None:
    stmt = (
        update(StudentLead)
        .where(StudentLead.student_telegram_id == student_telegram_id)
        .values(is_active=False)
    )
    await session.execute(stmt)
    await session.commit()


async def get_student_leads_by_owner(
    session: AsyncSession, owner_id: int, channel_id: Optional[int] = None
) -> List[StudentLead]:
    stmt = (
        select(StudentLead)
        .options(selectinload(StudentLead.channel))
        .where(
            and_(
                StudentLead.owner_id == owner_id,
                StudentLead.is_active.is_(True),
            )
        )
    )
    if channel_id:
        stmt = stmt.where(StudentLead.channel_id == channel_id)
    stmt = stmt.order_by(StudentLead.created_at.desc())
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_student_leads_count(
    session: AsyncSession, owner_id: int, channel_id: Optional[int] = None
) -> int:
    stmt = select(func.count(StudentLead.id)).where(
        and_(
            StudentLead.owner_id == owner_id,
            StudentLead.is_active.is_(True),
        )
    )
    if channel_id:
        stmt = stmt.where(StudentLead.channel_id == channel_id)
    res = await session.execute(stmt)
    return res.scalar_one() or 0


async def export_leads_csv(
    session: AsyncSession, owner_id: int, channel_id: Optional[int] = None
) -> str:
    """Exports all student leads into a CSV string for VIP teachers."""
    leads = await get_student_leads_by_owner(session, owner_id, channel_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Full Name", "Username", "Channel Name", "Gift Claimed", "Date Joined (UTC)"])

    for l in leads:
        writer.writerow([
            l.student_telegram_id,
            l.student_name or "",
            f"@{l.student_username}" if l.student_username else "",
            l.channel.title if l.channel else "",
            "Yes" if l.pdf_sent else "No",
            l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "",
        ])
    return output.getvalue()


async def log_broadcast(
    session: AsyncSession,
    owner_id: int,
    channel_id: Optional[int],
    total: int,
    sent: int,
    failed: int,
) -> BroadcastLog:
    log_entry = BroadcastLog(
        owner_id=owner_id,
        channel_id=channel_id,
        total_targets=total,
        sent_count=sent,
        failed_count=failed,
    )
    session.add(log_entry)
    await session.commit()
    return log_entry


# ===================== GLOBAL STATS =====================

async def get_global_stats(session: AsyncSession) -> dict:
    users_count = await session.scalar(select(func.count(User.telegram_id))) or 0
    approved_count = (
        await session.scalar(
            select(func.count(User.telegram_id)).where(User.is_approved.is_(True))
        )
        or 0
    )
    vip_count = (
        await session.scalar(
            select(func.count(User.telegram_id)).where(User.is_vip.is_(True))
        )
        or 0
    )
    channels_count = await session.scalar(select(func.count(Channel.telegram_id))) or 0
    pool_channels_count = (
        await session.scalar(
            select(func.count(Channel.telegram_id)).where(Channel.is_in_pool.is_(True))
        )
        or 0
    )
    active_deals = (
        await session.scalar(
            select(func.count(SwapDeal.id)).where(SwapDeal.status == "ACTIVE")
        )
        or 0
    )
    completed_deals = (
        await session.scalar(
            select(func.count(SwapDeal.id)).where(SwapDeal.status == "COMPLETED")
        )
        or 0
    )
    total_leads = await session.scalar(select(func.count(StudentLead.id))) or 0

    return {
        "users": users_count,
        "approved_users": approved_count,
        "vip_users": vip_count,
        "channels": channels_count,
        "pool_channels": pool_channels_count,
        "active_deals": active_deals,
        "completed_deals": completed_deals,
        "total_leads": total_leads,
    }


# ===================== SYSTEM SETTINGS =====================

async def get_system_setting(session: AsyncSession, key: str, default: str = "") -> str:
    stmt = select(SystemSetting).where(SystemSetting.key == key)
    res = await session.execute(stmt)
    setting = res.scalar_one_or_none()
    return setting.value if setting else default


async def set_system_setting(session: AsyncSession, key: str, value: str) -> SystemSetting:
    stmt = select(SystemSetting).where(SystemSetting.key == key)
    res = await session.execute(stmt)
    setting = res.scalar_one_or_none()
    if setting:
        setting.value = value
    else:
        setting = SystemSetting(key=key, value=value)
        session.add(setting)
    await session.commit()
    await session.refresh(setting)
    return setting


# ===================== REFERRAL SYSTEM (ANTI-NAKRUTKA) =====================

async def record_referral_invitation(
    session: AsyncSession,
    new_user_id: int,
    referrer_id: int,
) -> bool:
    """Anti-Nakrutka: Records an invite if new_user is not self, has no referrer, and referrer exists."""
    if new_user_id == referrer_id:
        return False
    user = await get_user(session, new_user_id)
    if not user or user.referred_by_id:
        return False
    referrer = await get_user(session, referrer_id)
    if not referrer:
        return False

    user.referred_by_id = referrer_id
    referrer.referrals_count = (referrer.referrals_count or 0) + 1
    await session.commit()
    return True


async def check_and_qualify_referral(
    session: AsyncSession,
    user_id: int,
    channel_subscribers: int,
    min_subs: int = 50,
) -> Optional[dict]:
    """Anti-Nakrutka Shield: Referral is ONLY qualified when the invited user binds a real channel with >= min_subs.
    Returns details if referrer unlocked a VIP reward."""
    user = await get_user(session, user_id)
    if not user or not user.referred_by_id or user.has_qualified_referral:
        return None

    if channel_subscribers < min_subs:
        return None

    user.has_qualified_referral = True
    referrer = await get_user(session, user.referred_by_id)
    if not referrer:
        await session.commit()
        return None

    referrer.qualified_referrals_count = (referrer.qualified_referrals_count or 0) + 1

    target_str = await get_system_setting(session, "referral_target", str(config.referral_target))
    days_str = await get_system_setting(session, "referral_reward_days", str(config.referral_reward_days))
    target = int(target_str) if target_str.isdigit() else config.referral_target
    days = int(days_str) if days_str.isdigit() else config.referral_reward_days

    vip_awarded = False
    if referrer.qualified_referrals_count >= target:
        await set_user_vip(session, referrer.telegram_id, is_vip=True, days=days)
        vip_awarded = True
    else:
        await session.commit()

    return {
        "referrer_id": referrer.telegram_id,
        "referrer_lang": getattr(referrer, "language", "uz") or "uz",
        "qualified_count": referrer.qualified_referrals_count,
        "target": target,
        "days": days,
        "vip_awarded": vip_awarded,
    }

