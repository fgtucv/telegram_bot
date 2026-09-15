import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# Завантажуємо токен з файлу .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен не знайдено! Перевірте файл .env")

# Налаштування логування
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обробник команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Бот успішно запущений та працює! 🚀")

async def main():
    print("Запуск бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())