"""
utils/notify_admin.py — отправка уведомлений администратору.
"""

from aiogram import Bot
from config import ADMIN_ID


async def notify_admin(bot: Bot, text: str) -> None:
    """
    Отправляет текстовое сообщение администратору бота.
    Если доставка не удалась — ошибка логируется, но не прерывает работу бота.
    """
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")
    except Exception as exc:
        print(f"⚠️ Не удалось отправить сообщение администратору: {exc}")
