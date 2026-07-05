import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import TOKEN, PROXY_URL
from database import create_db
from handlers import router

logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="شروع / راهنما"),
        BotCommand(command="book", description="رزرو نوبت جدید"),
        BotCommand(command="cancel", description="مشاهده و حذف نوبت‌های من"),
        BotCommand(command="language", description="تغییر زبان / Change language"),
        BotCommand(command="appointments", description="لیست نوبت‌ها (ادمین)"),
    ]
    await bot.set_my_commands(commands)


async def main():
    create_db()

    session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
