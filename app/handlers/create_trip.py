import html
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.services.tripsapi import create_trip
from app.filters.admin import IsAdmin, is_admin_user
from app.keyboards.trips import get_main_keyboard

router = Router()

# ──────────────────────────────────────────────
# FSM стани для покрокового створення поїздки
# ──────────────────────────────────────────────

class CreateTripStates(StatesGroup):
    name = State()
    description = State()
    location_started = State()
    destination = State()
    start_time = State()
    end_time = State()
    price_amount = State()
    price_currency = State()
    max_participants = State()
    location_started_url = State()
    destination_url = State()
    confirm = State()

# ──────────────────────────────────────────────
# Допоміжні клавіатури
# ──────────────────────────────────────────────

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Скасувати")]],
        resize_keyboard=True
    )

def get_skip_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Пропустити")],
            [KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Створити", callback_data="create_trip_confirm"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="create_trip_cancel")
        ]
    ])

def get_currency_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="EUR"), KeyboardButton(text="UAH"), KeyboardButton(text="USD")],
            [KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )

def format_preview_date(raw: str | None) -> str:
    if not raw:
        return "—"
    try:
        dt = datetime.fromisoformat(raw)
        return dt.strftime("%d.%m.%Y о %H:%M")
    except Exception:
        return str(raw)

def build_trip_preview(data: dict) -> str:
    lines = [
        "📋 <b>Попередній перегляд поїздки:</b>",
        "",
        f"📌 <b>Назва:</b> {html.escape(data.get('name', '—'))}",
    ]
    if data.get("description"):
        lines.append(f"📝 <b>Опис:</b> {html.escape(data['description'])}")
    if data.get("location_started"):
        lines.append(f"🏁 <b>Звідки:</b> {html.escape(data['location_started'])}")
    if data.get("destination"):
        lines.append(f"📍 <b>Куди:</b> {html.escape(data['destination'])}")
    if data.get("start_time"):
        lines.append(f"📅 <b>Початок:</b> {format_preview_date(data['start_time'])}")
    if data.get("end_time"):
        lines.append(f"🏁 <b>Кінець:</b> {format_preview_date(data['end_time'])}")
    if data.get("price_amount") is not None:
        currency = data.get("price_currency", "EUR")
        lines.append(f"💰 <b>Вартість:</b> {data['price_amount']} {html.escape(currency)}")
    if data.get("max_participants"):
        lines.append(f"👥 <b>Макс. учасників:</b> {data['max_participants']}")
    if data.get("location_started_url"):
        lines.append(f"🔗 <b>Посилання (звідки):</b> {html.escape(data['location_started_url'])}")
    if data.get("destination_url"):
        lines.append(f"🔗 <b>Посилання (куди):</b> {html.escape(data['destination_url'])}")
    return "\n".join(lines)

# ──────────────────────────────────────────────
# Скасування (працює на будь-якому кроці)
# ──────────────────────────────────────────────

@router.message(F.text == "❌ Скасувати", CreateTripStates)
async def cancel_creation(message: types.Message, state: FSMContext):
    await state.clear()
    is_admin = is_admin_user(message.from_user.id) if message.from_user else False
    await message.answer(
        "🚫 Створення поїздки скасовано.",
        reply_markup=get_main_keyboard(is_admin=is_admin)
    )

# ──────────────────────────────────────────────
# Крок 1: Натискання кнопки «➕ Створити поїздку»
# ──────────────────────────────────────────────

