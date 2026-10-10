from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.filters.admin import IsAdmin

def get_main_keyboard():

    buttons = [
        [KeyboardButton(text="🚗 Знайти поїздку")],
        [KeyboardButton(text="🗓 Мої поїздки")]
    ]

    if IsAdmin:
        buttons.append([KeyboardButton(text="➕ Створити поїздку")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    return keyboard

def get_trip_action_keyboard(trip_id: int):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🙋‍♂️ Доєднатися", callback_data=f"join_{trip_id}")]]
    )

    return keyboard