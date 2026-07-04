import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
PROXY_URL = os.getenv("PROXY_URL")  # مثال: http://127.0.0.1:10808

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN پیدا نشد. یه فایل .env کنار همین فایل بساز و این خط رو توش بذار:\n"
        "BOT_TOKEN=your_token_here"
    )
