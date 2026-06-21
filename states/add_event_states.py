from aiogram.fsm.state import State, StatesGroup


class AddEvent(StatesGroup):
    title = State()
    description = State()
    date = State()
    time = State()
    location = State()
    seats = State()
    photo = State()
