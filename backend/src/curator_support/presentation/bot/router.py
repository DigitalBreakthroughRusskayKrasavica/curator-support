import asyncio

from aiogram import Router, Bot
from aiogram.filters import CommandStart

from aiogram import types
from aiogram.filters import StateFilter, Command

from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommandScopeChat

from curator_support import exceptions
from curator_support.services import HelperService
from curator_support.models import Role

from curator_support.presentation.bot.commands import get_curator_commands, COMMON_COMMANDS

from curator_support.presentation.bot.filters import CuratorFilter

router = Router(name=__name__)


@router.message(Command('become_curator'))
async def become_curator(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.CURATOR)

    await bot.set_my_commands(get_curator_commands(), BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь куратор")


@router.message(Command('become_student'))
async def become_student(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.STUDENT)
    
    await bot.set_my_commands(COMMON_COMMANDS, BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь студент")
    


@router.message(~CuratorFilter())
async def get_question(msg: types.Message, state: FSMContext, service: HelperService):
    question = msg.text

    try:
        ans = await service.get_answer(question)
        await msg.answer(
            text=f"Ответ: {ans}.\n\nОтвет не устроил?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Связаться с куратором",
                            callback_data=f'start_conversation-{msg.chat.id}'
                        )
                    ]
                ]
            )
        )
    except exceptions.InvalidQuestion as e:
        pass
    except exceptions.QuestionNeedsСlarification as e:
        pass

