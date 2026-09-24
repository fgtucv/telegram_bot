import os
from aiogram import Router, Bot, types
from aiogram.filters import Command
from dotenv import load_dotenv
from app.filters.admin import IsAdmin

load_dotenv()

GROUP_ID = os.getenv("GROUP_ID")

router = Router()

@router.message(Command("broadcast"), IsAdmin())
async def cmd_broadcast(message: types.Message, bot: Bot):
    command_args = message.text.split(maxsplit=1)

    if len(command_args) < 2:
        await message.answer(
            "⚠️ Будь ласка, вкажіть текст після команди.\n"
            "Приклад: `/broadcast Привіт усім!`", 
            parse_mode="Markdown"
        )
        return
    
    broadcast_text = command_args[1]

    try: 
        chat_destination = int(GROUP_ID)

        await bot.send_message(chat_id=chat_destination, text=broadcast_text)
        await message.answer("✅ Повідомлення успішно відправлено у групу!")

    except Exception as e:
        await message.answer(f"❌ Помилка при відправці: {e}")