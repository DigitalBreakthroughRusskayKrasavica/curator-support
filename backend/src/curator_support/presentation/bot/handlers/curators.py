from aiogram import types, Router

from curator_support.presentation.bot.filters import CuratorFilter


router = Router()

@router.message(CuratorFilter())
async def get_msg_from_c(msg: types.Message):
    print("msg from curator")
