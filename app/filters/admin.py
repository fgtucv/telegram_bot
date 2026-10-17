import os
from aiogram.filters import Filter
from aiogram.types import TelegramObject
from dotenv import load_dotenv

load_dotenv()

def get_admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_ID", "")
    ids = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            ids.add(int(part))
    return ids

ADMIN_IDS = get_admin_ids()
ADMIN_ID = next(iter(ADMIN_IDS), 0)

def is_admin_user(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return user_id in ADMIN_IDS

class IsAdmin(Filter):
    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        if not user:
            return False
        return is_admin_user(user.id)