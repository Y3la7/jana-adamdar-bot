"""
handlers/admin.py — команды администратора.
Доступны только пользователю с ADMIN_ID из config.py.
"""

import os
import re
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from config import ADMIN_ID, DATABASE_PATH
from database.queries import get_all_members, get_upcoming_events, get_event_registrations_count, add_event, get_all_groups, remove_group
from states.add_event_states import AddEvent

router = Router(name="admin")

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")

SKIP_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭ Пропустить")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

CANCEL_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


# ─── Установка фото «Кто мы?» ────────────────────────────────────────────────

@router.message(F.photo & F.caption.startswith("/setwwa"))
async def set_who_we_are_photo(message: Message, bot: Bot) -> None:
    if not is_admin(message):
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    save_path = os.path.join(IMAGES_DIR, "who_we_are.jpg")

    for ext in ("jpg", "jpeg", "png", "webp"):
        old = os.path.join(IMAGES_DIR, f"who_we_are.{ext}")
        if os.path.exists(old):
            os.remove(old)

    await bot.download_file(file.file_path, destination=save_path)
    await message.answer("✅ Фото для раздела «Кто мы?» обновлено!")


# ─── Установка фото галереи ───────────────────────────────────────────────────

@router.message(F.photo & F.caption.startswith("/addphoto"))
async def add_gallery_photo(message: Message, bot: Bot) -> None:
    if not is_admin(message):
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    os.makedirs(IMAGES_DIR, exist_ok=True)

    existing = [f for f in os.listdir(IMAGES_DIR) if f.startswith("gallery_")]
    index = len(existing) + 1
    save_path = os.path.join(IMAGES_DIR, f"gallery_{index:03d}.jpg")

    await bot.download_file(file.file_path, destination=save_path)
    await message.answer(f"✅ Фото добавлено в галерею (всего фото: {index})")


# ─── Статистика ───────────────────────────────────────────────────────────────

@router.message(Command("stats"))
async def admin_stats(message: Message) -> None:
    if not is_admin(message):
        return

    members = await get_all_members()
    events = await get_upcoming_events()

    text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего заявок: <b>{len(members)}</b>\n"
        f"📅 Активных мероприятий: <b>{len(events)}</b>\n"
    )

    await message.answer(text=text, parse_mode="HTML")


# ─── Добавить мероприятие (/addevent) — FSM ──────────────────────────────────

@router.message(Command("addevent"))
async def addevent_start(message: Message, state: FSMContext) -> None:
    if not is_admin(message):
        return

    await state.set_state(AddEvent.title)
    await message.answer(
        "📅 <b>Добавление мероприятия</b>\n\n"
        "Шаг 1/7 — Введи <b>название</b> мероприятия:",
        reply_markup=CANCEL_KB,
        parse_mode="HTML",
    )


