from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import exceptions
from bot import reply_keyboards
from bot.handlers.utils import process_error
from bot.messages import bot_responses
from bot.reply_keyboards import reply_keyboard_texts
from excel.async_search import search_by_inn, search_by_passport, search_by_snils, search_by_name


class Searching(StatesGroup):
    end = State()
    message_ids = State()


async def process_type(message: types.Message, state: FSMContext):
    bot_message = await message.answer(text=bot_responses['searching']['end'], reply_markup=reply_keyboards.cancel)
    await state.update_data(type=message.text)

    await state.update_data(message_ids=[message.message_id, bot_message.message_id])
    await Searching.end.set()


async def process_document(message: types.Message, state: FSMContext):
    document = message.document
    if document is None:
        await message.answer(bot_responses['searching']['end'], reply_markup=reply_keyboards.cancel)
        return
    file_name = document.file_name
    path = f'./excel/documents/{document.file_unique_id}.xlsx'
    await document.download(path)
    await message.answer(bot_responses['searching']['wait'], reply_markup=types.ReplyKeyboardRemove())
    data = await state.get_data()
    if data.get('type') == reply_keyboard_texts['menu']['name']:
        try:
            document = await search_by_name(path)
        except exceptions.NotCorrectColumnType as err:
            await process_error(err, message, state)
            return
    elif data.get('type') == reply_keyboard_texts['menu']['passport']:
        document = await search_by_passport(path)
    elif data.get('type') == reply_keyboard_texts['menu']['inn']:
        document = await search_by_inn(path)
    elif data.get('type') == reply_keyboard_texts['menu']['snils']:
        try:
            document = await search_by_snils(path)
        except exceptions.NotExistColumn as err:
            await process_error(err, message, state)
            return
    else:
        await process_error('Неизвестный тип данных', message, state)
        return

    doc = types.InputFile(document, filename='new' + file_name)
    await message.answer_document(doc, reply_markup=reply_keyboards.menu)
    # data = await state.get_data()
    # await delete_messages(message.chat.id, data['message_ids'] + [message.message_id])
    await state.finish()


async def process_cancel(message: types.Message, state: FSMContext):
    await message.answer('Ок', reply_markup=reply_keyboards.menu)
    # data = await state.get_data()
    # await delete_messages(message.chat.id, data['message_ids'] + [message.message_id])
    await state.finish()


def register_handlers_searching(dp: Dispatcher):
    dp.register_message_handler(process_type, lambda msg: msg.text in reply_keyboard_texts['menu'].values())
    dp.register_message_handler(process_cancel,
                                Text(equals=reply_keyboard_texts['cancel'][0], ignore_case=True),
                                state=Searching.end)
    dp.register_message_handler(process_document, content_types=['document'], state=Searching.end)
