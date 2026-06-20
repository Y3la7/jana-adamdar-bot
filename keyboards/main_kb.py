"""
keyboards/main_kb.py — главное меню бота.
Чтобы добавить кнопку — добавь её здесь.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает клавиатуру главного меню с четырьмя кнопками."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👥 Кто мы?"),
                KeyboardButton(text="🚀 Присоединиться"),
            ],
            [
                KeyboardButton(text="📅 Календарь мероприятий"),
                KeyboardButton(text="📞 Помощь"),
            ],
        ],
        resize_keyboard=True,
        persistent=True,
    )
