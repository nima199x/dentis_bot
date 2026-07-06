<p align="center">
  <img src="assets/logo.png" width="140" alt="Dentis Bot logo">
</p>

<h1 align="center">🦷 Dentis Bot</h1>

<p align="center">
  A Telegram bot for booking dental clinic appointments — built with aiogram 3.x
</p>

---

## ✨ Features

- 📋 Step-by-step booking flow: name → phone number → date → time
- 📅 Interactive inline calendar (Persian/Jalali for Farsi users, Gregorian for English users)
- ⏰ Standard clinic time slots (morning and evening), with automatic blocking of taken slots and fully-booked days
- 🌐 Bilingual: Persian and English, each user picks their own language
- ❌ Customers can cancel their own appointments (`/cancel`)
- 👨‍⚕️ Admin panel to list all appointments (`/appointments`)
- 🔒 Secrets (bot token, admin IDs) always live in `.env`, never hardcoded

## 🛠 Tech Stack

- Python 3.10+
- [aiogram 3.x](https://docs.aiogram.dev/) — Telegram bot framework
- SQLite — appointment storage
- `jdatetime` — Jalali (Persian) calendar conversion

## 📸 Screenshots

<p align="center">
  <img src="assets/screenshot-calendar.png" width="280" alt="Calendar screenshot">
  <img src="assets/screenshot-booking.png" width="280" alt="Booking confirmation screenshot">
</p>

## 🚀 Setup

```bash
git clone https://github.com/nima199x/dentis_bot.git
cd dentis_bot

python -m venv dentis_venv
# Windows:
.\dentis_venv\Scripts\Activate.ps1
# Linux/macOS:
source dentis_venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file (copy from `.env.example`) and fill in real values:

```
BOT_TOKEN=your_bot_token_here
PROXY_URL=http://127.0.0.1:10808
ADMIN_IDS=your_numeric_telegram_id
```

Run:

```bash
python bot.py
```

## 📂 Project Structure

```
dentis_bot/
├── bot.py            # Entry point, bot startup
├── config.py         # Loads settings from .env
├── database.py       # SQLite database logic
├── handlers.py       # FSM flow and bot commands
├── calendar_kb.py     # Jalali/Gregorian calendar keyboard builder
├── time_kb.py         # Time-slot keyboard builder
├── lang.py            # Persian/English text strings
└── requirements.txt
```

## 📄 License

For personal/internal use only. No formal license.
