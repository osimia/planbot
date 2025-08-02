import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://planbot-production.up.railway.app
PORT = int(os.getenv("PORT", 8888))

logging.basicConfig(level=logging.INFO)

def create_app():
    dp = Dispatcher(storage=MemoryStorage())

    # Автоматически создать схему БД при первом запуске
    from database import db
    import asyncio
    async def on_startup(bot: Bot):
        await db.init_db_schema()
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

    from handlers import start, income, expense, reminder, cancel
    dp.include_router(start.router)
    dp.include_router(income.router)
    dp.include_router(expense.router)
    dp.include_router(reminder.router)
    dp.include_router(cancel.router)
    dp.startup.register(on_startup)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=PORT)
