import asyncio
import aiohttp
# import aiofiles
import os

from aiogram import types

from bot import reply_keyboards
from bot.bot import bot
from bot.handlers import utils
from bot.messages import bot_responses
from excel.async_search import search_by_name
from config import HIMERA_TOKEN_BOT


def test_queue(chat_id, text):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(asyncio.sleep(40))
    loop.run_until_complete(bot.send_message(chat_id, text))
    loop.close()


def process_document(bot_message, bot_message_, file_id):
    print('-'*30)
    print(bot_message)
    print('-'*30)
    loop = asyncio.new_event_loop()
    document = loop.run_until_complete(work_with_excel(bot_message, file_id))
    loop.run_until_complete(end_process(bot_message, bot_message_, file_id, document))


async def end_process(bot_message, bot_message_, file_name, document):
    await bot.delete_message(bot_message_['chat']['id'], bot_message_['message_id'])
    await bot.delete_message(bot_message['chat']['id'], bot_message['message_id'])
    new_file_name = utils.make_new_file_name(file_name)
    print(document, new_file_name)
    doc = types.InputFile(document, filename=new_file_name)
    await bot.send_document(bot_message['chat']['id'], doc, reply_markup=reply_keyboards.menu)
    for file in f'./excel/documents/{file_name}', f'./excel/documents/{new_file_name}':
        if os.path.exists(file):
            os.remove(file)


async def work_with_excel(bot_message, file_id):
    file = await bot.get_file(file_id)
    file_name = file.file_unique_id + '.xlsx'
    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/file/bot{HIMERA_TOKEN_BOT}/{file.file_path}'
        print(url)
        async with session.get(url) as response:
            print('='*40)
            print(response)
            print(os.listdir('./excel'))
            if not os.path.exists('./excel/documents'):
                print('making')
                os.mkdir('./excel/documents')
            print(os.path.exists('./excel/documents'))
            print(os.listdir('./excel'))
            with open(f'./excel/documents/{file_name}', 'wb') as f:
                f.write(await response.read())
    print(file)
    print(file.file_path)
    salt = 1
    text = bot_message['text']
    async for statistics in search_by_name(utils.get_path_to_excel_docs(file_name)):
        if statistics[0] == 'statistics':
            new_text = bot_responses['searching']['statistics'].format(
                number=statistics[1], all_number=statistics[2]
            )
            new_text += '.'*salt
            if text == new_text:
                salt = (salt + 1) % 3
                new_text += '.'
            await bot.edit_message_text(new_text, bot_message['chat']['id'], bot_message['message_id'])
            text = new_text
        else:
            document = statistics[1]
            return document
