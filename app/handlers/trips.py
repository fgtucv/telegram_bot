import html
from datetime import datetime
from aiogram import Router, types, F
from app.services.tripsapi import get_all_trips, get_trip_by_id
from app.services.participantsapi import add_participant_to_trip, is_user_in_trip, get_user_trip_ids
from app.keyboards.trips import get_trip_action_keyboard
from app.filters.admin import is_admin_user

router = Router()

def format_date_str(raw_date: str | None) -> str:
    if not raw_date:
        return "Дата не вказана"
    try:
        clean_date = str(raw_date).replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_date)
        return dt.strftime("%d.%m.%Y о %H:%M")
    except Exception:
        return str(raw_date)

def build_trip_card_text(trip: dict) -> str:
    trip_id = trip.get("id")
    title = trip.get("name") or trip.get("title") or "Поїздка"
    raw_date = trip.get("start_time") or trip.get("date")
    date_str = format_date_str(raw_date)

    destination = trip.get("destination")
    origin = trip.get("location_started")
    price = trip.get("price_amount")
    currency = trip.get("price_currency") or "UAH"
    max_p = trip.get("max_participants")
    description = trip.get("description")

    lines = [f"📌 <b>{html.escape(str(title))}</b>"]

    if origin and destination:
        lines.append(f"🛣 <b>Маршрут:</b> {html.escape(str(origin))} ➔ {html.escape(str(destination))}")
    elif destination:
        lines.append(f"📍 <b>Напрямок:</b> {html.escape(str(destination))}")

    lines.append(f"📅 <b>Дата:</b> {html.escape(date_str)}")

    if price is not None and price != "":
        lines.append(f"💰 <b>Вартість:</b> {price} {html.escape(currency)}")

    if max_p is not None and max_p != "":
        lines.append(f"👥 <b>Місць:</b> до {max_p}")

    if description:
        lines.append(f"ℹ️ <i>{html.escape(str(description))}</i>")

    lines.append(f"🆔 <code>#{trip_id}</code>")
    return "\n".join(lines)

@router.message(F.text == "🚗 Знайти поїздку")
async def show_all_trips(message: types.Message):
    trips = await get_all_trips()

    if not trips:
        await message.answer("Наразі немає доступних поїздок 😔")
        return

    await message.answer(f"Знайдено поїздок: <b>{len(trips)}</b> 👇", parse_mode="HTML")

    for trip in trips:
        trip_id = trip.get("id")
        destination_url = trip.get("destination_url") or trip.get("location_ended_url")
        card_text = build_trip_card_text(trip)

        await message.answer(
            card_text,
            parse_mode="HTML",
            reply_markup=get_trip_action_keyboard(trip_id, destination_url=destination_url)
        )

@router.callback_query(F.data.startswith("join_"))
async def handle_join_trip(callback: types.CallbackQuery):
    user = callback.from_user
    if not user:
        await callback.answer("Помилка ідентифікації користувача.", show_alert=True)
        return

    try:
        raw_id = callback.data.split("_")[1]
        trip_id = int(raw_id) if raw_id.isdigit() else raw_id
    except IndexError:
        await callback.answer("Некоректний ID поїздки.", show_alert=True)
        return

    # Перевіряємо, чи користувач уже доєднався
    already_joined = await is_user_in_trip(trip_id=trip_id, user_id=user.id)
    if already_joined:
        await callback.answer("Ви вже зареєстровані як учасник цієї поїздки! 👍", show_alert=True)
        return

    # Формуємо об'єкт учасника (JSONB)
    participant_data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name or "",
        "username": f"@{user.username}" if user.username else None
    }

    success, error_msg = await add_participant_to_trip(trip_id=trip_id, user_data=participant_data)

    if success:
        await callback.answer("Ви успішно приєдналися до поїздки! 🎉", show_alert=True)
        if callback.message:
            await callback.message.reply(
                f"✅ Вас додано до списку учасників поїздки <code>#{html.escape(str(trip_id))}</code>!\n"
                "Очікуйте на зв'язок від організатора/водія.",
                parse_mode="HTML"
            )
    else:
        # Якщо в базі налаштовано RLS або тип поля uuid
        if "uuid" in error_msg.lower():
            await callback.answer(
                "Помилка бази даних: тип поля trip_id очікує uuid, а не числовий ID поїздки. Зверніться до адміністратора.",
                show_alert=True
            )
        elif "policy" in error_msg.lower() or "42501" in error_msg:
            await callback.answer(
                "Помилка доступу до бази (RLS Policy). Зверніться до адміністратора.",
                show_alert=True
            )
        else:
            await callback.answer("Не вдалося доєднатися до поїздки. Спробуйте пізніше.", show_alert=True)

@router.message(F.text == "🗓 Мої поїздки")
async def show_my_trips(message: types.Message):
    user = message.from_user
    if not user:
        return

    trip_ids = await get_user_trip_ids(user.id)

    if not trip_ids:
        await message.answer(
            "🗓 <b>Ваші поїздки</b>\n\n"
            "У вас наразі немає активних бронювань.\n"
            "Щоб обрати та доєднатися до поїздки, скористайтеся кнопкою <b>🚗 Знайти поїздку</b>.",
            parse_mode="HTML"
        )
        return

    await message.answer(f"🗓 Ваші заброньовані поїздки (всього: <b>{len(trip_ids)}</b>):", parse_mode="HTML")

    for t_id in trip_ids:
        try:
            t_int = int(t_id) if str(t_id).isdigit() else t_id
            trip = await get_trip_by_id(t_int)
            if trip:
                card_text = build_trip_card_text(trip)
                destination_url = trip.get("destination_url") or trip.get("location_ended_url")
                await message.answer(
                    card_text,
                    parse_mode="HTML",
                    reply_markup=get_trip_action_keyboard(t_id, destination_url=destination_url)
                )
            else:
                await message.answer(f"📍 Поїздка <code>#{html.escape(str(t_id))}</code>", parse_mode="HTML")
        except Exception:
            continue