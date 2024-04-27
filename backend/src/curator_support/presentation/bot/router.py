import asyncio

from aiogram import Router, Bot
from aiogram.filters import CommandStart

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from curator_support import exceptions
from curator_support.services import HelperService

from curator_support.presentation.bot.filters import CuratorFilter


router = Router(name=__name__)

@router.message()
async def get_question(msg: types.Message, bot: Bot, service: HelperService):
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
    