@router.message(AddEvent.title)
async def addevent_title(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено.", reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(AddEvent.description)
    await message.answer(
        "Шаг 2/7 — Введи <b>описание</b> мероприятия:",
        reply_markup=CANCEL_KB,
        parse_mode="HTML",
    )


@router.message(AddEvent.description)
async def addevent_description(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено.", reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(description=message.text.strip())
    await state.set_state(AddEvent.date)
    await message.answer(
        "Шаг 3/7 — Введи <b>дату</b> в формате ДД.ММ.ГГГГ\n"
        "Например: <code>25.07.2025</code>",
        reply_markup=CANCEL_KB,
        parse_mode="HTML",
    )


@router.message(AddEvent.date)
async def addevent_date(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено.", reply_markup=ReplyKeyboardRemove())
        return

    date = message.text.strip()
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date):
        await message.answer("⚠️ Неверный формат. Введи дату в формате ДД.ММ.ГГГГ:")
        return

    await state.update_data(date=date)
    await state.set_state(AddEvent.time)
    await message.answer(
        "Шаг 4/7 — Введи <b>время</b> в формате ЧЧ:ММ\n"
        "Например: <code>18:00</code>",
        reply_markup=CANCEL_KB,
        parse_mode="HTML",
    )


@router.message(AddEvent.time)
async def addevent_time(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено.", reply_markup=ReplyKeyboardRemove())
        return

    time = message.text.strip()
    if not re.match(r"^\d{2}:\d{2}$", time):
        await message.answer("⚠️ Неверный формат. Введи время в формате ЧЧ:ММ:")
        return

    await state.update_data(time=time)
    await state.set_state(AddEvent.location)
    await message.answer(
        "Шаг 5/7 — Введи <b>место проведения</b>:",
        reply_markup=CANCEL_KB,
        parse_mode="HTML",
    )


@router.message(AddEvent.location)
async def addevent_location(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено.", reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(location=message.text.strip())
    await state.set_state(AddEvent.seats)
    await message.answer(
        "Шаг 6/7 — Введи <b>количество мест</b>:\n"
        "Напиши <code>0</code> если мест неограниченно.",
        reply_markup=CANCEL_KB,
        parse_mode="HTML",
    )


@router.message(AddEvent.seats)
async def addevent_seats(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено.", reply_markup=ReplyKeyboardRemove())
        return

    if not message.text.strip().isdigit():
        await message.answer("⚠️ Введи число (например 50 или 0 для неограниченного):")
        return

    await state.update_data(seats=int(message.text.strip()))
    await state.set_state(AddEvent.photo)

    skip_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏭ Пропустить"), KeyboardButton(text="❌ Отменить")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "Шаг 7/7 — Отправь <b>фото</b> мероприятия или нажми «Пропустить»:",
        reply_markup=skip_kb,
        parse_mode="HTML",
    )


@router.message(AddEvent.photo)
async def addevent_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Добавление отменено.", reply_markup=ReplyKeyboardRemove())
        return

    data = await state.get_data()
    photo_filename = None

    if message.photo:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        os.makedirs(IMAGES_DIR, exist_ok=True)

        existing = [f for f in os.listdir(IMAGES_DIR) if f.startswith("event_")]
        index = len(existing) + 1
        photo_filename = f"event_{index:03d}.jpg"
        save_path = os.path.join(IMAGES_DIR, photo_filename)
        await bot.download_file(file.file_path, destination=save_path)

    event_id = await add_event(
        title=data["title"],
        description=data["description"],
        date=data["date"],
        time=data["time"],
        location=data["location"],
        photo=photo_filename,
        seats=data["seats"],
    )

    await state.clear()

    seats_text = "Неограниченно" if data["seats"] == 0 else str(data["seats"])
    await message.answer(
        f"✅ <b>Мероприятие добавлено!</b> (ID: {event_id})\n\n"
        f"📌 <b>{data['title']}</b>\n"
        f"📅 {data['date']} в {data['time']}\n"
        f"📍 {data['location']}\n"
        f"👥 Мест: {seats_text}\n"
        f"🖼 Фото: {'да' if photo_filename else 'нет'}",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )

    # ─── Рассылаем анонс мероприятия во все группы ───────────────────────────
    groups = await get_all_groups()
    if groups:
        announce_text = (
            f"📣 <b>Новое мероприятие!</b>\n\n"
            f"📌 <b>{data['title']}</b>\n\n"
            f"📝 {data['description']}\n\n"
            f"📅 Дата: <b>{data['date']}</b>\n"
            f"🕐 Время: <b>{data['time']}</b>\n"
            f"📍 Место: <b>{data['location']}</b>\n"
            f"👥 Мест: <b>{seats_text}</b>"
        )

        sent = 0
        for group in groups:
            try:
                if photo_filename:
                    photo_path = os.path.join(IMAGES_DIR, photo_filename)
                    from aiogram.types import FSInputFile
                    await bot.send_photo(
                        chat_id=group["chat_id"],
                        photo=FSInputFile(photo_path),
                        caption=announce_text,
                        parse_mode="HTML",
                    )
                else:
                    await bot.send_message(
                        chat_id=group["chat_id"],
                        text=announce_text,
                        parse_mode="HTML",
                    )
                sent += 1
            except Exception:
                await remove_group(group["chat_id"])

        if sent:
            await message.answer(f"📨 Анонс разослан в <b>{sent}</b> групп(ы).", parse_mode="HTML")


# ─── Список команд администратора ─────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_help(message: Message) -> None:
    if not is_admin(message):
        return

    text = (
        "🛠 <b>Команды администратора</b>\n\n"
        "📸 <b>Фото «Кто мы?»</b>\n"
        "Отправь фото с подписью <code>/setwwa</code>\n\n"
        "🖼 <b>Добавить в галерею</b>\n"
        "Отправь фото с подписью <code>/addphoto</code>\n\n"
        "📅 <b>Добавить мероприятие</b>\n"
        "<code>/addevent</code> — пошаговая форма\n\n"
        "📊 <b>Статистика</b>\n"
        "<code>/stats</code> — число заявок и мероприятий\n"
    )

    await message.answer(text=text, parse_mode="HTML")
