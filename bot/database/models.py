from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database.session import Base


def utc_now() -> datetime:
    """Returns naive UTC datetime for standard database compatibility across SQLite and PostgreSQL."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    language: Mapped[Optional[str]] = mapped_column(String(8), nullable=True, default=None)  # 'uz', 'ru', 'en' or None if new
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)  # Public access default
    request_pending: Mapped[bool] = mapped_column(Boolean, default=False)
    vip_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    swaps_this_week: Mapped[int] = mapped_column(Integer, default=0)
    quota_reset_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    referred_by_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    referrals_count: Mapped[int] = mapped_column(Integer, default=0)
    qualified_referrals_count: Mapped[int] = mapped_column(Integer, default=0)
    has_qualified_referral: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    channels: Mapped[list["Channel"]] = relationship("Channel", back_populates="owner", cascade="all, delete-orphan")
    student_leads: Mapped[list["StudentLead"]] = relationship("StudentLead", back_populates="owner")

    @property
    def is_vip_active(self) -> bool:
        if not self.is_vip:
            return False
        if self.vip_until is None:
            return True
        vip_dt = self.vip_until
        if vip_dt.tzinfo is not None:
            vip_dt = vip_dt.replace(tzinfo=None)
        return vip_dt > utc_now()


class Channel(Base):
    __tablename__ = "channels"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    invite_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_tier: Mapped[int] = mapped_column(Integer, default=200)  # Views: 100, 150, 200, 250, 500, 1000...
    is_in_pool: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Anti-Spam & Posting Schedule Controls
    posting_window: Mapped[str] = mapped_column(String(32), default="anytime")  # 'anytime', 'evening' (18-22), 'morning' (09-13)
    swap_cooldown_hours: Mapped[int] = mapped_column(Integer, default=6)  # Rest period after a swap
    last_swap_finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    manual_confirm_required: Mapped[bool] = mapped_column(Boolean, default=False)  # Require 1-click launch approval
    
    # VIP Automated 24h Pitch Funnel (Auto-seller)
    auto_pitch_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    owner: Mapped["User"] = relationship("User", back_populates="channels")
    creative: Mapped[Optional["Creative"]] = relationship("Creative", back_populates="channel", uselist=False, cascade="all, delete-orphan")
    leads: Mapped[list["StudentLead"]] = relationship("StudentLead", back_populates="channel", cascade="all, delete-orphan")


class Creative(Base):
    __tablename__ = "creatives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.telegram_id", ondelete="CASCADE"), unique=True)
    creative_type: Mapped[str] = mapped_column(String(16), default="text")  # 'text' (Traditional Text) or 'lead_magnet'
    ad_text: Mapped[str] = mapped_column(Text)
    media_type: Mapped[str] = mapped_column(String(16), default="text")  # 'text', 'photo', 'video'
    media_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    button_text: Mapped[str] = mapped_column(String(64), default="🎁 Claim Free Gift & Join")
    
    # Flexible Lead Magnet: Supports PDF, ZIP, RAR, DOCX, Video, Photo, or Text/Links!
    gift_type: Mapped[str] = mapped_column(String(16), default="document")  # 'document', 'photo', 'video', 'audio', 'text'
    gift_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gift_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gift_text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gift_title: Mapped[str] = mapped_column(String(255), default="Exclusive Study Materials")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    channel: Mapped["Channel"] = relationship("Channel", back_populates="creative")


class SwapDeal(Base):
    __tablename__ = "swap_deals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID str
    channel_a_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.telegram_id"))
    channel_b_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.telegram_id"))
    target_views: Mapped[int] = mapped_column(Integer, default=200)
    views_a_received: Mapped[int] = mapped_column(Integer, default=0)
    views_b_received: Mapped[int] = mapped_column(Integer, default=0)
    target_joins: Mapped[int] = mapped_column(Integer, default=0)
    joins_a_received: Mapped[int] = mapped_column(Integer, default=0)
    joins_b_received: Mapped[int] = mapped_column(Integer, default=0)
    invite_link_a: Mapped[str] = mapped_column(String(255))
    invite_link_b: Mapped[str] = mapped_column(String(255))
    post_msg_id_in_a: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    post_msg_id_in_b: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    post_a_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    post_b_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, COMPLETED, EXPIRED, CANCELLED
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    channel_a: Mapped["Channel"] = relationship("Channel", foreign_keys=[channel_a_id])
    channel_b: Mapped["Channel"] = relationship("Channel", foreign_keys=[channel_b_id])
    leads: Mapped[list["SwapLead"]] = relationship("SwapLead", back_populates="swap", cascade="all, delete-orphan")


class SwapLead(Base):
    __tablename__ = "swap_leads"
    __table_args__ = (
        UniqueConstraint("swap_id", "channel_id", "student_telegram_id", name="uq_swap_channel_student"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    swap_id: Mapped[str] = mapped_column(String(36), ForeignKey("swap_deals.id", ondelete="CASCADE"))
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.telegram_id"))
    student_telegram_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    swap: Mapped["SwapDeal"] = relationship("SwapDeal", back_populates="leads")


class StudentLead(Base):
    __tablename__ = "student_leads"
    __table_args__ = (
        UniqueConstraint("channel_id", "student_telegram_id", name="uq_channel_student_lead"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.telegram_id", ondelete="CASCADE"))
    student_telegram_id: Mapped[int] = mapped_column(BigInteger)
    student_username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    student_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pdf_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    pitch_sent: Mapped[bool] = mapped_column(Boolean, default=False)  # Automated 24h follow-up sales pitch
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    owner: Mapped["User"] = relationship("User", back_populates="student_leads")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="leads")


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(BigInteger)
    channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    total_targets: Mapped[int] = mapped_column(Integer)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

