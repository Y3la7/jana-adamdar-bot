"""
handlers/help.py — обработчик раздела «Помощь».
Контакты берутся из config.py, изменяй там.
"""

from aiogram import Router, F
from aiogram.types import Message

from config import CONTACTS
from texts.messages import HELP_TEXT

router = Router(name="help")


@router.message(F.text == "📞 Помощь")
async def help_section(message: Message) -> None:
    """Отображает контактную информацию движения."""
    text = HELP_TEXT.format(
        phone=CONTACTS["phone"],
        telegram=CONTACTS["telegram"],
        instagram=CONTACTS["instagram"],
        email=CONTACTS["email"],
    )
    await message.answer(text=text, parse_mode="HTML")
