from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import reply_keyboards
from bot.bot import bot
from bot.messages import bot_responses


async def delete_messages(chat_id: int, message_ids: List[int]):
    for message_id in message_ids:
        await bot.delete_message(chat_id, message_id)


async def process_error(error, message: types.Message, state: FSMContext = None):
    await message.answer(text=bot_responses['error'].format(error=error),
                         reply_markup=reply_keyboards.menu,
                         parse_mode='Markdown')
    if state is not None:
        await state.finish()
