"""
keyboards/events_kb.py — клавиатуры для раздела «Мероприятия».
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def events_list_keyboard(events: list) -> InlineKeyboardMarkup:
    """
    Генерирует список кнопок для каждого мероприятия.
    events — список объектов из БД с полями id и title.
    """
    buttons = [
        [InlineKeyboardButton(text=f"📌 {event['title']}", callback_data=f"event:{event['id']}")]
        for event in events
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def event_detail_keyboard(event_id: int) -> InlineKeyboardMarkup:
    """Кнопки на карточке мероприятия: «Записаться» и «Назад»."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Записаться", callback_data=f"register:{event_id}")],
            [InlineKeyboardButton(text="⬅️ К списку", callback_data="events:list")],
        ]
    )
