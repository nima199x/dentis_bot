from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ساعت‌های معمول ویزیت (صبح و عصر)
CLINIC_SLOTS = [
    "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30",
    "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30",
]


def build_time_keyboard(booked_times) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for slot in CLINIC_SLOTS:
        if slot in booked_times:
            row.append(InlineKeyboardButton(text=f"🚫 {slot}", callback_data="time:taken"))
        else:
            row.append(InlineKeyboardButton(text=slot, callback_data=f"time:pick:{slot}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton(text="⬅ بازگشت به تقویم", callback_data="time:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
