"""
handlers/main_menu.py — обработчики главного меню и команды /start.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_kb import main_menu_keyboard
from texts.messages import WELCOME, BACK_TO_MENU

router = Router(name="main_menu")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Приветствие при первом запуске или команде /start."""
    await message.answer(
        text=WELCOME,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(lambda m: m.text == BACK_TO_MENU)
async def back_to_menu(message: Message) -> None:
    """Возврат в главное меню из любого раздела."""
    await message.answer(
        text=WELCOME,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
