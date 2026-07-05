import datetime
import calendar as gcal

import jdatetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lang import MONTHS, WEEKDAYS, GREGORIAN_MONTHS, GREGORIAN_WEEKDAYS


def _days_in_month_jalali(year: int, month: int) -> int:
    for day in (31, 30, 29):
        try:
            jdatetime.date(year, month, day)
            return day
        except ValueError:
            continue
    return 29


def _strike(text: str) -> str:
    # خط‌خوردگی بصری برای روزهای غیرفعال (گذشته)
    return "".join(ch + "\u0336" for ch in text)


def _build_jalali_rows(year: int, month: int, full_dates: set) -> list:
    rows = [
        [
            InlineKeyboardButton(text="«", callback_data=f"cal:nav:{year}:{month}:prev"),
            InlineKeyboardButton(text=f"{MONTHS['fa'][month - 1]} {year}", callback_data="cal:ignore"),
            InlineKeyboardButton(text="»", callback_data=f"cal:nav:{year}:{month}:next"),
        ],
        [InlineKeyboardButton(text=w, callback_data="cal:ignore") for w in WEEKDAYS["fa"]],
    ]

    today = jdatetime.date.today()
    days_count = _days_in_month_jalali(year, month)
    first_weekday = jdatetime.date(year, month, 1).weekday()  # 0=شنبه ... 6=جمعه

    # راست‌به‌چپ: ستون 6=شنبه ... ستون 0=جمعه
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
                row_buttons.append(InlineKeyboardButton(text=_strike(str(day)), callback_data="cal:past"))
            elif date_str in full_dates:
                row_buttons.append(InlineKeyboardButton(text=f"❌{day}", callback_data="cal:full"))
            else:
                row_buttons.append(InlineKeyboardButton(
                    text=label,
                    callback_data=f"cal:day:{year}:{month}:{day}",
                ))
        rows.append(row_buttons)

    return rows


def _build_gregorian_rows(year: int, month: int, full_dates: set) -> list:
    rows = [
        [
            InlineKeyboardButton(text="«", callback_data=f"cal:nav:{year}:{month}:prev"),
            InlineKeyboardButton(text=f"{GREGORIAN_MONTHS[month - 1]} {year}", callback_data="cal:ignore"),
            InlineKeyboardButton(text="»", callback_data=f"cal:nav:{year}:{month}:next"),
        ],
        [InlineKeyboardButton(text=w, callback_data="cal:ignore") for w in GREGORIAN_WEEKDAYS],
    ]

    today = datetime.date.today()
    # هفته از دوشنبه شروع می‌شه (استاندارد میلادی)
    month_grid = gcal.Calendar(firstweekday=0).monthdayscalendar(year, month)

    for week in month_grid:
        row_buttons = []
        for day in week:
            if day == 0:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="cal:ignore"))
                continue

            d = datetime.date(year, month, day)
            # تاریخ همیشه به شمسی تبدیل و ذخیره می‌شه، چون کلینیک با تاریخ شمسی کار می‌کنه
            jd = jdatetime.date.fromgregorian(date=d)
            jalali_str = f"{jd.day:02d}-{jd.month:02d}-{jd.year}"
            label = f"·{day}·" if d == today else str(day)

            if d < today:
                row_buttons.append(InlineKeyboardButton(text=_strike(str(day)), callback_data="cal:past"))
            elif jalali_str in full_dates:
                row_buttons.append(InlineKeyboardButton(text=f"❌{day}", callback_data="cal:full"))
            else:
                row_buttons.append(InlineKeyboardButton(
                    text=label,
                    callback_data=f"cal:day:{jd.year}:{jd.month}:{jd.day}",
                ))
        rows.append(row_buttons)

    return rows


def build_calendar(year: int, month: int, full_dates=None, lang: str = "fa") -> InlineKeyboardMarkup:
    full_dates = full_dates or set()
    if lang == "en":
        rows = _build_gregorian_rows(year, month, full_dates)
    else:
        rows = _build_jalali_rows(year, month, full_dates)
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
