import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers.broadcast import router as broadcast_router

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Підключаємо роутер із фільтром
dp.include_router(broadcast_router)

async def main():
    print("Бот запущений...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())