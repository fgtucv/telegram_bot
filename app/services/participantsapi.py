import os
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()

SUPABASE_TRIPS_URL = os.getenv("SUPABASE_TRIPS_URL")
SUPABASE_PARTICIPANTS_URL = os.getenv("SUPABASE_PARTICIPANTS_URL")
if not SUPABASE_PARTICIPANTS_URL and SUPABASE_TRIPS_URL:
    SUPABASE_PARTICIPANTS_URL = SUPABASE_TRIPS_URL.rsplit("/", 1)[0] + "/trip_participants"

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def is_user_in_trip(trip_id: int | str, user_id: int) -> bool:
    """Перевіряє, чи користувач вже доданий як учасник до вказаної поїздки."""
    if not SUPABASE_PARTICIPANTS_URL or not SUPABASE_KEY:
        return False

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{SUPABASE_PARTICIPANTS_URL}?trip_id=eq.{trip_id}&participants->>user_id=eq.{user_id}&limit=1"

    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return len(data) > 0
                return False
        except Exception as e:
            logging.error(f"Помилка перевірки участі в поїздці: {e}")
            return False

async def add_participant_to_trip(trip_id: int | str, user_data: dict) -> tuple[bool, str]:
    """
    Додає учасника до таблиці trip_participants.
    Поля об'єкта:
    - id: генерується базою (uuid gen_random_uuid())
    - trip_id: ID поїздки
    - participants: JSON об'єкт з даними користувача (jsonb)
    """
    if not SUPABASE_PARTICIPANTS_URL or not SUPABASE_KEY:
        return False, "Не налаштовано підключення до бази даних (SUPABASE_PARTICIPANTS_URL/KEY)"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    payload = {
        "trip_id": trip_id,
        "participants": user_data
    }

    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(SUPABASE_PARTICIPANTS_URL, json=payload, headers=headers) as resp:
                if resp.status in (200, 201):
                    logging.info(f"Користувач {user_data.get('user_id')} успішно приєднався до поїздки #{trip_id}")
                    return True, "Успішно"
                else:
                    error_text = await resp.text()
                    logging.error(f"Помилка додавання учасника до поїздки #{trip_id} ({resp.status}): {error_text}")
                    return False, error_text
        except Exception as e:
            logging.error(f"Помилка з'єднання з Supabase при додаванні учасника: {e}")
            return False, str(e)

async def get_user_trip_ids(user_id: int) -> list:
    """Повертає список trip_id, до яких приєднався користувач."""
    if not SUPABASE_PARTICIPANTS_URL or not SUPABASE_KEY:
        return []

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{SUPABASE_PARTICIPANTS_URL}?participants->>user_id=eq.{user_id}&select=trip_id"

    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [item.get("trip_id") for item in data if item.get("trip_id") is not None]
                return []
        except Exception as e:
            logging.error(f"Помилка отримання поїздок користувача {user_id}: {e}")
            return []
