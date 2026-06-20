# 🤖 Бот «Жаңа адамдар»

Telegram-бот для молодёжного движения «Жаңа адамдар», написанный на Python + aiogram 3.x.

## Структура проекта

```
telegram-bot/
│
├── bot.py                  ← точка входа, запуск бота
├── config.py               ← конфигурация (токен, контакты, пути)
│
├── handlers/               ← обработчики сообщений и callback-ов
│   ├── main_menu.py        ← /start и главное меню
│   ├── who_we_are.py       ← раздел «Кто мы?»
│   ├── join.py             ← анкета «Присоединиться» (FSM)
│   ├── events.py           ← мероприятия и регистрация
│   └── help.py             ← контакты
│
├── keyboards/              ← клавиатуры (Reply и Inline)
│   ├── main_kb.py
│   ├── who_we_are_kb.py
│   ├── events_kb.py
│   ├── join_kb.py
│   └── back_kb.py
│
├── states/
│   └── join_states.py      ← FSM-состояния анкеты
│
├── database/
│   ├── db.py               ← инициализация SQLite
│   └── queries.py          ← все запросы к БД
│
├── utils/
│   └── notify_admin.py     ← уведомления администратору
│
├── texts/
│   └── messages.py         ← ВСЕ тексты бота (меняй только здесь)
│
├── images/                 ← папка для фото (jpg, png, webp)
│
├── requirements.txt
├── .env.example
└── README.md
```

## Быстрый старт

### 1. Установи зависимости

```bash
cd telegram-bot
pip install -r requirements.txt
```

### 2. Создай файл `.env`

```bash
cp .env.example .env
```

Открой `.env` и заполни:

```
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_Telegram_ID
DATABASE_PATH=database/bot.db
```

> **Где взять BOT_TOKEN** — создай бота через [@BotFather](https://t.me/BotFather) командой `/newbot`.  
> **Где взять ADMIN_ID** — напиши [@userinfobot](https://t.me/userinfobot), он покажет твой ID.

### 3. Запусти бота

```bash
python bot.py
```

---

## Частые задачи

### Изменить текст

Открой `texts/messages.py` — все тексты хранятся там.

### Изменить контакты

Открой `config.py`, найди словарь `CONTACTS` и обнови значения.

### Добавить фото в раздел «Кто мы?»

Положи любой `.jpg`, `.png` или `.webp` файл в папку `images/` — бот подхватит его автоматически.

### Добавить мероприятие в БД

```python
from database.queries import add_event
import asyncio

asyncio.run(add_event(
    title="Форум молодёжи 2025",
    description="Ежегодный форум для лидеров движения.",
    date="2025-09-15",
    time="10:00",
    location="Алматы, ул. Абая 5",
    photo=None,         # или имя файла из папки images/, например "forum.jpg"
    seats=100,
))
```

### Добавить новую кнопку в главное меню

1. Открой `keyboards/main_kb.py` — добавь `KeyboardButton`.
2. Создай новый роутер в `handlers/`.
3. Зарегистрируй роутер в `bot.py`.

---

## Что можно добавить в будущем

- 🔐 **Авторизация** — через Telegram Login Widget или FSM-пароль
- 👮 **Система ролей** — администратор, модератор, участник
- 📊 **Статистика** — число участников, активность, популярные разделы
- 🗄 **PostgreSQL** — замени `aiosqlite` на `asyncpg` + `SQLAlchemy`
- 🔴 **Redis** — замени `MemoryStorage` на `RedisStorage` для FSM
- 📣 **Рассылки** — массовые уведомления участникам
- 🛠 **Админ-панель** — управление мероприятиями прямо из бота
- 🌐 **Мультиязычность** — казахский, русский, английский
- 📈 **Веб-дашборд** — статистика через отдельный сайт
