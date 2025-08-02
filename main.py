import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def main():
    from aiogram.client.default import DefaultBotProperties
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    # Автоматически создать схему БД при первом запуске
    from database import db
    await db.init_db_schema()

    from handlers import start, income, expense, reminder, cancel
    dp.include_router(start.router)
    dp.include_router(income.router)
    dp.include_router(expense.router)
    dp.include_router(reminder.router)
    dp.include_router(cancel.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
