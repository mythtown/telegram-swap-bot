import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    admin_ids: List[int] = field(
        default_factory=lambda: [
            int(x.strip())
            for x in os.getenv("ADMIN_IDS", "").split(",")
            if x.strip().isdigit()
        ]
    )
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
    )
    telegram_api_id: int = field(
        default_factory=lambda: int(os.getenv("TELEGRAM_API_ID", "0"))
    )
    telegram_api_hash: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_API_HASH", "")
    )
    scanner_username: str = field(
        default_factory=lambda: os.getenv("SCANNER_USERNAME", "")
    )
    support_username: str = field(
        default_factory=lambda: os.getenv("SUPPORT_USERNAME", "")
    )
    private_mode: bool = field(
        default_factory=lambda: os.getenv("PRIVATE_MODE", "false").lower() in ("true", "1", "yes")
    )
    mandatory_channel: str = field(
        default_factory=lambda: os.getenv("MANDATORY_CHANNEL", "")
    )
    referral_enabled: bool = field(
        default_factory=lambda: os.getenv("REFERRAL_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    referral_target: int = field(
        default_factory=lambda: int(os.getenv("REFERRAL_TARGET", "2"))
    )
    referral_reward_days: int = field(
        default_factory=lambda: int(os.getenv("REFERRAL_REWARD_DAYS", "7"))
    )
    referral_min_subs: int = field(
        default_factory=lambda: int(os.getenv("REFERRAL_MIN_SUBS", "50"))
    )
    matchmaking_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("MATCHMAKING_INTERVAL_SECONDS", "60"))
    )
    scanner_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("SCANNER_INTERVAL_SECONDS", "45"))
    )
    cleanup_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("CLEANUP_INTERVAL_SECONDS", "300"))
    )
    deal_timeout_hours: int = field(
        default_factory=lambda: int(os.getenv("DEAL_TIMEOUT_HOURS", "24"))
    )
    free_weekly_swap_limit: int = field(
        default_factory=lambda: int(os.getenv("FREE_WEEKLY_SWAP_LIMIT", "3"))
    )
    swap_cooldown_days: int = field(
        default_factory=lambda: int(os.getenv("SWAP_COOLDOWN_DAYS", "14"))
    )

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids


config = Config()
