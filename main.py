import asyncio
import os
import sys
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from app.handlers.start import router as start_router
from app.handlers.create_trip import router as create_trip_router
from app.handlers.trips import router as trips_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    logging.critical("Помилка: BOT_TOKEN не знайдено у файлі .env!")
    sys.exit(1)

bot = Bot(
    token=bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(create_trip_router)
dp.include_router(trips_router)

async def main():
    logging.info("Бот запущений і готовий до роботи...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logging.info("Сесію бота успішно закрито.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Роботу бота завершено.")