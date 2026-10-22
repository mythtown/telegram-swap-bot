"""Time and Clock Utility for EduSwap.
Handles Uzbekistan (Tashkent, UTC+5) timezone, clock formatting,
cooldown timers, and 24h deal timers.
"""
from datetime import datetime, timedelta, timezone

# Uzbekistan Standard Time (Tashkent): UTC+5
TASHKENT_TZ = timezone(timedelta(hours=5))


def tashkent_now() -> datetime:
    """Returns current naive or aware datetime in Tashkent (UTC+5)."""
    return datetime.now(TASHKENT_TZ)


def format_clock(dt: datetime = None) -> str:
    """Formats current clock: HH:MM (Tashkent / UTC+5)."""
    if dt is None:
        dt = tashkent_now()
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc).astimezone(TASHKENT_TZ)
    return dt.strftime("%H:%M")


def is_within_posting_window(window: str) -> bool:
    """Checks whether current Tashkent time falls within channel's configured window.
    - 'evening': 18:00 - 22:00
    - 'morning': 09:00 - 13:00
    - 'anytime': 24/7
    """
    if window == "anytime" or not window:
        return True
    
    cur_hour = tashkent_now().hour
    if window == "evening":
        return 18 <= cur_hour < 22
    elif window == "morning":
        return 9 <= cur_hour < 13
    return True


def format_remaining_timer(seconds: float, lang: str = "uz") -> str:
    """Formats human-readable remaining time for rest periods or deal timeouts."""
    if seconds <= 0:
        if lang == "uz":
            return "✅ Cheklov yo'q (tayyor)"
        elif lang == "ru":
            return "✅ Без ограничений (готов)"
        else:
            return "✅ No restriction (ready)"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        if lang == "uz":
            return f"⏳ {hours} soat {minutes} daqiqa"
        elif lang == "ru":
            return f"⏳ {hours} ч. {minutes} мин."
        else:
            return f"⏳ {hours}h {minutes}m"
    else:
        if lang == "uz":
            return f"⏳ {minutes} daqiqa"
        elif lang == "ru":
            return f"⏳ {minutes} мин."
        else:
            return f"⏳ {minutes}m"
