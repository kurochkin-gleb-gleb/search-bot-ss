from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from rq import Queue

from bot import exceptions
from bot import reply_keyboards
from bot.handlers import utils
from bot.handlers.utils import process_error
from bot.messages import bot_responses
from bot.reply_keyboards import reply_keyboard_texts
from excel import process_excel_with_worker
from worker import conn


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
    file_name = document.file_unique_id + '.xlsx'
    print(file_name)
    path = utils.get_path_to_excel_docs(file_name)
    await document.download(path)
    bot_message_ = await message.answer(bot_responses['searching']['wait'], reply_markup=types.ReplyKeyboardRemove())
    bot_message = await message.answer(bot_responses['searching']['statistics'].format(
        number=0, all_number='...'
    ))
    data = await state.get_data()
    if data.get('type') == reply_keyboard_texts['menu']['name']:
        try:
            queue = Queue(connection=conn)
            queue.enqueue(process_excel_with_worker.process_document, bot_message.to_python(),
                          bot_message_.to_python(), file_name)
            await state.finish()
        except exceptions.NotCorrectColumnType as err:
            await process_error(err, message, state)
            return
    else:
        await process_error('Неизвестный тип данных', message, state)
        return


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
