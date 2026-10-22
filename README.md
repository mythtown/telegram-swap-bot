# 📚 EduSwap: Automated Telegram Cross-Promotion & Student Lead Capture Bot

An enterprise-grade, fully automated Telegram cross-promotion (**Vzaimopiar / VP**) and student lead generation bot tailored specifically for educators, CEFR/IELTS teachers, tutoring centers, and educational Telegram channel administrators.

Built with **Python 3.11+**, **aiogram 3.x**, **SQLAlchemy 2.0 (Async)**, **APScheduler**, and a dedicated **Telethon MTProto Eye-Icon View Scanner**.

---

## 🌟 Key Features

### 1. 🔒 Private "Teacher-Only" Access Gate
- Prevents public spam and unauthorized use.
- When new users enter, they submit a verification application.
- SuperAdmins receive an instant interactive notification with **[Approve]** and **[Reject]** buttons, or can use `/whitelist <user_id>`.

### 2. 👁 Real-Time Eye-Icon View Scanner (MTProto)
- Swaps are negotiated strictly on **actual post views (the eye icon)**: `100`, `150`, `200`, `250`, `300`, `400`, `500`, `600`, `800`, `1000`, `1500`, `2000` views.
- Channel owners guarantee reach and impressions—not fickle click-through rates.
- A dedicated Telethon MTProto scanner account reads the exact `message.views` counter every 45 seconds.
- The exact moment `views >= target_views`, both promotional posts are **instantly auto-deleted** to keep channels clean.

### 3. 🎁 Universal File & Student Lead Magnet Engine
- Teachers can upload free educational gifts in **any format**: PDF books, ZIP archives, high-resolution study guides, audio listening tracks, videos, or formatted text.
- Students must tap a special Telegram **Request to Join** link. When they subscribe, the bot automatically delivers their promised study material and captures them permanently into the teacher's **Student Leads CRM**.

### 4. 🌐 3-Language Localization (Uzbek / Russian / English)
- **First-Time Start Prompt:** Minimal, compact language selection:
  ```text
  🌐 Uzb / Rus / Eng:
  [ 🇺🇿 O'zbekcha ] [ 🇷🇺 Русский ] [ 🇬🇧 English ]
  ```
- 100% pure localization across all menus, buttons, notifications, and wizard prompts with zero mixed-language leakage.
- Users can switch their language anytime via `⚙ Sozlamalar` or `/lang`.

### 5. 🕒 Tashkent Peak-Hours Time Window & Rest Timers
- Matches channels only during peak study hours in Uzbekistan (**09:00–13:00** and **18:00–22:00** Tashkent UTC+5).
- Enforces an automated rest cooldown (default: 14 days) between identical channel pairs to protect subscribers from ad fatigue.
- Stale deal garbage collector auto-cancels and deletes ads if target views are not fulfilled within 24 hours.

### 6. 👑 VIP Monetization Tier
- **Free Tier:** 2–3 swaps per week, watermarked posts, basic lead counter.
- **VIP Superpowers:**
  - ⚡ **Unlimited Swaps:** No weekly quotas.
  - ✉ **Direct DM Broadcast:** Message all captured student leads directly in their private chats with 80%+ open rates.
  - 📥 **1-Click Excel/CSV Export:** Download full student lead contact lists with timestamps and channel source.
  - 👑 **100% Whitelabel Posts:** No bot branding or watermarks on promotional creatives.
- SuperAdmins can grant VIP via `/grant_vip <user_id> [days]` or through the interactive `⊘ Admin panel`.

### 7. ✉ Direct Support & Partnership Integration
- Built-in `✉ Aloqa / Support` button connects channel owners directly to the administrator for questions, custom agreements, or inquiries.

---

## 🏗 Project Architecture

