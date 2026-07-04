import jdatetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ترتیب راست‌به‌چپ: شنبه سمت راست، جمعه سمت چپ (مطابق تقویم‌های فارسی)
WEEKDAYS_FA = ["جمعه", "پنجشنبه", "چهارشنبه", "سه‌شنبه", "دوشنبه", "یکشنبه", "شنبه"]

MONTH_NAMES_FA = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]


def _days_in_month(year: int, month: int) -> int:
    for day in (31, 30, 29):
        try:
            jdatetime.date(year, month, day)
            return day
        except ValueError:
            continue
    return 29


def build_calendar(year: int, month: int, full_dates=None) -> InlineKeyboardMarkup:
    full_dates = full_dates or set()
    rows = []

    rows.append([
        InlineKeyboardButton(text="«", callback_data=f"cal:nav:{year}:{month}:prev"),
        InlineKeyboardButton(text=f"{MONTH_NAMES_FA[month - 1]} {year}", callback_data="cal:ignore"),
        InlineKeyboardButton(text="»", callback_data=f"cal:nav:{year}:{month}:next"),
    ])

    rows.append([InlineKeyboardButton(text=w, callback_data="cal:ignore") for w in WEEKDAYS_FA])

    today = jdatetime.date.today()
    days_count = _days_in_month(year, month)
    first_weekday = jdatetime.date(year, month, 1).weekday()  # 0=شنبه ... 6=جمعه

    # چیدمان راست‌به‌چپ: ستون 6 = شنبه ... ستون 0 = جمعه
    # با افزایش روز، حرکت از راست به چپ در هر هفته انجام می‌شه
    weeks = [[None] * 7]
    row, col = 0, 6 - first_weekday
    for day in range(1, days_count + 1):
        weeks[row][col] = day
        col -= 1
        if col < 0:
            col = 6
            row += 1
            weeks.append([None] * 7)

    if all(cell is None for cell in weeks[-1]):
        weeks.pop()

    for week in weeks:
        row_buttons = []
        for day in week:
            if day is None:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="cal:ignore"))
                continue

            d = jdatetime.date(year, month, day)
            date_str = f"{day:02d}-{month:02d}-{year}"
            label = f"·{day}·" if d == today else str(day)

            if d < today:
                row_buttons.append(InlineKeyboardButton(text=label, callback_data="cal:past"))
            elif date_str in full_dates:
                row_buttons.append(InlineKeyboardButton(text=f"❌{day}", callback_data="cal:full"))
            else:
                row_buttons.append(InlineKeyboardButton(
                    text=label,
                    callback_data=f"cal:day:{year}:{month}:{day}",
                ))
        rows.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def shift_month(year: int, month: int, direction: str) -> tuple[int, int]:
    if direction == "next":
        month += 1
        if month > 12:
            month = 1
            year += 1
    else:
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    return year, month
