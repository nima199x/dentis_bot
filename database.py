import sqlite3

DB_NAME = 'appointments.db'


def create_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT,
                        phone TEXT,
                        date TEXT,
                        time TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_prefs (
                        user_id INTEGER PRIMARY KEY,
                        language TEXT)''')
    conn.commit()

    # مهاجرت برای دیتابیس‌های قدیمی که ستون time رو ندارن
    cursor.execute("PRAGMA table_info(appointments)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if "time" not in existing_cols:
        cursor.execute("ALTER TABLE appointments ADD COLUMN time TEXT")
        conn.commit()

    conn.close()


def get_user_language(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM user_prefs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def set_user_language(user_id, language):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_prefs (user_id, language) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET language = excluded.language",
        (user_id, language)
    )
    conn.commit()
    conn.close()


def add_appointment(user_id, name, phone, date, time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (user_id, name, phone, date, time) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, phone, date, time)
    )
    conn.commit()
    conn.close()


def _date_sort_key(date_str):
    try:
        day, month, year = date_str.split("-")
        return (int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def get_all_appointments():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, date, time FROM appointments")
    rows = cursor.fetchall()
    conn.close()
    rows.sort(key=lambda r: (_date_sort_key(r[3]), r[4] or ""))
    return rows


def get_booked_times(date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT time FROM appointments WHERE date = ?", (date_str,))
    rows = cursor.fetchall()
    conn.close()
    return {r[0] for r in rows if r[0]}


def get_fully_booked_dates(total_slots):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, COUNT(*) FROM appointments GROUP BY date")
    rows = cursor.fetchall()
    conn.close()

    return {date_str for date_str, count in rows if count >= total_slots}


def get_user_appointments(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, date, time FROM appointments WHERE user_id = ?",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    rows.sort(key=lambda r: (_date_sort_key(r[1]), r[2] or ""))
    return rows


def delete_appointment(appointment_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM appointments WHERE id = ? AND user_id = ?",
        (appointment_id, user_id)
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
