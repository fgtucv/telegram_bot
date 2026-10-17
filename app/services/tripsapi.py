import os
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()

SUPABASE_TRIPS_URL = os.getenv("SUPABASE_TRIPS_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def get_all_trips() -> list:
    if not SUPABASE_TRIPS_URL or not SUPABASE_KEY:
        logging.error("SUPABASE_TRIPS_URL або SUPABASE_KEY не налаштовано в .env")
        return []

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session: 
        try:
            url = f"{SUPABASE_TRIPS_URL}?order=created_at.desc"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    trips = await resp.json()
                    return trips
                else:
                    error_text = await resp.text()
                    logging.error(f"Помилка отримання поїздок ({resp.status}): {error_text}")
                    return []
        except Exception as e:
            logging.error(f"Не вдалося з'єднатися з Supabase: {e}")
            return []

async def get_trip_by_id(trip_id: int) -> dict | None:
    if not SUPABASE_TRIPS_URL or not SUPABASE_KEY:
        return None

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            url = f"{SUPABASE_TRIPS_URL}?id=eq.{trip_id}&limit=1"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data[0] if data else None
                return None
        except Exception as e:
            logging.error(f"Помилка отримання поїздки #{trip_id}: {e}")
            return None

async def create_trip(trip_data: dict) -> tuple[bool, str]:
    """Створює нову поїздку в Supabase. Повертає (success, message)."""
    if not SUPABASE_TRIPS_URL or not SUPABASE_KEY:
        return False, "Не налаштовано підключення до бази даних"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(SUPABASE_TRIPS_URL, json=trip_data, headers=headers) as resp:
                if resp.status in (200, 201):
                    data = await resp.json()
                    trip_id = data[0].get("id") if data else "?"
                    logging.info(f"Поїздку #{trip_id} успішно створено!")
                    return True, str(trip_id)
                else:
                    error_text = await resp.text()
                    logging.error(f"Помилка створення поїздки ({resp.status}): {error_text}")
                    return False, error_text
        except Exception as e:
            logging.error(f"Не вдалося з'єднатися з Supabase: {e}")
            return False, str(e)