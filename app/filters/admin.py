import os
from aiogram.filters import Filter
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID"))

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN_ID