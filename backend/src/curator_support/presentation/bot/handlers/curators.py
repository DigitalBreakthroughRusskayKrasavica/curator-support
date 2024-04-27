from aiogram import Router, types, Bot, F

from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from curator_support.presentation.bot.filters import CuratorFilter
from curator_support.presentation.bot.states import NewPairForm
from curator_support.services import HelperService

router = Router()

CANCEL_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='stop_appending')]]
)


@router.message(CuratorFilter(), Command('new_pair'))
async def add_new_pair(msg: types.Message, state: FSMContext):
    await state.set_state(NewPairForm.question)
    await msg.answer('Введите новый вопрос', reply_markup=CANCEL_KEYBOARD)


@router.message(StateFilter(NewPairForm.question))
async def get_question(msg: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(question=msg.text)
    await state.set_state(NewPairForm.category)

    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    await msg.answer('Введите категорию этого вопроса', reply_markup=CANCEL_KEYBOARD)


@router.message(StateFilter(NewPairForm.category))
async def get_question_category(msg: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(category=msg.text)
    await state.set_state(NewPairForm.answer)

    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    await msg.answer('Введите ответ для этого вопроса', reply_markup=CANCEL_KEYBOARD)


@router.message(StateFilter(NewPairForm.answer))
async def get_answer(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    data = await state.get_data()
    question, category, answer = data['question'], data['category'], msg.text

    await service.add_new_pair(question, category, answer)

    await state.clear()

    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    await msg.answer(
        text='Добавлена новая пара вопрос-ответ:\n\n'
             f"'{question}' : '{answer}'"
    )


@router.callback_query(StateFilter(NewPairForm), F.data == 'stop_appending')
async def cancel_appending(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Вы отменили процесс добавления пары')
