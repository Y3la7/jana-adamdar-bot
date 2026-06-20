"""
states/join_states.py — состояния FSM для анкеты вступления.
Добавляй новые состояния сюда при расширении формы.
"""

from aiogram.fsm.state import State, StatesGroup


class JoinForm(StatesGroup):
    """Шаги заполнения анкеты вступления в движение."""
    first_name = State()   # Имя
    last_name = State()    # Фамилия
    age = State()          # Возраст
    city = State()         # Город
    phone = State()        # Телефон
    telegram = State()     # Telegram username
