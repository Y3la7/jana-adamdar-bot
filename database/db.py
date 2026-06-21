"""
database/db.py — инициализация и управление подключением к SQLite через aiosqlite.
"""

import os
from contextlib import asynccontextmanager
import aiosqlite
from config import DATABASE_PATH


@asynccontextmanager
async def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        yield conn


async def init_db() -> None:
    async with get_connection() as db:
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
                status      TEXT NOT NULL DEFAULT 'active',
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        try:
            await db.execute("ALTER TABLE events ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
            await db.commit()
        except Exception:
            pass

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

        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id    INTEGER UNIQUE NOT NULL,
                title      TEXT,
                thread_id  INTEGER DEFAULT NULL,
                added_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Добавляем thread_id если таблица уже существует без него
        try:
            await db.execute("ALTER TABLE groups ADD COLUMN thread_id INTEGER DEFAULT NULL")
            await db.commit()
        except Exception:
            pass

        await db.commit()

    print("✅ База данных инициализирована")
