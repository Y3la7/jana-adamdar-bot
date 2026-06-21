"""
database/queries.py — все запросы к базе данных.
Бизнес-логика хранится здесь, обработчики только вызывают эти функции.
"""

from typing import Optional
import aiosqlite
from database.db import get_connection


# ═══════════════════════════════════════════════════════════════════════════════
#  УЧАСТНИКИ
# ═══════════════════════════════════════════════════════════════════════════════

async def is_member_exists(user_id: int) -> bool:
    """Проверяет, подавал ли пользователь заявку ранее."""
    async with get_connection() as db:
        async with db.execute(
            "SELECT 1 FROM members WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone() is not None


async def add_member(
    user_id: int,
    first_name: str,
    last_name: str,
    age: int,
    city: str,
    phone: str,
    telegram: str,
) -> None:
    """Сохраняет нового участника в базу данных."""
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO members (user_id, first_name, last_name, age, city, phone, telegram)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, first_name, last_name, age, city, phone, telegram),
        )
        await db.commit()


async def get_all_members() -> list:
    """Возвращает список всех участников (для будущей админ-панели)."""
    async with get_connection() as db:
        async with db.execute(
            "SELECT * FROM members ORDER BY joined_at DESC"
        ) as cursor:
            return await cursor.fetchall()


# ═══════════════════════════════════════════════════════════════════════════════
#  МЕРОПРИЯТИЯ
# ═══════════════════════════════════════════════════════════════════════════════

async def get_upcoming_events() -> list:
    """
    Возвращает предстоящие мероприятия вместе с количеством свободных мест.
    """
    async with get_connection() as db:
        async with db.execute(
            """
            SELECT
                e.*,
                (e.seats - COUNT(r.id)) AS free_seats
            FROM events e
            LEFT JOIN event_registrations r ON r.event_id = e.id
            GROUP BY e.id
            HAVING free_seats > 0 OR e.seats = 0
            ORDER BY e.date ASC, e.time ASC
            """
        ) as cursor:
            return await cursor.fetchall()


async def get_event_by_id(event_id: int) -> Optional[aiosqlite.Row]:
    """Возвращает одно мероприятие по ID с подсчётом свободных мест."""
    async with get_connection() as db:
        async with db.execute(
            """
            SELECT
                e.*,
                (e.seats - COUNT(r.id)) AS free_seats
            FROM events e
            LEFT JOIN event_registrations r ON r.event_id = e.id
            WHERE e.id = ?
            GROUP BY e.id
            """,
            (event_id,),
        ) as cursor:
            return await cursor.fetchone()


async def add_event(
    title: str,
    description: str,
    date: str,
    time: str,
    location: str,
    photo: Optional[str],
    seats: int,
) -> int:
    """Добавляет новое мероприятие. Возвращает ID созданного мероприятия."""
    async with get_connection() as db:
        async with db.execute(
            """
            INSERT INTO events (title, description, date, time, location, photo, seats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, description, date, time, location, photo, seats),
        ) as cursor:
            event_id = cursor.lastrowid
        await db.commit()
    return event_id


# ═══════════════════════════════════════════════════════════════════════════════
#  РЕГИСТРАЦИИ НА МЕРОПРИЯТИЯ
# ═══════════════════════════════════════════════════════════════════════════════

async def is_registered_for_event(event_id: int, user_id: int) -> bool:
    """Проверяет, зарегистрирован ли пользователь на мероприятие."""
    async with get_connection() as db:
        async with db.execute(
            "SELECT 1 FROM event_registrations WHERE event_id = ? AND user_id = ?",
            (event_id, user_id),
        ) as cursor:
            return await cursor.fetchone() is not None


async def register_for_event(event_id: int, user_id: int) -> bool:
    """
    Регистрирует пользователя на мероприятие.
    Возвращает True при успехе, False если мест нет или уже зарегистрирован.
    """
    event = await get_event_by_id(event_id)
    if not event:
        return False

    # Проверяем наличие свободных мест
    if event["seats"] > 0 and event["free_seats"] <= 0:
        return False

    async with get_connection() as db:
        try:
            await db.execute(
                "INSERT INTO event_registrations (event_id, user_id) VALUES (?, ?)",
                (event_id, user_id),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            # Уникальное ограничение — уже зарегистрирован
            return False


async def get_event_registrations_count(event_id: int) -> int:
    """Возвращает количество зарегистрированных на мероприятие."""
    async with get_connection() as db:
        async with db.execute(
            "SELECT COUNT(*) FROM event_registrations WHERE event_id = ?",
            (event_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ГРУППЫ
# ═══════════════════════════════════════════════════════════════════════════════

async def save_group(chat_id: int, title: str) -> None:
    """Сохраняет группу в БД (или обновляет название если уже есть)."""
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO groups (chat_id, title) VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET title = excluded.title
            """,
            (chat_id, title),
        )
        await db.commit()


async def remove_group(chat_id: int) -> None:
    """Удаляет группу из БД (бота кикнули)."""
    async with get_connection() as db:
        await db.execute("DELETE FROM groups WHERE chat_id = ?", (chat_id,))
        await db.commit()


async def get_all_groups() -> list:
    """Возвращает все сохранённые группы."""
    async with get_connection() as db:
        async with db.execute("SELECT chat_id, title, thread_id FROM groups ORDER BY added_at DESC") as cursor:
            return await cursor.fetchall()


async def update_group_thread(chat_id: int, thread_id: int) -> None:
    """Сохраняет ID топика для группы."""
    async with get_connection() as db:
        await db.execute(
            "UPDATE groups SET thread_id = ? WHERE chat_id = ?",
            (thread_id, chat_id),
        )
        await db.commit()
