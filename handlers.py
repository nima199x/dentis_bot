import re

import jdatetime
from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from calendar_kb import build_calendar, shift_month
from time_kb import CLINIC_SLOTS, build_time_keyboard
from database import (
    add_appointment,
    get_all_appointments,
    get_booked_times,
    get_fully_booked_dates,
    get_user_appointments,
    delete_appointment,
)

router = Router()

# آی‌دی عددی ادمین
ADMIN_IDS = {50753843}

PHONE_PATTERN = re.compile(r"^09\d{9}$")

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ لغو")]],
    resize_keyboard=True,
)


class BookingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_date = State()
    waiting_for_time = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "سلام! خوش آمدید 🦷\n"
        "برای رزرو نوبت پزشکی، دستور /book رو بفرست.\n"
        "برای دیدن یا حذف نوبت‌هاتون، دستور /cancel رو بفرست."
    )


@router.message(Command("book"))
async def cmd_book(message: types.Message, state: FSMContext):
    await state.set_state(BookingStates.waiting_for_name)
    await message.answer(
        "لطفاً نام و نام خانوادگی خودتون رو وارد کنید:",
        reply_markup=cancel_kb,
    )


@router.message(F.text == "❌ لغو", StateFilter("*"))
async def cancel_booking(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("رزرو نوبت لغو شد.", reply_markup=ReplyKeyboardRemove())


@router.message(BookingStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("نام واردشده خیلی کوتاهه. لطفاً نام کامل رو وارد کنید:")
        return

    await state.update_data(name=name)
    await state.set_state(BookingStates.waiting_for_phone)
    await message.answer("شماره تماستون رو وارد کنید (مثال: 09121234567):")


@router.message(BookingStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not PHONE_PATTERN.match(phone):
        await message.answer(
            "شماره واردشده معتبر نیست. لطفاً به فرمت 09121234567 وارد کنید:"
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(BookingStates.waiting_for_date)

    today = jdatetime.date.today()
    full_dates = get_fully_booked_dates(today.year, today.month, len(CLINIC_SLOTS))
    await message.answer(
        "تاریخ موردنظرتون رو با دکمه‌های زیر انتخاب کنید 👇",
        reply_markup=build_calendar(today.year, today.month, full_dates),
    )


@router.message(BookingStates.waiting_for_date)
async def process_date_text_fallback(message: types.Message):
    await message.answer("لطفاً تاریخ رو از تقویم بالا با کلیک انتخاب کنید 📅")


@router.message(BookingStates.waiting_for_time)
async def process_time_text_fallback(message: types.Message):
    await message.answer("لطفاً ساعت رو از دکمه‌های بالا انتخاب کنید ⏰")


@router.callback_query(BookingStates.waiting_for_date, F.data == "cal:ignore")
async def calendar_ignore(callback: types.CallbackQuery):
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_date, F.data == "cal:past")
async def calendar_past(callback: types.CallbackQuery):
    await callback.answer("این تاریخ گذشته. یه روز دیگه رو انتخاب کنید.", show_alert=True)


@router.callback_query(BookingStates.waiting_for_date, F.data == "cal:full")
async def calendar_full(callback: types.CallbackQuery):
    await callback.answer("تمام ساعت‌های این روز رزرو شده. یه روز دیگه انتخاب کنید.", show_alert=True)


@router.callback_query(BookingStates.waiting_for_date, F.data.startswith("cal:nav:"))
async def calendar_navigate(callback: types.CallbackQuery):
    _, _, year, month, direction = callback.data.split(":")
    new_year, new_month = shift_month(int(year), int(month), direction)
    full_dates = get_fully_booked_dates(new_year, new_month, len(CLINIC_SLOTS))
    await callback.message.edit_reply_markup(
        reply_markup=build_calendar(new_year, new_month, full_dates)
    )
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_date, F.data.startswith("cal:day:"))
async def calendar_pick_day(callback: types.CallbackQuery, state: FSMContext):
    _, _, year, month, day = callback.data.split(":")
    date_str = f"{int(day):02d}-{int(month):02d}-{int(year)}"

    booked_times = get_booked_times(date_str)
    if len(booked_times) >= len(CLINIC_SLOTS):
        await callback.answer(
            "تمام ساعت‌های این روز رزرو شده. یه روز دیگه انتخاب کنید.",
            show_alert=True,
        )
        return

    await state.update_data(date=date_str)
    await state.set_state(BookingStates.waiting_for_time)

    await callback.message.edit_text(
        f"تاریخ انتخابی: {date_str}\nحالا ساعت موردنظرتون رو انتخاب کنید ⏰"
    )
    await callback.message.edit_reply_markup(reply_markup=build_time_keyboard(booked_times))
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_time, F.data == "time:taken")
async def time_taken(callback: types.CallbackQuery):
    await callback.answer("این ساعت قبلاً رزرو شده. یه ساعت دیگه انتخاب کنید.", show_alert=True)


@router.callback_query(BookingStates.waiting_for_time, F.data == "time:back")
async def time_back(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date_str = data.get("date", "")
    try:
        day, month, year = (int(p) for p in date_str.split("-"))
    except ValueError:
        today = jdatetime.date.today()
        year, month = today.year, today.month

    await state.set_state(BookingStates.waiting_for_date)
    full_dates = get_fully_booked_dates(year, month, len(CLINIC_SLOTS))
    await callback.message.edit_text("تاریخ موردنظرتون رو با دکمه‌های زیر انتخاب کنید 👇")
    await callback.message.edit_reply_markup(reply_markup=build_calendar(year, month, full_dates))
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_time, F.data.startswith("time:pick:"))
async def time_pick(callback: types.CallbackQuery, state: FSMContext):
    slot = callback.data.split(":", 2)[2]

    data = await state.get_data()
    date_str = data.get("date")

    # جلوگیری از رزرو دوباره‌ی همون ساعت توسط دو نفر همزمان
    booked_times = get_booked_times(date_str)
    if slot in booked_times:
        await callback.answer(
            "این ساعت همین الان توسط شخص دیگه‌ای رزرو شد. یه ساعت دیگه انتخاب کنید.",
            show_alert=True,
        )
        await callback.message.edit_reply_markup(reply_markup=build_time_keyboard(booked_times))
        return

    add_appointment(
        user_id=callback.from_user.id,
        name=data["name"],
        phone=data["phone"],
        date=date_str,
        time=slot,
    )
    await state.clear()

    await callback.message.edit_text(
        "✅ نوبت شما با موفقیت ثبت شد!\n\n"
        f"نام: {data['name']}\n"
        f"شماره تماس: {data['phone']}\n"
        f"تاریخ: {date_str}\n"
        f"ساعت: {slot}\n\n"
        "منتظر حضورتون هستیم."
    )
    await callback.message.answer(
        "برای رزرو نوبت جدید، دستور /book رو بفرست.\n"
        "برای دیدن یا حذف نوبت‌ها، دستور /cancel رو بفرست.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    rows = get_user_appointments(message.from_user.id)
    if not rows:
        await message.answer("شما هیچ نوبت فعالی ندارید.")
        return

    keyboard_rows = []
    for appt_id, date_str, time_str in rows:
        keyboard_rows.append([
            types.InlineKeyboardButton(
                text=f"❌ حذف نوبت {date_str} ساعت {time_str}",
                callback_data=f"delappt:{appt_id}",
            )
        ])

    markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    await message.answer("نوبت‌های شما:", reply_markup=markup)


@router.callback_query(F.data.startswith("delappt:"))
async def cancel_appointment(callback: types.CallbackQuery):
    appt_id = int(callback.data.split(":")[1])
    deleted = delete_appointment(appt_id, callback.from_user.id)

    if deleted:
        await callback.message.edit_text("✅ نوبت شما با موفقیت حذف شد.")
    else:
        await callback.message.edit_text("این نوبت پیدا نشد یا قبلاً حذف شده.")
    await callback.answer()


@router.message(Command("appointments"))
async def cmd_appointments(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("این دستور فقط برای ادمین در دسترسه.")
        return

    rows = get_all_appointments()
    if not rows:
        await message.answer("هیچ نوبتی ثبت نشده.")
        return

    lines = [
        f"#{row[0]} — {row[1]} | {row[2]} | {row[3]} ساعت {row[4] or '-'}"
        for row in rows
    ]
    await message.answer("📋 لیست نوبت‌ها:\n\n" + "\n".join(lines))
