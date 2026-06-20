"""
keyboards/join_kb.py — клавиатуры для анкеты «Присоединиться».
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка отмены при заполнении анкеты."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить анкету")]],
        resize_keyboard=True,
    )
