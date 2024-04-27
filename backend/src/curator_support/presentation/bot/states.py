from aiogram.fsm.state import State, StatesGroup


class Conversation(StatesGroup):
    active = State()
    