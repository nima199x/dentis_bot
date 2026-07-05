import re
import datetime

import jdatetime
from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from calendar_kb import build_calendar, shift_month
from time_kb import CLINIC_SLOTS, build_time_keyboard
from lang import t
from config import ADMIN_IDS
from database import (
    add_appointment,
    get_all_appointments,
    get_booked_times,
    get_fully_booked_dates,
    get_user_appointments,
    delete_appointment,
    get_user_language,
    set_user_language,
)

router = Router()

PHONE_PATTERN = re.compile(r"^09\d{9}$")

DEFAULT_LANG = "fa"


def user_lang(user_id: int) -> str:
    return get_user_language(user_id) or DEFAULT_LANG


def format_date_for_display(date_str: str, lang: str) -> str:
    """date_str همیشه به فرمت شمسی DD-MM-YYYY ذخیره می‌شه؛
    برای زبان انگلیسی به میلادی نمایش داده می‌شه."""
    if lang != "en":
        return date_str
    try:
        day, month, year = (int(p) for p in date_str.split("-"))
        g_date = jdatetime.date(year, month, day).togregorian()
        return g_date.strftime("%B %d, %Y")
    except ValueError:
        return date_str


def cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "cancel_keyboard_button"))]],
        resize_keyboard=True,
    )


def language_kb() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang:set:fa"),
            types.InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:set:en"),
        ]
    ])


class BookingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_date = State()
    waiting_for_time = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    lang = get_user_language(message.from_user.id)
    if lang is None:
        await message.answer(
            t("fa", "choose_language") + "\n" + t("en", "choose_language"),
            reply_markup=language_kb(),
        )
        return
    await message.answer(t(lang, "welcome"))


@router.message(Command("language"))
async def cmd_language(message: types.Message):
    await message.answer(
        t("fa", "choose_language") + "\n" + t("en", "choose_language"),
        reply_markup=language_kb(),
    )


