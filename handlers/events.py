"""
handlers/events.py — обработчики раздела «Календарь мероприятий».
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
import os

from keyboards.events_kb import events_list_keyboard, event_detail_keyboard
from keyboards.back_kb import inline_back_keyboard
from database.queries import (
    get_upcoming_events,
    get_event_by_id,
    register_for_event,
    is_registered_for_event,
)
from utils.notify_admin import notify_admin
from texts.messages import (
    EVENTS_TITLE,
    EVENTS_EMPTY,
    EVENT_CARD,
    EVENT_NO_SEATS,
    EVENT_REGISTERED,
    EVENT_ALREADY_REGISTERED,
    EVENT_ADMIN_NOTIFY,
)

router = Router(name="events")

# Путь к папке с изображениями мероприятий
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")


@router.message(F.text == "📅 Календарь мероприятий")
async def events_list(message: Message) -> None:
    """Отображает список предстоящих мероприятий."""
    events = await get_upcoming_events()

    if not events:
        await message.answer(text=EVENTS_EMPTY, parse_mode="HTML")
        return

    await message.answer(
        text=EVENTS_TITLE,
        reply_markup=events_list_keyboard(events),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "events:list")
async def events_list_callback(callback: CallbackQuery) -> None:
    """Возврат к списку мероприятий из карточки."""
    events = await get_upcoming_events()

    if not events:
        await callback.message.edit_text(text=EVENTS_EMPTY, parse_mode="HTML")
        await callback.answer()
        return

    await callback.message.edit_text(
        text=EVENTS_TITLE,
        reply_markup=events_list_keyboard(events),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("event:"))
async def event_detail(callback: CallbackQuery) -> None:
    """Показывает детальную карточку одного мероприятия."""
    event_id = int(callback.data.split(":")[1])
    event = await get_event_by_id(event_id)

    if not event:
        await callback.answer("Мероприятие не найдено.", show_alert=True)
        return

    # Формируем текст карточки
    free_seats = event["free_seats"] if event["seats"] > 0 else "Неограниченно"
    card_text = EVENT_CARD.format(
        title=event["title"],
        description=event["description"],
        date=event["date"],
        time=event["time"],
        location=event["location"],
        seats=free_seats,
    )

    # Если у мероприятия есть фото — отправляем его
    if event["photo"] and os.path.exists(os.path.join(IMAGES_DIR, event["photo"])):
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=FSInputFile(os.path.join(IMAGES_DIR, event["photo"])),
            caption=card_text,
            reply_markup=event_detail_keyboard(event_id),
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            text=card_text,
            reply_markup=event_detail_keyboard(event_id),
            parse_mode="HTML",
        )

    await callback.answer()


@router.callback_query(F.data.startswith("register:"))
async def register_for_event_handler(callback: CallbackQuery, bot: Bot) -> None:
    """Регистрирует пользователя на мероприятие."""
    event_id = int(callback.data.split(":")[1])
    user = callback.from_user

    # Проверяем, не зарегистрирован ли уже
    if await is_registered_for_event(event_id, user.id):
        await callback.answer(EVENT_ALREADY_REGISTERED, show_alert=True)
        return

    # Пробуем зарегистрировать
    success = await register_for_event(event_id, user.id)

    if not success:
        await callback.answer(EVENT_NO_SEATS, show_alert=True)
        return

    # Получаем данные мероприятия для уведомления
    event = await get_event_by_id(event_id)
    event_title = event["title"] if event else f"ID {event_id}"

    # Уведомляем администратора
    admin_text = EVENT_ADMIN_NOTIFY.format(
        event_title=event_title,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        user_id=user.id,
        username=user.username or "нет",
    )
    await notify_admin(bot, admin_text)

    # Подтверждаем пользователю
    await callback.answer(
        text=EVENT_REGISTERED.format(title=event_title),
        show_alert=True,
    )
