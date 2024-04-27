from typing import List

from aiogram.types import BotCommand

COMMON_COMMANDS = [
    BotCommand(command="start", description="Перезапустить бота"),
    BotCommand(command="help", description="Посмотреть справку о боте"),
]


def get_curator_commands() -> List[BotCommand]:
    return [
        *COMMON_COMMANDS,
        BotCommand(command="new_pair", description="Добавить пару вопрос-ответ"),
    ]
