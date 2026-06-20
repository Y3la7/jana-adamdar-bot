"""
handlers/join.py — обработчики анкеты «Присоединиться» (FSM).
Каждый шаг — отдельная функция. Добавляй новые поля аналогично.
"""

import re
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.join_states import JoinForm
from keyboards.main_kb import main_menu_keyboard
from keyboards.join_kb import cancel_keyboard
from database.queries import add_member, is_member_exists
from utils.notify_admin import notify_admin
from texts.messages import (
    JOIN_START,
    JOIN_ASK_LAST_NAME,
    JOIN_ASK_AGE,
    JOIN_ASK_CITY,
    JOIN_ASK_PHONE,
    JOIN_ASK_TELEGRAM,
    JOIN_SUCCESS,
    JOIN_ALREADY_REGISTERED,
    JOIN_ADMIN_NOTIFY,
    JOIN_INVALID_AGE,
    JOIN_INVALID_PHONE,
    JOIN_CANCELLED,
)

router = Router(name="join")

# Регулярное выражение для проверки телефонного номера
PHONE_REGEX = re.compile(r"^\+?[7|8][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$")


@router.message(F.text == "🚀 Присоединиться")
async def join_start(message: Message, state: FSMContext) -> None:
    """Запускает анкету или сообщает, что пользователь уже подавал заявку."""
    # Проверяем, подавал ли пользователь заявку ранее
    if await is_member_exists(message.from_user.id):
        await message.answer(
            text=JOIN_ALREADY_REGISTERED,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    # Начинаем FSM и просим ввести имя
    await state.set_state(JoinForm.first_name)
    await message.answer(
        text=JOIN_START,
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == "❌ Отменить анкету")
async def cancel_join(message: Message, state: FSMContext) -> None:
    """Отмена заполнения анкеты на любом шаге."""
    await state.clear()
    await message.answer(
        text=JOIN_CANCELLED,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(JoinForm.first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    """Шаг 1: сохраняем имя, переходим к фамилии."""
    await state.update_data(first_name=message.text.strip())
    await state.set_state(JoinForm.last_name)
    await message.answer(text=JOIN_ASK_LAST_NAME, parse_mode="HTML")


@router.message(JoinForm.last_name)
async def process_last_name(message: Message, state: FSMContext) -> None:
    """Шаг 2: сохраняем фамилию, переходим к возрасту."""
    await state.update_data(last_name=message.text.strip())
    await state.set_state(JoinForm.age)
    await message.answer(text=JOIN_ASK_AGE, parse_mode="HTML")


@router.message(JoinForm.age)
async def process_age(message: Message, state: FSMContext) -> None:
    """Шаг 3: проверяем и сохраняем возраст, переходим к городу."""
    text = message.text.strip()

    # Валидация возраста
    if not text.isdigit() or not (10 <= int(text) <= 100):
        await message.answer(text=JOIN_INVALID_AGE, parse_mode="HTML")
        return

    await state.update_data(age=int(text))
    await state.set_state(JoinForm.city)
    await message.answer(text=JOIN_ASK_CITY, parse_mode="HTML")


@router.message(JoinForm.city)
async def process_city(message: Message, state: FSMContext) -> None:
    """Шаг 4: сохраняем город, переходим к телефону."""
    await state.update_data(city=message.text.strip())
    await state.set_state(JoinForm.phone)
    await message.answer(text=JOIN_ASK_PHONE, parse_mode="HTML")


@router.message(JoinForm.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    """Шаг 5: проверяем и сохраняем телефон, переходим к Telegram."""
    phone = message.text.strip()

    # Удаляем пробелы и дефисы для проверки
    normalized = re.sub(r"[\s\-\(\)]", "", phone)
    if not PHONE_REGEX.match(normalized.replace(normalized[0], normalized[0], 1)):
        # Упрощённая проверка: минимум 10 цифр
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 10:
            await message.answer(text=JOIN_INVALID_PHONE, parse_mode="HTML")
            return

    await state.update_data(phone=phone)
    await state.set_state(JoinForm.telegram)
    await message.answer(text=JOIN_ASK_TELEGRAM, parse_mode="HTML")


@router.message(JoinForm.telegram)
async def process_telegram(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Шаг 6 (последний): сохраняем Telegram, записываем в БД,
    уведомляем администратора и завершаем FSM.
    """
    telegram_username = message.text.strip()

    # Нормализуем: убираем @ если пользователь его добавил, и добавляем обратно
    if telegram_username.lower() == "нет":
        telegram_username = "—"
    elif not telegram_username.startswith("@"):
        telegram_username = f"@{telegram_username}"

    # Собираем все данные из состояния
    data = await state.get_data()
    data["telegram"] = telegram_username
    data["user_id"] = message.from_user.id

    # Сохраняем в базу данных
    await add_member(
        user_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        age=data["age"],
        city=data["city"],
        phone=data["phone"],
        telegram=telegram_username,
    )

    # Уведомляем администратора
    admin_text = JOIN_ADMIN_NOTIFY.format(
        first_name=data["first_name"],
        last_name=data["last_name"],
        age=data["age"],
        city=data["city"],
        phone=data["phone"],
        telegram=telegram_username,
        user_id=message.from_user.id,
    )
    await notify_admin(bot, admin_text)

    # Завершаем FSM и благодарим пользователя
    await state.clear()
    await message.answer(
        text=JOIN_SUCCESS.format(first_name=data["first_name"]),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
