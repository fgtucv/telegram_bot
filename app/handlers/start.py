import html
from aiogram import Router, types
from aiogram.filters import CommandStart
from app.keyboards.trips import get_main_keyboard
from app.filters.admin import is_admin_user

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user
    if not user:
        return

    is_admin = is_admin_user(user.id)
    keyboard = get_main_keyboard(is_admin=is_admin)
    safe_name = html.escape(user.first_name)

    await message.answer(
        f"Вітаю, {safe_name}! 👋\n\n"
        "Ласкаво просимо! Скористайтеся кнопками нижче, щоб знайти або переглянути поїздки:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )