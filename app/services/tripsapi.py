import os
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()

SUPABASE_TRIPS_URL = os.getenv("SUPABASE_TRIPS_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def get_all_trips() -> list:

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session: 
        try:
            async with session.get(SUPABASE_TRIPS_URL, headers=headers, timeout=5) as resp:
                if resp.status == 200:
                    trips = await resp.json()
                    return trips
                else:
                    logging.error(f"Помилка отримання поїздок ({resp.status})")
                    return []
        except Exception as e:
            logging.error(f"Не вдалося з'єднатися з Supabase: {e}")
            return []