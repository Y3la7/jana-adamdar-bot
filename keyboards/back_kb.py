"""
keyboards/back_kb.py — универсальная кнопка «Назад» и «В главное меню».
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from texts.messages import BACK_TO_MENU, BACK_BUTTON


def back_to_menu_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка возврата в главное меню (Reply-клавиатура)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BACK_TO_MENU)]],
        resize_keyboard=True,
    )


def inline_back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Inline-кнопка «Назад» с заданным callback_data."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BACK_BUTTON, callback_data=callback_data)]
        ]
    )
