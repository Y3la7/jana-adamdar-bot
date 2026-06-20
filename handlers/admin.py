"""
handlers/admin.py — команды администратора.
Доступны только пользователю с ADMIN_ID из config.py.
"""

import os
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID, DATABASE_PATH
from database.queries import get_all_members, get_upcoming_events, get_event_registrations_count

router = Router(name="admin")

# Путь к папке с изображениями
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")


def is_admin(message: Message) -> bool:
    """Проверяет, является ли отправитель администратором."""
    return message.from_user.id == ADMIN_ID


# ─── Установка фото «Кто мы?» ────────────────────────────────────────────────

@router.message(F.photo & F.caption.startswith("/setwwa"))
async def set_who_we_are_photo(message: Message, bot: Bot) -> None:
    """
    Сохраняет фото для раздела «Кто мы?».
    Использование: отправь фото с подписью /setwwa
    """
    if not is_admin(message):
        return

    # Берём фото в наибольшем качестве
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    save_path = os.path.join(IMAGES_DIR, "who_we_are.jpg")

    # Удаляем старое фото если есть
    for ext in ("jpg", "jpeg", "png", "webp"):
        old = os.path.join(IMAGES_DIR, f"who_we_are.{ext}")
        if os.path.exists(old):
            os.remove(old)

    await bot.download_file(file.file_path, destination=save_path)

    await message.answer("✅ Фото для раздела «Кто мы?» обновлено!")


# ─── Установка фото галереи ───────────────────────────────────────────────────

@router.message(F.photo & F.caption.startswith("/addphoto"))
async def add_gallery_photo(message: Message, bot: Bot) -> None:
    """
    Добавляет фото в галерею «Фото и видео».
    Использование: отправь фото с подписью /addphoto
    """
    if not is_admin(message):
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Генерируем уникальное имя файла
    existing = [f for f in os.listdir(IMAGES_DIR) if f.startswith("gallery_")]
    index = len(existing) + 1
    save_path = os.path.join(IMAGES_DIR, f"gallery_{index:03d}.jpg")

    await bot.download_file(file.file_path, destination=save_path)

    await message.answer(f"✅ Фото добавлено в галерею (всего фото: {index})")


# ─── Статистика ───────────────────────────────────────────────────────────────

@router.message(Command("stats"))
async def admin_stats(message: Message) -> None:
    """
    Показывает статистику бота (только для администратора).
    Использование: /stats
    """
    if not is_admin(message):
        return

    members = await get_all_members()
    events = await get_upcoming_events()

    text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего заявок: <b>{len(members)}</b>\n"
        f"📅 Активных мероприятий: <b>{len(events)}</b>\n"
    )

    await message.answer(text=text, parse_mode="HTML")


# ─── Список команд администратора ─────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_help(message: Message) -> None:
    """Показывает список доступных команд администратора."""
    if not is_admin(message):
        return

    text = (
        "🛠 <b>Команды администратора</b>\n\n"
        "📸 <b>Фото «Кто мы?»</b>\n"
        "Отправь фото с подписью <code>/setwwa</code>\n\n"
        "🖼 <b>Добавить в галерею</b>\n"
        "Отправь фото с подписью <code>/addphoto</code>\n\n"
        "📊 <b>Статистика</b>\n"
        "/stats — число заявок и мероприятий\n"
    )

    await message.answer(text=text, parse_mode="HTML")
