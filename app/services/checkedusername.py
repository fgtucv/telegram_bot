import os
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_USER_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def chacked_username_for_login(username: str) -> bool:

    if not username:
        return False

    formatted_username = f"@{username.lstrip('@')}"
    url = f"{SUPABASE_URL}?user_name=eq.{formatted_username}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    return len(data) > 0
                else:
                    logging.error(f"Помилка при перевірці username ({resp.status})")

                    return False
        except Exception as e:
            logging.error(f"Помилка з'єднання: {e}")
            return False