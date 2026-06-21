"""
bot.py — точка входа в бота «Жаңа адамдар».
Регистрирует все роутеры и запускает polling.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db

# ─── Импорт всех роутеров ─────────────────────────────────────────────────────
from handlers import main_menu, who_we_are, join, events, help as help_handler, admin, broadcast

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Главная асинхронная функция запуска бота."""

    # Инициализируем базу данных (создаём таблицы если нет)
    await init_db()

    # Создаём экземпляр бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Создаём диспетчер с хранилищем состояний в памяти
    # Для продакшена замени MemoryStorage на RedisStorage
    dp = Dispatcher(storage=MemoryStorage())

    # ─── Подключаем роутеры ───────────────────────────────────────────────────
    # Порядок важен: join должен идти ДО main_menu,
    # чтобы FSM-обработчики перехватывали сообщения раньше общих фильтров.
    dp.include_router(admin.router)
    dp.include_router(broadcast.router)
    dp.include_router(join.router)
    dp.include_router(who_we_are.router)
    dp.include_router(events.router)
    dp.include_router(help_handler.router)
    dp.include_router(main_menu.router)  # Всегда последним — содержит catch-all

    logger.info("🚀 Бот «Жаңа адамдар» запускается...")

    # Удаляем вебхуки (на случай если они были) и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