```text
├── bot/
│   ├── config.py                 # Environment variables and app configuration
│   ├── database/
│   │   ├── models.py             # SQLAlchemy async models (User, Channel, Deal, Lead, Creative)
│   │   ├── crud.py               # Database CRUD operations and analytics
│   │   └── session.py            # Async engine and session factory
│   ├── handlers/
│   │   ├── start.py              # /start, initial language selector, teacher gate
│   │   ├── channels.py           # Channel binding, permission verification, schedule viewer
│   │   ├── creatives.py          # Ad post builder with PDF/ZIP/Media support
│   │   ├── pool.py               # View tiers and Auto-VP pool participation
│   │   ├── deals.py              # Active deals, live progress counters, 24h countdown
│   │   ├── leads.py              # Lead CRM, subscriber verification, CSV export
│   │   ├── broadcast.py          # VIP DM broadcast ("Rassilka") engine
│   │   ├── admin.py              # SuperAdmin panel, metrics dashboard, VIP management
│   │   └── settings.py           # User preferences and language switching
│   ├── keyboards/
│   │   ├── common.py             # 2-column reply keyboards with geometric icons
│   │   ├── channel_kb.py         # Channel management inline buttons
│   │   ├── creative_kb.py        # Ad post format selectors
│   │   ├── deal_kb.py            # Deal tracking buttons
│   │   ├── lead_kb.py            # Student lead CRM buttons
│   │   └── admin_kb.py           # SuperAdmin control buttons
│   ├── locales/
│   │   └── texts.py              # Complete Uzbek, Russian, and English dictionary
│   ├── services/
│   │   ├── swap_engine.py        # Automated matchmaking and parity algorithms
│   │   ├── view_scanner.py       # Telethon MTProto eye-icon view scanner
│   │   └── time_utils.py         # Tashkent UTC+5 clock and posting window calculators
│   └── states/
│       └── states.py             # Aiogram Finite State Machines (FSM)
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore file for secrets and virtualenv
├── main.py                       # Bot entrypoint & APScheduler daemon
├── requirements.txt              # Production Python dependencies
└── README.md                     # Comprehensive documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+** installed on Linux / macOS / Windows.
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather).
- Telegram MTProto API Credentials (`api_id` and `api_hash`) from [my.telegram.org](https://my.telegram.org).

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/eduswap-telegram-bot.git
cd eduswap-telegram-bot
```

### 3. Create a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your values:
```env
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567
ADMIN_IDS=123456789,987654321
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_telegram_api_hash_here
SCANNER_USERNAME=your_telethon_account_username
SUPPORT_USERNAME=your_personal_username
PRIVATE_MODE=true
DATABASE_URL=sqlite+aiosqlite:///bot.db
```

### 6. Initialize Telethon Scanner Session
Run the scanner session generator once to authenticate your scanner account via Telegram SMS/code:
```bash
python3 -c "from telethon.sync import TelegramClient; client = TelegramClient('scanner_session', int('$TELEGRAM_API_ID'), '$TELEGRAM_API_HASH'); client.start(); print('Scanner session authenticated successfully!')"
```

### 7. Run the Bot
```bash
python3 main.py
```

---

## 🛠 Production Deployment (Systemd)

For 24/7 background operation on an Ubuntu/Debian VPS:

1. Create a service file:
```bash
sudo nano /etc/systemd/system/telegram_swap_bot.service
```

2. Paste the configuration:
```ini
[Unit]
Description=EduSwap Telegram Bot Daemon
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/eduswap-telegram-bot
ExecStart=/home/ubuntu/eduswap-telegram-bot/.venv/bin/python3 /home/ubuntu/eduswap-telegram-bot/main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram_swap_bot
sudo systemctl start telegram_swap_bot
sudo systemctl status telegram_swap_bot
```

---

## 👑 Administrator Commands

| Command | Description |
| :--- | :--- |
| `/admin` | Open interactive SuperAdmin dashboard with real-time statistics |
| `/whitelist <user_id>` | Manually approve a teacher's access to the private bot |
| `/grant_vip <user_id> [days]` | Grant VIP status for `N` days (`0` = lifetime / permanent) |
| `/revoke_vip <user_id>` | Revoke VIP status from a user |
| `/force_match` | Trigger an immediate matchmaking cycle across all view pools |
| `/force_scan` | Trigger an immediate eye-icon view scan on all active deals |
| `/force_cleanup` | Clean up and auto-delete expired (>24h) deals |
| `/lang` | Quick language switcher (Uzbek, Russian, English) |

---

## 📤 How to Push to GitHub

To upload this clean codebase to your GitHub account:

```bash
# 1. Initialize git (if not already initialized)
git init

# 2. Add all files (secrets and databases are automatically excluded by .gitignore)
git add .

# 3. Create initial commit
git commit -m "feat: complete eduswap automated telegram cross-promotion & lead capture bot"

# 4. Link your remote GitHub repository
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git

# 5. Push to GitHub
git push -u origin main
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
