"""
database/db.py — инициализация и управление подключением к SQLite через aiosqlite.
"""

import os
from contextlib import asynccontextmanager
import aiosqlite
from config import DATABASE_PATH


@asynccontextmanager
async def get_connection():
    """
    Асинхронный контекстный менеджер для работы с БД.
    Использование:
        async with get_connection() as db:
            ...
    """
    # Создаём директорию, если её нет
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")  # Улучшает конкурентный доступ
        yield conn


async def init_db() -> None:
    """
    Создаёт все таблицы при первом запуске бота.
    Безопасно вызывать при каждом старте — таблицы не пересоздаются.
    """
    async with get_connection() as db:
        # Таблица участников движения
        await db.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER UNIQUE NOT NULL,
                first_name  TEXT NOT NULL,
                last_name   TEXT NOT NULL,
                age         INTEGER NOT NULL,
                city        TEXT NOT NULL,
                phone       TEXT NOT NULL,
                telegram    TEXT,
                joined_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица мероприятий
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT NOT NULL,
                date        TEXT NOT NULL,
                time        TEXT NOT NULL,
                location    TEXT NOT NULL,
                photo       TEXT,
                seats       INTEGER NOT NULL DEFAULT 0,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица регистраций на мероприятия
        await db.execute("""
            CREATE TABLE IF NOT EXISTS event_registrations (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id     INTEGER NOT NULL,
                user_id      INTEGER NOT NULL,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_id, user_id),
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        """)

        await db.commit()

    print("✅ База данных инициализирована")
