from aiogram import Router, types
from aiogram.filters import CommandStart
from app.services.userapi import register_user_in_supabase
from app.keyboards.trips import get_main_keyboard
from app.services.checkedusername import chacked_username_for_login

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user

    if not chacked_username_for_login(username=user.username):

        payload = {
            "id": user.id,
            "full_name": f"{user.first_name} {user.last_name or ''}".strip(),
            "user_name": f"@{user.username}" if user.username else None,
            "is_blocked": False
        }

        success = await register_user_in_supabase(payload)

        print(success)

        if success:
            await message.answer(f"Вітаю, {user.first_name}! Ви успішно зареєстровані 🚀")

            await message.answer(
                "Ласкаво просимо! Скористайтеся кнопкою нижче, щоб знайти поїздку:",
                reply_markup=get_main_keyboard()
        )
        else:
            await message.answer(f"{chacked_username_for_login(username=user.username)}")
            
            await message.answer(
                f"Вітаю, {user.first_name}! Сталася помилка при збереженні даних, але ви можете користуватися ботом."
            )

    else:
        await message.answer(f"З повернення, {user.first_name}!")

        await message.answer(
            "Ласкаво просимо! Скористайтеся кнопкою нижче, щоб знайти поїздку:",
            reply_markup=get_main_keyboard()
        )