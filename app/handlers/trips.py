from aiogram import Router, types, F
from app.services.tripsapi import get_all_trips
from app.keyboards.trips import get_trip_action_keyboard

router = Router()

@router.message(F.text == "🚗 Знайти поїздку")
async def show_all_trips(message: types.Message):
    trips = await get_all_trips()

    if not trips:
        await message.answer("Наразі немає доступних поїздок 😔")
        return

    await message.answer(f"Знайдено поїздок: {len(trips)} 👇")

    for trip in trips:
        # Використовуємо оператор "=" замість двокрапки ":"
        trip_id = trip.get("id")
        title = trip.get("name") or trip.get("title", "Поїздка")
        date = trip.get("start_time") or trip.get("date", "Дата не вказана")

        card_text = (
            f"📌 **{title}**\n"
            f"📍 **id:** {trip_id}\n"
            f"📅 **Дата:** {date}"
        )

        await message.answer(
            card_text,
            parse_mode="Markdown",
            reply_markup=get_trip_action_keyboard(trip_id)
        )