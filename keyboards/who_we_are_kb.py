"""
keyboards/who_we_are_kb.py — подменю раздела «Кто мы?».
Добавляй новые подразделы сюда.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def who_we_are_keyboard() -> InlineKeyboardMarkup:
    """Inline-клавиатура подразделов раздела «Кто мы?»."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 О нас", callback_data="wwa:about")],
            [InlineKeyboardButton(text="🎯 Наша миссия", callback_data="wwa:mission")],
            [InlineKeyboardButton(text="⚡ Чем мы занимаемся", callback_data="wwa:what_we_do")],
            [InlineKeyboardButton(text="❓ FAQ", callback_data="wwa:faq")],
            [InlineKeyboardButton(text="🌐 Наши социальные сети", callback_data="wwa:social")],
            [InlineKeyboardButton(text="📸 Фото и видео", callback_data="wwa:photos")],
        ]
    )
