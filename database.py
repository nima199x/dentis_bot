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
    conn.commit()

    # مهاجرت برای دیتابیس‌های قدیمی که ستون time رو ندارن
    cursor.execute("PRAGMA table_info(appointments)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if "time" not in existing_cols:
        cursor.execute("ALTER TABLE appointments ADD COLUMN time TEXT")
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


def get_fully_booked_dates(year, month, total_slots):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, COUNT(*) FROM appointments GROUP BY date")
    rows = cursor.fetchall()
    conn.close()

    full_dates = set()
    for date_str, count in rows:
        try:
            day, mo, yr = date_str.split("-")
        except (ValueError, AttributeError):
            continue
        if int(yr) == year and int(mo) == month and count >= total_slots:
            full_dates.add(date_str)
    return full_dates


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