@router.message(F.text == "➕ Створити поїздку")
async def create_trip_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else None
    if not is_admin_user(user_id):
        await message.answer("⛔ Ця функція доступна лише адміністраторам.")
        return

    await state.clear()
    await state.set_state(CreateTripStates.name)
    await message.answer(
        "➕ <b>Створення нової поїздки</b>\n\n"
        "Крок 1/10 — Введіть <b>назву</b> поїздки:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 2: Назва → Опис
# ──────────────────────────────────────────────

@router.message(CreateTripStates.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip() if message.text else ""
    if not name or len(name) < 2:
        await message.answer("⚠️ Назва має містити щонайменше 2 символи. Спробуйте ще раз:")
        return

    await state.update_data(name=name)
    await state.set_state(CreateTripStates.description)
    await message.answer(
        f"✅ Назва: <b>{html.escape(name)}</b>\n\n"
        "Крок 2/10 — Введіть <b>опис</b> поїздки (або натисніть «⏭ Пропустити»):",
        parse_mode="HTML",
        reply_markup=get_skip_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 3: Опис → Звідки
# ──────────────────────────────────────────────

@router.message(CreateTripStates.description)
async def process_description(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text == "⏭ Пропустити":
        text = ""
    if text:
        await state.update_data(description=text)
    await state.set_state(CreateTripStates.location_started)
    await message.answer(
        "Крок 3/10 — Введіть <b>місце відправлення</b> (звідки):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 4: Звідки → Куди
# ──────────────────────────────────────────────

@router.message(CreateTripStates.location_started)
async def process_location_started(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if not text:
        await message.answer("⚠️ Вкажіть місце відправлення:")
        return

    await state.update_data(location_started=text)
    await state.set_state(CreateTripStates.destination)
    await message.answer(
        "Крок 4/10 — Введіть <b>пункт призначення</b> (куди):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 5: Куди → Дата початку
# ──────────────────────────────────────────────

@router.message(CreateTripStates.destination)
async def process_destination(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if not text:
        await message.answer("⚠️ Вкажіть пункт призначення:")
        return

    await state.update_data(destination=text)
    await state.set_state(CreateTripStates.start_time)
    await message.answer(
        "Крок 5/10 — Введіть <b>дату та час початку</b>\n"
        "Формат: <code>ДД.ММ.РРРР ГГ:ХХ</code>\n"
        "Приклад: <code>25.12.2026 10:00</code>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 6: Дата початку → Дата кінця
# ──────────────────────────────────────────────

@router.message(CreateTripStates.start_time)
async def process_start_time(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    try:
        dt = datetime.strptime(text, "%d.%m.%Y %H:%M")
        iso_str = dt.isoformat()
    except ValueError:
        await message.answer(
            "⚠️ Невірний формат. Введіть дату у форматі:\n"
            "<code>ДД.ММ.РРРР ГГ:ХХ</code>\n"
            "Приклад: <code>25.12.2026 10:00</code>",
            parse_mode="HTML"
        )
        return

    await state.update_data(start_time=iso_str)
    await state.set_state(CreateTripStates.end_time)
    await message.answer(
        "Крок 6/10 — Введіть <b>дату та час завершення</b>\n"
        "Формат: <code>ДД.ММ.РРРР ГГ:ХХ</code>\n\n"
        "Або натисніть «⏭ Пропустити».",
        parse_mode="HTML",
        reply_markup=get_skip_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 7: Дата кінця → Вартість
# ──────────────────────────────────────────────

@router.message(CreateTripStates.end_time)
async def process_end_time(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text != "⏭ Пропустити":
        try:
            dt = datetime.strptime(text, "%d.%m.%Y %H:%M")
            iso_str = dt.isoformat()
            await state.update_data(end_time=iso_str)
        except ValueError:
            await message.answer(
                "⚠️ Невірний формат. Введіть дату у форматі:\n"
                "<code>ДД.ММ.РРРР ГГ:ХХ</code>",
                parse_mode="HTML"
            )
            return

    await state.set_state(CreateTripStates.price_amount)
    await message.answer(
        "Крок 7/10 — Введіть <b>вартість</b> поїздки (число):\n"
        "Приклад: <code>50</code>\n\n"
        "Або натисніть «⏭ Пропустити», якщо безкоштовно.",
        parse_mode="HTML",
        reply_markup=get_skip_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 8: Вартість → Валюта
# ──────────────────────────────────────────────

@router.message(CreateTripStates.price_amount)
async def process_price_amount(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text == "⏭ Пропустити":
        await state.set_state(CreateTripStates.max_participants)
        await message.answer(
            "Крок 9/10 — Введіть <b>макс. кількість учасників</b> (число):\n"
            "Приклад: <code>7</code>\n\n"
            "Або натисніть «⏭ Пропустити».",
            parse_mode="HTML",
            reply_markup=get_skip_cancel_keyboard()
        )
        return

    try:
        price = float(text.replace(",", "."))
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Введіть число (наприклад: <code>50</code> або <code>29.99</code>):", parse_mode="HTML")
        return

    await state.update_data(price_amount=price)
    await state.set_state(CreateTripStates.price_currency)
    await message.answer(
        "Крок 8/10 — Оберіть <b>валюту</b>:",
        parse_mode="HTML",
        reply_markup=get_currency_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 8b: Валюта → Макс. учасників
# ──────────────────────────────────────────────

@router.message(CreateTripStates.price_currency)
async def process_price_currency(message: types.Message, state: FSMContext):
    text = message.text.strip().upper() if message.text else ""
    if text not in ("EUR", "UAH", "USD", "GBP", "PLN", "CZK"):
        await message.answer("⚠️ Оберіть валюту з кнопок або введіть код (EUR, UAH, USD):")
        return

    await state.update_data(price_currency=text)
    await state.set_state(CreateTripStates.max_participants)
    await message.answer(
        "Крок 9/10 — Введіть <b>макс. кількість учасників</b> (число):\n"
        "Приклад: <code>7</code>\n\n"
        "Або натисніть «⏭ Пропустити».",
        parse_mode="HTML",
        reply_markup=get_skip_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 9: Макс. учасників → Посилання
# ──────────────────────────────────────────────

@router.message(CreateTripStates.max_participants)
async def process_max_participants(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text != "⏭ Пропустити":
        try:
            max_p = int(text)
            if max_p < 1:
                raise ValueError
            await state.update_data(max_participants=max_p)
        except ValueError:
            await message.answer("⚠️ Введіть ціле число більше 0:")
            return

    await state.set_state(CreateTripStates.destination_url)
    await message.answer(
        "Крок 10/10 — Надішліть <b>посилання на Google Maps</b> (пункт призначення):\n\n"
        "Або натисніть «⏭ Пропустити».",
        parse_mode="HTML",
        reply_markup=get_skip_cancel_keyboard()
    )

# ──────────────────────────────────────────────
# Крок 10: Посилання → Підтвердження
# ──────────────────────────────────────────────

@router.message(CreateTripStates.destination_url)
async def process_destination_url(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text != "⏭ Пропустити":
        if not (text.startswith("http://") or text.startswith("https://")):
            await message.answer("⚠️ Посилання має починатись з http:// або https://")
            return
        await state.update_data(destination_url=text)

    # Показуємо попередній перегляд
    data = await state.get_data()
    preview = build_trip_preview(data)
    await state.set_state(CreateTripStates.confirm)
    await message.answer(
        f"{preview}\n\n"
        "Натисніть <b>✅ Створити</b> для збереження або <b>❌ Скасувати</b>:",
        parse_mode="HTML",
        reply_markup=get_confirm_keyboard()
    )

# ──────────────────────────────────────────────
# Підтвердження або скасування (inline кнопки)
# ──────────────────────────────────────────────

@router.callback_query(F.data == "create_trip_confirm", CreateTripStates.confirm)
async def confirm_trip_creation(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id if callback.from_user else None
    if not is_admin_user(user_id):
        await callback.answer("⛔ Тільки адміністратор може створювати поїздки.", show_alert=True)
        await state.clear()
        return

    data = await state.get_data()

    # Формуємо об'єкт для Supabase (тільки заповнені поля)
    trip_payload = {}
    field_map = {
        "name": "name",
        "description": "description",
        "location_started": "location_started",
        "destination": "destination",
        "start_time": "start_time",
        "end_time": "end_time",
        "price_amount": "price_amount",
        "price_currency": "price_currency",
        "max_participants": "max_participants",
        "destination_url": "destination_url",
    }
    for fsm_key, db_key in field_map.items():
        value = data.get(fsm_key)
        if value is not None and value != "":
            trip_payload[db_key] = value

    success, result_msg = await create_trip(trip_payload)
    await state.clear()

    is_admin = is_admin_user(user_id)

    if success:
        await callback.answer("✅ Поїздку успішно створено!", show_alert=True)
        if callback.message:
            await callback.message.answer(
                f"🎉 Поїздку <b>{html.escape(data.get('name', ''))}</b> успішно створено!\n"
                f"🆔 ID: <code>#{html.escape(result_msg)}</code>",
                parse_mode="HTML",
                reply_markup=get_main_keyboard(is_admin=is_admin)
            )
    else:
        await callback.answer("❌ Помилка при створенні поїздки.", show_alert=True)
        if callback.message:
            await callback.message.answer(
                "❌ Не вдалося створити поїздку. Перевірте налаштування бази даних.\n"
                f"Деталі: <code>{html.escape(result_msg[:200])}</code>",
                parse_mode="HTML",
                reply_markup=get_main_keyboard(is_admin=is_admin)
            )

@router.callback_query(F.data == "create_trip_cancel", CreateTripStates.confirm)
async def cancel_trip_creation_inline(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin = is_admin_user(callback.from_user.id) if callback.from_user else False
    await callback.answer("🚫 Створення скасовано.")
    if callback.message:
        await callback.message.answer(
            "🚫 Створення поїздки скасовано.",
            reply_markup=get_main_keyboard(is_admin=is_admin)
        )