@router.callback_query(F.data.startswith("lang:set:"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split(":")[2]
    set_user_language(callback.from_user.id, lang)
    await callback.message.edit_text(t(lang, "language_saved"))
    await callback.message.answer(t(lang, "welcome"))
    await callback.answer()


@router.message(Command("book"))
async def cmd_book(message: types.Message, state: FSMContext):
    lang = user_lang(message.from_user.id)
    await state.update_data(lang=lang)
    await state.set_state(BookingStates.waiting_for_name)
    await message.answer(t(lang, "ask_name"), reply_markup=cancel_kb(lang))


@router.message(
    F.text.in_({t("fa", "cancel_keyboard_button"), t("en", "cancel_keyboard_button")}),
    StateFilter("*"),
)
async def cancel_booking(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    data = await state.get_data()
    lang = data.get("lang") or user_lang(message.from_user.id)
    await state.clear()
    await message.answer(t(lang, "booking_cancelled"), reply_markup=ReplyKeyboardRemove())


@router.message(BookingStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(message.from_user.id)

    name = message.text.strip()
    if len(name) < 3:
        await message.answer(t(lang, "name_too_short"))
        return

    await state.update_data(name=name)
    await state.set_state(BookingStates.waiting_for_phone)
    await message.answer(t(lang, "ask_phone"))


@router.message(BookingStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(message.from_user.id)

    phone = message.text.strip()
    if not PHONE_PATTERN.match(phone):
        await message.answer(t(lang, "invalid_phone"))
        return

    await state.update_data(phone=phone)
    await state.set_state(BookingStates.waiting_for_date)

    if lang == "en":
        today = datetime.date.today()
    else:
        today = jdatetime.date.today()

    full_dates = get_fully_booked_dates(len(CLINIC_SLOTS))
    await message.answer(
        t(lang, "ask_date"),
        reply_markup=build_calendar(today.year, today.month, full_dates, lang=lang),
    )


@router.message(BookingStates.waiting_for_date)
async def process_date_text_fallback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(message.from_user.id)
    await message.answer(t(lang, "date_text_fallback"))


@router.message(BookingStates.waiting_for_time)
async def process_time_text_fallback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(message.from_user.id)
    await message.answer(t(lang, "time_text_fallback"))


@router.callback_query(BookingStates.waiting_for_date, F.data == "cal:ignore")
async def calendar_ignore(callback: types.CallbackQuery):
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_date, F.data == "cal:past")
async def calendar_past(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(callback.from_user.id)
    await callback.answer(t(lang, "past_date_alert"), show_alert=True)


@router.callback_query(BookingStates.waiting_for_date, F.data == "cal:full")
async def calendar_full(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(callback.from_user.id)
    await callback.answer(t(lang, "full_date_alert"), show_alert=True)


@router.callback_query(BookingStates.waiting_for_date, F.data.startswith("cal:nav:"))
async def calendar_navigate(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(callback.from_user.id)

    _, _, year, month, direction = callback.data.split(":")
    new_year, new_month = shift_month(int(year), int(month), direction)
    full_dates = get_fully_booked_dates(len(CLINIC_SLOTS))
    await callback.message.edit_reply_markup(
        reply_markup=build_calendar(new_year, new_month, full_dates, lang=lang)
    )
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_date, F.data.startswith("cal:day:"))
async def calendar_pick_day(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(callback.from_user.id)

    _, _, year, month, day = callback.data.split(":")
    date_str = f"{int(day):02d}-{int(month):02d}-{int(year)}"

    booked_times = get_booked_times(date_str)
    if len(booked_times) >= len(CLINIC_SLOTS):
        await callback.answer(t(lang, "full_date_alert"), show_alert=True)
        return

    await state.update_data(date=date_str)
    await state.set_state(BookingStates.waiting_for_time)

    await callback.message.edit_text(t(lang, "selected_date_prompt", date=format_date_for_display(date_str, lang)))
    await callback.message.edit_reply_markup(reply_markup=build_time_keyboard(booked_times, lang=lang))
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_time, F.data == "time:taken")
async def time_taken(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(callback.from_user.id)
    await callback.answer(t(lang, "time_taken_alert"), show_alert=True)


@router.callback_query(BookingStates.waiting_for_time, F.data == "time:back")
async def time_back(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(callback.from_user.id)
    date_str = data.get("date", "")

    try:
        day, month, year = (int(p) for p in date_str.split("-"))
        if lang == "en":
            g_date = jdatetime.date(year, month, day).togregorian()
            year, month = g_date.year, g_date.month
    except ValueError:
        today = datetime.date.today() if lang == "en" else jdatetime.date.today()
        year, month = today.year, today.month

    await state.set_state(BookingStates.waiting_for_date)
    full_dates = get_fully_booked_dates(len(CLINIC_SLOTS))
    await callback.message.edit_text(t(lang, "ask_date"))
    await callback.message.edit_reply_markup(
        reply_markup=build_calendar(year, month, full_dates, lang=lang)
    )
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_time, F.data.startswith("time:pick:"))
async def time_pick(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or user_lang(callback.from_user.id)

    slot = callback.data.split(":", 2)[2]
    date_str = data.get("date")

    # جلوگیری از رزرو دوباره‌ی همون ساعت توسط دو نفر همزمان
    booked_times = get_booked_times(date_str)
    if slot in booked_times:
        await callback.answer(t(lang, "time_taken_race_alert"), show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=build_time_keyboard(booked_times, lang=lang))
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
        t(lang, "booking_confirmed", name=data["name"], phone=data["phone"],
          date=format_date_for_display(date_str, lang), time=slot)
    )
    await callback.message.answer(
        t(lang, "booking_confirmed_footer"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    lang = user_lang(message.from_user.id)
    rows = get_user_appointments(message.from_user.id)
    if not rows:
        await message.answer(t(lang, "cancel_none"))
        return

    keyboard_rows = []
    for appt_id, date_str, time_str in rows:
        keyboard_rows.append([
            types.InlineKeyboardButton(
                text=t(lang, "cancel_button", date=format_date_for_display(date_str, lang), time=time_str),
                callback_data=f"delappt:{appt_id}",
            )
        ])

    markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    await message.answer(t(lang, "cancel_list_title"), reply_markup=markup)


@router.callback_query(F.data.startswith("delappt:"))
async def cancel_appointment(callback: types.CallbackQuery):
    lang = user_lang(callback.from_user.id)
    appt_id = int(callback.data.split(":")[1])
    deleted = delete_appointment(appt_id, callback.from_user.id)

    if deleted:
        await callback.message.edit_text(t(lang, "cancel_success"))
    else:
        await callback.message.edit_text(t(lang, "cancel_not_found"))
    await callback.answer()


@router.message(Command("appointments"))
async def cmd_appointments(message: types.Message):
    lang = user_lang(message.from_user.id)
    if message.from_user.id not in ADMIN_IDS:
        await message.answer(t(lang, "admin_only"))
        return

    rows = get_all_appointments()
    if not rows:
        await message.answer(t(lang, "admin_no_appointments"))
        return

    lines = [
        f"#{row[0]} — {row[1]} | {row[2]} | {row[3]} ساعت {row[4] or '-'}"
        for row in rows
    ]
    await message.answer(t(lang, "admin_list_title") + "\n\n" + "\n".join(lines))
