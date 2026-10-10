import os
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_USER_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def register_user_in_supabase(user_data: dict) -> bool:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SUPABASE_URL, json=user_data, headers=headers, timeout=5) as resp:
                if resp.status in (200, 201):
                    logging.info(f"Користувач {user_data.get('username')} успішно доданий в Supabase!")
                    return True
                else:
                    error_text = await resp.text()
                    logging.error(f"Помилка Supabase ({resp.status}): {error_text}")
                    return False
        except Exception as e:
            logging.error(f"Не вдалося з'єднатися з Supabase API: {e}")
            return False