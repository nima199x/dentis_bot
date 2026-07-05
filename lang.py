TEXT = {
    "fa": {
        "choose_language": "زبان مورد نظرتون رو انتخاب کنید:",
        "language_saved": "زبان به فارسی تغییر کرد. ✅",
        "welcome": (
            "سلام! خوش آمدید 🦷\n"
            "برای رزرو نوبت پزشکی، دستور /book رو بفرست.\n"
            "برای دیدن یا حذف نوبت‌هاتون، دستور /cancel رو بفرست.\n"
            "برای تغییر زبان، دستور /language رو بفرست."
        ),
        "ask_name": "لطفاً نام و نام خانوادگی خودتون رو وارد کنید:",
        "name_too_short": "نام واردشده خیلی کوتاهه. لطفاً نام کامل رو وارد کنید:",
        "ask_phone": "شماره تماستون رو وارد کنید (مثال: 09121234567):",
        "invalid_phone": "شماره واردشده معتبر نیست. لطفاً به فرمت 09121234567 وارد کنید:",
        "ask_date": "تاریخ موردنظرتون رو با دکمه‌های زیر انتخاب کنید 👇",
        "date_text_fallback": "لطفاً تاریخ رو از تقویم بالا با کلیک انتخاب کنید 📅",
        "time_text_fallback": "لطفاً ساعت رو از دکمه‌های بالا انتخاب کنید ⏰",
        "past_date_alert": "این تاریخ گذشته. یه روز دیگه رو انتخاب کنید.",
        "full_date_alert": "تمام ساعت‌های این روز رزرو شده. یه روز دیگه انتخاب کنید.",
        "selected_date_prompt": "تاریخ انتخابی: {date}\nحالا ساعت موردنظرتون رو انتخاب کنید ⏰",
        "time_taken_alert": "این ساعت قبلاً رزرو شده. یه ساعت دیگه انتخاب کنید.",
        "time_taken_race_alert": "این ساعت همین الان توسط شخص دیگه‌ای رزرو شد. یه ساعت دیگه انتخاب کنید.",
        "booking_confirmed": (
            "✅ نوبت شما با موفقیت ثبت شد!\n\n"
            "نام: {name}\nشماره تماس: {phone}\nتاریخ: {date}\nساعت: {time}\n\n"
            "منتظر حضورتون هستیم."
        ),
        "booking_confirmed_footer": (
            "برای رزرو نوبت جدید، دستور /book رو بفرست.\n"
            "برای دیدن یا حذف نوبت‌ها، دستور /cancel رو بفرست."
        ),
        "cancel_none": "شما هیچ نوبت فعالی ندارید.",
        "cancel_list_title": "نوبت‌های شما:",
        "cancel_button": "❌ حذف نوبت {date} ساعت {time}",
        "cancel_success": "✅ نوبت شما با موفقیت حذف شد.",
        "cancel_not_found": "این نوبت پیدا نشد یا قبلاً حذف شده.",
        "booking_cancelled": "رزرو نوبت لغو شد.",
        "admin_only": "این دستور فقط برای ادمین در دسترسه.",
        "admin_no_appointments": "هیچ نوبتی ثبت نشده.",
        "admin_list_title": "📋 لیست نوبت‌ها:",
        "back_to_calendar": "⬅ بازگشت به تقویم",
        "cancel_keyboard_button": "❌ لغو",
    },
    "en": {
        "choose_language": "Please choose your language:",
        "language_saved": "Language switched to English. ✅",
        "welcome": (
            "Hello! Welcome 🦷\n"
            "To book an appointment, send /book.\n"
            "To view or cancel your appointments, send /cancel.\n"
            "To change language, send /language."
        ),
        "ask_name": "Please enter your full name:",
        "name_too_short": "That name is too short. Please enter your full name:",
        "ask_phone": "Please enter your phone number (example: 09121234567):",
        "invalid_phone": "That phone number isn't valid. Please use the format 09121234567:",
        "ask_date": "Please pick a date using the buttons below 👇",
        "date_text_fallback": "Please pick a date from the calendar above by tapping it 📅",
        "time_text_fallback": "Please pick a time from the buttons above ⏰",
        "past_date_alert": "That date is in the past. Please pick another day.",
        "full_date_alert": "All time slots for that day are booked. Please pick another day.",
        "selected_date_prompt": "Selected date: {date}\nNow pick a time ⏰",
        "time_taken_alert": "That time slot is already booked. Please pick another one.",
        "time_taken_race_alert": "That time slot was just booked by someone else. Please pick another one.",
        "booking_confirmed": (
            "✅ Your appointment has been booked!\n\n"
            "Name: {name}\nPhone: {phone}\nDate: {date}\nTime: {time}\n\n"
            "We look forward to seeing you."
        ),
        "booking_confirmed_footer": (
            "To book a new appointment, send /book.\n"
            "To view or cancel appointments, send /cancel."
        ),
        "cancel_none": "You have no active appointments.",
        "cancel_list_title": "Your appointments:",
        "cancel_button": "❌ Cancel {date} at {time}",
        "cancel_success": "✅ Your appointment has been cancelled.",
        "cancel_not_found": "This appointment was not found or already cancelled.",
        "booking_cancelled": "Booking cancelled.",
        "admin_only": "This command is admin-only.",
        "admin_no_appointments": "No appointments booked yet.",
        "admin_list_title": "📋 Appointment list:",
        "back_to_calendar": "⬅ Back to calendar",
        "cancel_keyboard_button": "❌ Cancel",
    },
}

MONTHS = {
    "fa": [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
    ],
    "en": [
        "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
        "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand",
    ],
}

GREGORIAN_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

GREGORIAN_WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# fa: چیدمان راست‌به‌چپ (چپ‌ترین = جمعه ... راست‌ترین = شنبه)
# en: چیدمان چپ‌به‌راست (چپ‌ترین = شنبه ... راست‌ترین = جمعه)
WEEKDAYS = {
    "fa": ["جمعه", "پنجشنبه", "چهارشنبه", "سه‌شنبه", "دوشنبه", "یکشنبه", "شنبه"],
    "en": ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"],
}


def t(lang: str, key: str, **kwargs) -> str:
    template = TEXT.get(lang, TEXT["fa"]).get(key, key)
    return template.format(**kwargs) if kwargs else template
