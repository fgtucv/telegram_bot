from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚗 Знайти поїздку")],
        [KeyboardButton(text="🗓 Мої поїздки")]
    ]

    if is_admin:
        buttons.append([KeyboardButton(text="➕ Створити поїздку")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

def get_trip_action_keyboard(trip_id: int, destination_url: str | None = None) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🙋‍♂️ Доєднатися", callback_data=f"join_{trip_id}")]
    ]
    if destination_url and (destination_url.startswith("http://") or destination_url.startswith("https://")):
        buttons.append([InlineKeyboardButton(text="🗺 Локація на карті", url=destination_url)])

    return InlineKeyboardMarkup(inline_keyboard=buttons)