from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from bot import reply_keyboards
from bot.handlers.finite_state_machine.searching import register_handlers_searching
from bot.messages import bot_responses
from bot.reply_keyboards import reply_keyboard_texts
from excel.async_himera import get_limit


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_start, commands=['start'], state='*')
    dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')
    dp.register_message_handler(feedback_message, commands=['feedback'], state='*')
    dp.register_message_handler(about_message, commands=['about'], state='*')
    dp.register_message_handler(send_limit,
                                Text(equals=reply_keyboard_texts['menu']['check limit'], ignore_case=True),
                                state='*')
    register_handlers_searching(dp)
    dp.register_message_handler(help_message)


async def send_start(message: types.Message):
    await message.answer(text=bot_responses['start'], reply_markup=reply_keyboards.menu)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(bot_responses['cancel handler']['no state'], reply_markup=reply_keyboards.menu)
    else:
        await state.finish()
        await message.answer(bot_responses['cancel handler']['state was cleared'], reply_markup=reply_keyboards.menu)


async def feedback_message(message: types.Message):
    await message.answer(bot_responses['feedback'])


async def about_message(message: types.Message):
    await message.answer(bot_responses['about'], reply_markup=reply_keyboards.menu)


async def send_limit(message: types.Message):
    await message.answer(text=bot_responses['check limit'].format(limit=get_limit()['limit']),
                         reply_markup=reply_keyboards.menu)


async def help_message(message: types.Message):
    await message.answer(text=bot_responses['help'], reply_markup=reply_keyboards.menu)
