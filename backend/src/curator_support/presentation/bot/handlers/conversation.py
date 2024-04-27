import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from curator_support.presentation.bot.states import Conversation
from curator_support.presentation.bot.filters import CuratorFilter


logger = logging.getLogger(__name__)

router = Router()

CANCEL_KEYWORDS = "Отменить диалог"
CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=CANCEL_KEYWORDS)]], resize_keyboard=True
)


@router.callback_query(F.data.startswith("start_conversation"))
async def start_conversation(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    if not callback.data:
        logger.info("No callback data")
        return

    student_id = int(callback.data.split("-")[1])

    await state.set_state(Conversation.active)
    await state.storage.set_state(
        key=StorageKey(bot_id=bot.id, chat_id=student_id, user_id=student_id),
        state=Conversation.active,
    )
    await state.update_data(student_id=student_id, first_message=True)

    if not callback.message:
        logger.info("No message")
        return

    await bot.edit_message_reply_markup(
        chat_id=ADMIN_ID, message_id=callback.message.message_id, reply_markup=None
    )

    if not isinstance(callback.message, types.Message):
        logger.info("Message has incorrect type")
        return

    await callback.message.answer(
        f"Диалог со студентом {student_id} начат", reply_markup=CANCEL_KEYBOARD
    )


@router.message(StateFilter(Conversation.active), CuratorFilter())
async def handle_admin_chat(
    message: types.Message, state: FSMContext, bot: Bot
) -> None:
    data = await state.get_data()
    student_id = data["student_id"]

    if data["first_message"]:
        await state.update_data(first_message=False)
        await bot.send_message(
            chat_id=student_id, text="Администратор начал с вами диалог"
        )

    if message.text == CANCEL_KEYWORDS:
        await state.clear()
        await message.answer(
            "Диалог завершен", reply_markup=types.ReplyKeyboardRemove()
        )
        await bot.send_message(
            chat_id=student_id,
            text="Админ завершил диалог",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    await bot.copy_message(
        from_chat_id=message.chat.id,
        chat_id=student_id,
        message_id=message.message_id,
        reply_markup=CANCEL_KEYBOARD,
    )
    return


@router.message(StateFilter(Conversation.active))
async def handle_student_chat(
    message: types.Message, state: FSMContext, bot: Bot
) -> None:
    student_id = message.chat.id

    if message.text == CANCEL_KEYWORDS:
        await state.clear()
        await message.answer(
            "Диалог завершен", reply_markup=types.ReplyKeyboardRemove()
        )
        await bot.send_message(
            chat_id=student_id,
            text=f"Пользователь {student_id} завершил диалог",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    await bot.copy_message(
        from_chat_id=message.chat.id,
        chat_id=ADMIN_ID,
        message_id=message.message_id,
        reply_markup=CANCEL_KEYBOARD,
    )