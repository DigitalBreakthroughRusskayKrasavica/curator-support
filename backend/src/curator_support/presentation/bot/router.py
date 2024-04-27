import asyncio

from aiogram import Router, Bot
from aiogram.filters import CommandStart

from aiogram import types

from curator_support import exceptions
from curator_support.services import HelperService

from curator_support.presentation.bot.filters import CuratorFilter


router = Router(name=__name__)

@router.message()
async def get_question(msg: types.Message, bot: Bot, service: HelperService):
    question = msg.text
    
    loop = asyncio.get_event_loop()
    try:
        ans = await loop.run_in_executor(None, service.get_answer, question)
        await msg.answer(f"Ответ: {ans}")
    except exceptions.InvalidQuestion as e:
        pass
    except exceptions.QuestionNeedsСlarification as e:
        pass
    